from django.urls import path
from .views import *

urlpatterns = [
    path('', DashBoard.as_view()),
    path('github-webhook', github_webhook),
    path('asana-webhook', asana_webhook)
]