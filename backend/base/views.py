from rest_framework import generics, status
import uuid, secrets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from .models import MagicLinkToken, User, BusinessProfile, CustomerProfile, AnonymousSession, Post
from django.contrib.auth.hashers import make_password
from .utils import generate_qr_base64
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from django.utils import timezone

MAGIC_LINK_EXPIRY_DAYS = 10

class UserRegisterView(GenericAPIView):
    permission_classes = (AllowAny, )
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {
            "refresh":str(token),
            "access": str(token.access_token)
        }
        return Response(data, status=status.HTTP_201_CREATED)

class UserLoginView(GenericAPIView):
    permission_classes = (AllowAny, )
    serializer_class = LoginSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        serializer = UserSerializer(user)
        token = RefreshToken.for_user(user)
        data = dict(serializer.data)
        data["tokens"] = {
            "refresh":str(token),
            "access": str(token.access_token)
        }
        return Response(data, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([AllowAny])
def start_anonymous_session(request):
    email = request.data.get("email")

    if not email:
        return Response({"detail": "Email required"}, status=400)

    anon = AnonymousSession.objects.create(
        email=email,
        display_name=f"anonymous_{secrets.randbelow(100000)}"
    )

    # Send magic link
    token = secrets.token_urlsafe(48)
    expires_at = timezone.now() + timedelta(days=10)

    MagicLinkToken.objects.create(
        token=token,
        email=email,
        expires_at=expires_at,
        # optional link to anon
        anonymous_session=anon
    )

    link = f"{settings.FRONTEND_BASE_URL}/magic-login?token={token}"
    send_mail(
        "Finish creating your account",
        f"Click here to continue: {link}",
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )

    return Response({
        "anonymous_session_id": anon.session_id,
        "display_name": anon.display_name
    })



    # Create anonymous session ONLY if needed
    if anon_id:
        anon_session = AnonymousSession.objects.filter(
            session_id=anon_id
        ).first()

    if not anon_session:
        anon_session = AnonymousSession.objects.create(
            email=email,
            display_name=f"anonymous_{secrets.randbelow(100000)}"
        )
    else:
        anon_session.email = email
        anon_session.save(update_fields=["email"])

    token = secrets.token_urlsafe(48)
    expires_at = timezone.now() + timedelta(days=MAGIC_LINK_EXPIRY_DAYS)

    MagicLinkToken.objects.create(
        token=token,
        email=email,
        expires_at=expires_at,
        anonymous_session=anon_session
    )

    link = f"{settings.FRONTEND_BASE_URL}/magic-login?token={token}"

    send_mail(
        subject="Finish creating your account",
        message=(
            f"Click the link below to create your account.\n\n"
            f"{link}\n\n"
            f"This link expires in {MAGIC_LINK_EXPIRY_DAYS} days."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    return Response({
        "detail": "Magic link sent",
        "anonymous_session_id": anon_session.session_id,
        "display_name": anon_session.display_name,
    })

    

@api_view(["POST"])
@permission_classes([AllowAny])
def request_magic_link(request):
    """
    Creates an anonymous session (if not already created),
    stores email, sends magic link.
    """
    email = request.data.get("email")

    if not email:
        return Response({"detail": "Email required"}, status=400)

    # 🚫 Prevent magic link / anon session for existing users
    if User.objects.filter(email=email).exists():
        return Response({"detail": "An account with this email already exists."}, status=400)

    if MagicLinkToken.objects.filter(email=email).exists():
        return Response({"detail": "A magic link has already been sent to this email, please login using the link in the email"}, status=400)

    anon_session = None
    anon_id = request.data.get("anonymous_session_id")

    # Create anonymous session ONLY if needed
    if anon_id:
        anon_session = AnonymousSession.objects.filter(
            session_id=anon_id
        ).first()

    if not anon_session:
        anon_session = AnonymousSession.objects.create(
            email=email,
            display_name=f"anonymous_{secrets.randbelow(100000)}"
        )
    else:
        anon_session.email = email
        anon_session.save(update_fields=["email"])

    token = secrets.token_urlsafe(48)
    expires_at = timezone.now() + timedelta(days=MAGIC_LINK_EXPIRY_DAYS)

    MagicLinkToken.objects.create(
        token=token,
        email=email,
        expires_at=expires_at,
        anonymous_session=anon_session
    )

    link = f"{settings.FRONTEND_BASE_URL}/magic-login?token={token}"

    send_mail(
        subject="Finish creating your account",
        message=(
            f"Click the link below to create your account.\n\n"
            f"{link}\n\n"
            f"This link expires in {MAGIC_LINK_EXPIRY_DAYS} days."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    return Response({
        "detail": "Magic link sent",
        "anonymous_session_id": anon_session.session_id,
        "display_name": anon_session.display_name,
    })




class CreatePostView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        anon_id = request.data.get("anonymous_session_id")

        if not user and not anon_id:
            return Response(
                {"detail": "Authentication or anonymous session required"},
                status=400
            )

        anonymous_session = None
        if anon_id:
            anonymous_session = get_object_or_404(
                AnonymousSession,
                session_id=anon_id
            )

        post = Post.objects.create(
            event_id=request.data["event_id"],
            text=request.data.get("text", ""),
            user=user,
            anonymous_session=anonymous_session
        )

        return Response(
            {"id": post.id, "detail": "Post created"},
            status=201
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def complete_magic_signup(request):
    """
    User clicks magic link → sets password + optional username
    """
    token = request.data.get("token")
    password = request.data.get("password")
    username = request.data.get("username")  # optional

    if not token or not password:
        return Response({"detail": "Token and password required"}, status=400)

    # 1️⃣ Get magic token
    m = get_object_or_404(MagicLinkToken, token=token)
    if m.used or m.is_expired():
        return Response({"detail": "Token invalid or expired"}, status=400)

    # 2️⃣ Create or update user
    user, created = User.objects.get_or_create(
        email=m.email,
        defaults={
            "username": username or m.email.split("@")[0],
            "user_type": "customer",
            "password": make_password(password)
        }
    )

    if not created:
        # Update password and username if needed
        user.password = make_password(password)
        if username:
            user.username = username
        user.user_type = "customer"
        user.save()

    # 3️⃣ Merge anonymous data
    if m.anonymous_session:
        Post.objects.filter(anonymous_session=m.anonymous_session).update(
            user=user,
            anonymous_session=None
        )

    # 4️⃣ Mark token used
    m.used = True
    m.save()

    # 5️⃣ Generate JWT
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    return Response({
        "access": access_token,
        "refresh": str(refresh),
        "user": UserSerializer(user).data
    })




@api_view(["POST"])
def refresh_token_cookie(request):
    refresh_token = request.COOKIES.get("refresh_token")
    if not refresh_token:
        return Response({"detail":"No refresh token"}, status=401)
    try:
        rt = RefreshToken(refresh_token)
        new_access = str(rt.access_token)
        # Optionally rotate refresh token: create new refresh; send in cookie
        return Response({"access": new_access})
    except Exception:
        return Response({"detail":"Invalid refresh token"}, status=401)


class UserLogoutView(GenericAPIView):
    permission_classes = (IsAuthenticated, )
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)