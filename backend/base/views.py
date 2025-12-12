from rest_framework import generics, status
import uuid
from rest_framework.decorators import api_view
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from .models import MagicLinkToken
from .utils import generate_qr_base64
from django.utils import timezone

MAGIC_LINK_EXPIRY_MINUTES = 14400



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


