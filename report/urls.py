from django.urls import path
from report import views

urlpatterns = [
    path(
        "users/",
        views.UserReportView.as_view(),
        name="users",
    ),
    path(
        "pdf-file/",
        views.PDFFileDownloadView.as_view(),
        name="pdf",
    ),
    path(
        "post-download/",
        views.PostDownloadView.as_view(),
        name="post-download",
    ),
]
