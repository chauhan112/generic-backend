from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from rest_framework_api_key.models import APIKey
import json
from handlers.controller import ApiController
from handlers.simpleHandler import SimpleHandler
from handlers.githubHandler import MainGitHubHandler

def get_body(request):
    return json.loads(request.body) if request.body else {}

def serialize_qs(qs):
    return list(qs.values())

controller = ApiController()
controller.set_base_path("/api")
controller.add_handler(SimpleHandler())
controller.add_handler(MainGitHubHandler.get_handler())
@csrf_exempt
@require_POST
def all_ops(request):
    api_key = (
        request.headers.get("X-API-Key")
        or request.headers.get("X_API_KEY")
        or request.META.get(settings.API_KEY_CUSTOM_HEADER)
    )
    
    if not api_key or not APIKey.objects.is_valid(api_key):
        return JsonResponse({"detail": "Invalid or missing API key"}, status=401)
    # try:
    #     data = get_body(request)
    #     controller.set_path(request.path)
    #     controller.set_input(data)
    #     return JsonResponse(controller.process(), safe=False)
    # except Exception as e:
    #     return JsonResponse({"detail": str(e)}, status=400)
    
    data = get_body(request)
    controller.set_path(request.path)
    controller.set_input(data)
    return JsonResponse(controller.process(), safe=False)
    
