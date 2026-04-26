from django.urls import path

from apps.documents import views


app_name = "documents"

urlpatterns = [
    path("", views.document_list, name="list"),
    path("templates/", views.template_library, name="templates"),
    path("upload/", views.document_upload, name="upload"),
    path("<str:document_id>/download/", views.document_download, name="download"),
    path("<str:document_id>/delete/", views.document_delete, name="delete"),
]