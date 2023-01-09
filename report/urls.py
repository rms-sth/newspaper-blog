from django.urls import path
from report import views

urlpatterns = [
    path(
        "users/",
        views.UserReportView.as_view(),
        name="users",
    ),
]
