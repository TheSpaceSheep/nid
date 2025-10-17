import json
from pathlib import Path
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from pywebpush import webpush, WebPushException
from py_vapid import Vapid01
from accounts.decorators import login_required


def service_worker(request):
    """Serve the service worker from root path with correct MIME type"""
    sw_path = Path(settings.BASE_DIR) / "static" / "service-worker.js"
    with open(sw_path, 'r') as f:
        content = f.read()
    response = HttpResponse(content, content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    return response


@login_required
@require_http_methods(["POST"])
def send_notification(request):
    """Send a web push notification"""
    subscription_json = request.POST.get("subscription", "").strip()
    message_text = request.POST.get("message", "").strip()

    if not subscription_json or not message_text:
        return HttpResponse(
            "<p class='text-red-600 font-semibold'>Error: Both subscription and message are required</p>"
        )

    try:
        subscription_info = json.loads(subscription_json)

        payload = json.dumps({
            "title": "New Notification",
            "body": message_text,
            "icon": "/static/icon.png",
        })

        # Replace literal \n with actual newlines and strip any quotes
        private_key_pem = settings.VAPID_PRIVATE_KEY.strip('\'"').replace('\\n', '\n')

        # Create Vapid object from PEM
        vapid = Vapid01.from_pem(private_key_pem.encode())

        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=vapid,
            vapid_claims={
                "sub": f"mailto:{settings.VAPID_ADMIN_EMAIL}"
            }
        )

        return HttpResponse(
            "<p class='text-green-600 font-semibold'>✓ Notification sent successfully!</p>"
        )

    except WebPushException as e:
        return HttpResponse(
            f"<p class='text-red-600 font-semibold'>Error: {str(e)}</p>"
        )
    except Exception as e:
        return HttpResponse(
            f"<p class='text-red-600 font-semibold'>Error: {str(e)}</p>"
        )


@csrf_exempt
@require_http_methods(["POST"])
def save_subscription(request):
    """Save a push subscription (in a real app, store this in the database)"""
    try:
        subscription_data = json.loads(request.body)
        return JsonResponse({"success": True, "subscription": subscription_data})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
