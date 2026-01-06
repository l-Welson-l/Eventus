from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', UserRegisterView.as_view(), name="register-user"),
    path('login/', UserLoginView.as_view(), name="login-user"),
    path('logout/', UserLogoutView.as_view(), name="logout-user"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token-refresh"),

    path("auth/magic-link/", request_magic_link),
    path("auth/magic-complete/", complete_magic_signup),

    path("me/", current_user),


    path("events/create/", CreateEventView.as_view(), name="create-event"),
    path("events/<uuid:event_id>/join/", join_event, name="join-event"),
    path("events/<uuid:event_id>/", event_detail, name="event-detail"),
    path(
        "events/<uuid:event_id>/toggle-feature/",
        toggle_event_feature,
        name="toggle-event-feature",
    ),
    path("events/<uuid:event_id>/update/", update_event),
    path("my-events/", my_events),
    path("media/event_menus/<str:filename>/view/", ServeMenuPDF.as_view()),



    path(
        "events/<uuid:event_id>/posts/",
        EventPostListCreateView.as_view(),
        name="event-posts"
    ),
    path(
        "posts/<uuid:post_id>/comments/create/",
        CommentCreateView.as_view(),
        name="post-comments"
    ),
    path(
        "posts/<uuid:post_id>/comments/",
        CommentListView.as_view(),
        name="comment-list",
    ),

    path(
        "events/<uuid:event_id>/subtopics/",
        SubTopicListView.as_view(),
        name="event-subtopics",
    ),
    path(
        "events/<uuid:event_id>/subtopics/create/",
        SubTopicCreateView.as_view(),
        name="subtopic-create",
    ),


    path("posts/<uuid:post_id>/like/", toggle_post_like),
    path("comments/<uuid:comment_id>/like/", toggle_comment_like),

    path("events/<uuid:event_id>/moments/", EventMomentsListView.as_view(), name="event-moments-list"),
    
     path("moments/create/", CreateMomentView.as_view(), name="create-moment"),
     path("moments/<uuid:moment_id>/like/", ToggleMomentLikeView.as_view())




]
