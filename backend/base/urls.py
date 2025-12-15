from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name="register-user"),
    path('login/', UserLoginView.as_view(), name="login-user"),
    path('logout/', UserLogoutView.as_view(), name="logout-user"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token-refresh"),

    path("auth/magic-link/", request_magic_link),
    path("auth/magic-verify/", verify_magic_link),

    path("posts/", CreatePostView.as_view(), name="create-post"),
]
