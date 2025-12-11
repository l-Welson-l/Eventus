from django.urls import path
from . import views

urlpatterns = [
    path("events/create/", views.EventCreateView.as_view(), name="event-create"),
    path("events/<int:event_id>/session/", views.create_posting_session, name="create-session"),
    path("events/<int:event_id>/post/", views.upload_post, name="upload-post"),
    path("events/<int:event_id>/posts/", views.list_posts, name="list-posts"),

    path("admin/events/<int:event_id>/posts/", views.admin_list_posts, name="admin-list-posts"),
    path("admin/posts/<int:post_id>/", views.admin_delete_post, name="admin-delete-post"),
    path("admin/events/<int:event_id>/download/", views.admin_download_zip, name="admin-download-zip"),
]
