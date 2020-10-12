from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
import json

# Create your views here.

class Settings(View):
    def get(self, request):
        return HttpResponse('get settings')

    def post(self, request):
        return HttpResponse('post settings')


class DashBoard(View):
    def get(self, request):
        return HttpResponse('Dashboard')


@csrf_exempt
def github_webhook(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    print(body)
    return HttpResponse('pong')


@csrf_exempt
@require_POST
def asana_webhook(request):
    return HttpResponse(200)