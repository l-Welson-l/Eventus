from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from .models import Event, PostingSession, Post
from .serializers import EventCreateSerializer, PostSerializer, PostingSessionSerializer
from .utils import generate_qr_base64
from django.utils import timezone

# Owner creates event
class EventCreateView(generics.CreateAPIView):
    serializer_class = EventCreateSerializer
    permission_classes = []  # add owner auth if implemented

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# Guest scans QR → create posting session
@api_view(["POST"])
def create_posting_session(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    device_id = request.data.get("device_id")
    session = PostingSession.create_for_event(event, hours_valid=8, device_id=device_id)
    data = PostingSessionSerializer(session).data
    post_url = f"{request.scheme}://{request.get_host()}/event/{event.id}/post?token={session.token}"
    data["qr_base64"] = generate_qr_base64(post_url)
    return Response(data, status=201)

# Upload photo
@api_view(["POST"])
def upload_post(request, event_id):
    token = request.headers.get("X-POST-TOKEN") or request.data.get("token")
    if not token:
        return Response({"detail": "No posting token provided."}, status=401)
    try:
        session = PostingSession.objects.get(token=token, event_id=event_id)
    except PostingSession.DoesNotExist:
        return Response({"detail": "Invalid token."}, status=401)
    if not session.is_valid():
        return Response({"detail": "Token expired."}, status=401)

    image = request.FILES.get("image")
    caption = request.data.get("caption", "")
    if not image:
        return Response({"detail": "No image provided."}, status=400)

    post = Post.objects.create(event=session.event, session=session, image=image, caption=caption, approved=session.event.auto_approve)
    return Response(PostSerializer(post, context={"request": request}).data, status=201)

# List approved posts
@api_view(["GET"])
def list_posts(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    posts = event.posts.filter(approved=True)
    data = PostSerializer(posts, many=True, context={"request": request}).data
    return Response(data)

# Admin endpoints
@api_view(["GET"])
def admin_list_posts(request, event_id):
    admin_token = request.headers.get("X-ADMIN-TOKEN") or request.query_params.get("admin_token")
    event = get_object_or_404(Event, id=event_id, admin_token=admin_token)
    posts = event.posts.all()
    data = PostSerializer(posts, many=True, context={"request": request}).data
    return Response(data)

@api_view(["DELETE"])
def admin_delete_post(request, post_id):
    admin_token = request.headers.get("X-ADMIN-TOKEN") or request.query_params.get("admin_token")
    post = get_object_or_404(Post, id=post_id)
    if post.event.admin_token != admin_token:
        return Response({"detail": "Forbidden."}, status=403)
    post.image.delete(save=False)
    post.delete()
    return Response(status=204)

@api_view(["POST"])
def admin_download_zip(request, event_id):
    admin_token = request.headers.get("X-ADMIN-TOKEN") or request.data.get("admin_token")
    event = get_object_or_404(Event, id=event_id, admin_token=admin_token)

    posts = event.posts.all()
    bio = BytesIO()
    with ZipFile(bio, mode="w", compression=ZIP_DEFLATED) as z:
        for p in posts:
            if not p.image:
                continue
            fname = f"{p.id}_{p.created_at.strftime('%Y%m%d_%H%M%S')}.jpg"
            content = p.image.read()
            z.writestr(fname, content)
    bio.seek(0)
    response = HttpResponse(bio.read(), content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename=event_{event.id}_photos.zip'
    return response
