from rest_framework import generics, status
import uuid, secrets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
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
from django.http import HttpResponse, FileResponse, JsonResponse
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from .models import MagicLinkToken, User, BusinessProfile, CustomerProfile, AnonymousSession, Post, Event, EventFeature, EventMembership, Comment, Moment, MomentMedia, MomentLike, Menu, MenuItem
from django.contrib.auth.hashers import make_password
from .utils import generate_qr_base64
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, EventSerializer, EventFeatureSerializer, CommentSerializer, PostSerializer, MomentSerializer, MenuCategorySerializer, MenuItemSerializer, MenuSerializer
from django.utils import timezone
from django.views import View
import os
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import IntegrityError, transaction


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



class EventJoinMixin:
    """
    Ensures user OR anonymous session
    is a member of the event
    """

    def ensure_membership(self, request, event):
        if request.user.is_authenticated:
            membership, _ = EventMembership.objects.get_or_create(
                event=event,
                user=request.user
            )
            return {"user": request.user}

        anon_id = request.data.get("anonymous_session_id")
        if anon_id:
            anon = get_object_or_404(
                AnonymousSession,
                session_id=anon_id
            )
            membership, _ = EventMembership.objects.get_or_create(
                event=event,
                anonymous_session=anon
            )
            return {"anonymous_session": anon}

        raise PermissionDenied("Login or email required")




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

@api_view(["POST"])
@permission_classes([AllowAny])
def join_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    user = request.user if request.user.is_authenticated else None
    anon_id = request.data.get("anonymous_session_id")

    if not user and not anon_id:
        return Response(
            {"detail": "Anonymous session required"},
            status=400
        )

    anonymous_session = None
    if anon_id:
        anonymous_session = get_object_or_404(
            AnonymousSession,
            session_id=anon_id
        )

    membership, created = EventMembership.objects.get_or_create(
        event=event,
        user=user,
        anonymous_session=anonymous_session
    )

    return Response({
        "joined": True,
        "event_id": str(event.id)
    })

@api_view(["GET"])
@permission_classes([AllowAny])
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    serializer = EventSerializer(event)
    return Response(serializer.data)




class CreateEventView(APIView):
    permission_classes = [IsAuthenticated]



    def post(self, request):
        if request.user.user_type != "business":
            return Response(
                {"detail": "Only business accounts can create events"},
                status=403
            )
        
        business = request.user.business_profile


        event = Event.objects.create(
            business=business,
            name=request.data["name"],
            description=request.data.get("description", "")
        )

        selected_features = request.data.get("features", [])

        for key in selected_features:
            EventFeature.objects.create(event=event, key=key)

        event.generate_qr()

        return Response({
            "id": event.id,
            "qr_code": event.qr_code
        }, status=201)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_event_feature(request, event_id):
    event = get_object_or_404(Event, id=event_id, business=request.user.business_profile)
    key = request.data.get("key")

    feature = EventFeature.objects.filter(event=event, key=key).first()

    if feature:
        feature.delete()
        enabled = False
    else:
        EventFeature.objects.create(event=event, key=key)
        enabled = True

    return Response({"key": key, "enabled": enabled})

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_event(request, event_id):
    """
    Edit event basic details (name, description)
    Only the business owner can update
    """
    if request.user.user_type != "business":
        return Response(
            {"detail": "Only business accounts can edit events"},
            status=403
        )

    event = get_object_or_404(
        Event,
        id=event_id,
        business=request.user.business_profile
    )

    # Update fields safely
    event.name = request.data.get("name", event.name)
    event.description = request.data.get("description", event.description)

    if "menu_file" in request.FILES:
        event.menu_file = request.FILES["menu_file"]
    if "cover_image" in request.FILES:
        event.cover_image = request.FILES["cover_image"]

    event.save()

    serializer = EventSerializer(event)
    return Response(serializer.data, status=200)

class ServeMenuPDF(View):
    def get(self, request, filename):
        filepath = os.path.join(settings.MEDIA_ROOT, "event_menus", filename)
        return FileResponse(open(filepath, "rb"), content_type="application/pdf")

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_events(request):
    if request.user.user_type != "business":
        return Response([], status=200)

    business = request.user.business_profile
    events = Event.objects.filter(business=business)

    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


class EventPostListCreateView(EventJoinMixin, generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(
            event_id=self.kwargs["event_id"]
        ).select_related("user", "anonymous_session") \
         .prefetch_related("comments")

    def perform_create(self, serializer):
        event = get_object_or_404(Event, id=self.kwargs["event_id"])
        author = self.ensure_membership(self.request, event)

        serializer.save(
            event=event,
            **author
        )


class CommentCreateView(EventJoinMixin, generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        author = self.ensure_membership(self.request, post.event)

        serializer.save(
            post=post,
            **author
        )

class EventMomentsListView(generics.ListAPIView):
    serializer_class = MomentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        event_id = self.kwargs["event_id"]
        return Moment.objects.filter(event_id=event_id).prefetch_related("media").select_related("user", "anonymous_session")
   
class CreateMomentView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        event_id = request.data.get("event")
        caption = request.data.get("caption", "")

        event = get_object_or_404(Event, id=event_id)

        # Determine author
        user = request.user if request.user.is_authenticated else None
        anon_session = getattr(request, "anonymous_session", None)

        moment = Moment.objects.create(
            event=event,
            user=user,
            anonymous_session=anon_session,
            caption=caption
        )

        files = request.FILES.getlist("files")
        for index, file in enumerate(files):
            media_type = "video" if file.content_type.startswith("video") else "image"
            MomentMedia.objects.create(
                moment=moment,
                file=file,
                media_type=media_type,
                order=index
            )

        serializer = MomentSerializer(moment, context={"request": request})
        return Response(serializer.data, status=201)


class ToggleMomentLikeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, moment_id):
        moment = get_object_or_404(Moment, id=moment_id)

        # Get user or anonymous session
        user = request.user if request.user.is_authenticated else None
        anon_id = request.data.get("anonymous_session_id")
        anon = None
        if anon_id:
            anon = get_object_or_404(AnonymousSession, session_id=anon_id)

        if not user and not anon:
            return Response({"error": "Must provide user or anonymous_session"}, status=400)

        # Wrap in transaction to avoid race conditions
        try:
            with transaction.atomic():
                like, created = MomentLike.objects.get_or_create(
                    moment=moment,
                    user=user,
                    anonymous_session=anon,
                )

                if not created:
                    like.delete()
                    liked = False
                else:
                    liked = True

                # Return current likes count
                likes_count = MomentLike.objects.filter(moment=moment).count()

                return Response({"liked": liked, "likes_count": likes_count})
        except IntegrityError:
            return Response({"error": "Cannot like this moment"}, status=400)
        

@api_view(["GET"])
def get_menu(request, event_id):
    event = Event.objects.get(id=event_id)

    # Optional safety check
    if not event.features.filter(key="menu").exists():
        return Response({"detail": "Menu disabled"}, status=403)

    menu, _ = Menu.objects.get_or_create(event=event)
    return Response(MenuSerializer(menu).data)

@api_view(["POST"])
def create_category(request):
    serializer = MenuCategorySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=201)

@api_view(["POST"])
def create_item(request):
    serializer = MenuItemSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=201)

@api_view(["PATCH"])
def update_item(request, item_id):
    try:
        item = MenuItem.objects.get(id=item_id)
    except MenuItem.DoesNotExist:
        return Response({"detail": "Item not found"}, status=404)

    serializer = MenuItemSerializer(item, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


