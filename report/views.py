import csv

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views.generic import View

User = get_user_model()

COLUMNS = ["first_name", "last_name", "username", "email"]


class UserReportView(View):
    def get(self, request):

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=users.csv"

        users = User.objects.all().only(*COLUMNS).values(*COLUMNS)

        writer = csv.DictWriter(response, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)

        return response
