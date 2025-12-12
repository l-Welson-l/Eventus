from rest_framework import generics, status
import uuid
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
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
from .models import MagicLinkToken
from .utils import generate_qr_base64
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from django.utils import timezone

MAGIC_LINK_EXPIRY_MINUTES = 14400

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
def request_magic_link(request):
    email = request.data.get("email")
    if not email:
        return Response({"detail":"Email required"}, status=status.HTTP_400_BAD_REQUEST)
    
    token = uuid.uuid4().hex + uuid.uuid4().hex
    expires_at = timezone.now() + timedelta(minutes=MAGIC_LINK_EXPIRY_MINUTES)

   
    m = MagicLinkToken.objects.create(token=token, email=email, expires_at=expires_at)

    # Build link (frontend will call verify)
    link = f"{settings.FRONTEND_BASE_URL}/magic-login?token={token}"

    # send email (use your email provider)
    subject = "Your login link"
    body = f"Click to login: {link}\nThis link expires in {MAGIC_LINK_EXPIRY_MINUTES} minutes."
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)

    # Always return generic success to prevent enumeration
    return Response({"detail":"If the email exists, a magic link has been sent."})



@api_view(["POST"])
def verify_magic_link(request):
    token = request.data.get("token")
    anon_session = request.data.get("anonymous_session_id")  # optional
    if not token:
        return Response({"detail":"token required"}, status=400)
    try:
        m = MagicLinkToken.objects.get(token=token)
    except MagicLinkToken.DoesNotExist:
        return Response({"detail":"Invalid token"}, status=400)
    if m.used or m.is_expired():
        return Response({"detail":"Token invalid or expired"}, status=400)

    # Get or create user
    user, created = User.objects.get_or_create(email=m.email, defaults={"username": m.email.split("@")[0]})

    # Mark token used
    m.used = True
    m.save()

    # create JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    # Merge anonymous data (photos)
    if anon_session:
        from .models import Photo
        Photo.objects.filter(session=anon_session).update(user=user, session=None)

    # Set refresh token in HttpOnly cookie
    response = Response({"access": access_token})
    cookie_max_age = 7 * 24 * 60 * 60  # seconds
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure= not settings.DEBUG,
        samesite="Lax",
        max_age=cookie_max_age,
        path="/api/token/refresh/"
    )
    return response


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