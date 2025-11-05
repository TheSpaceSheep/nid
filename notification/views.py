import json
import csv
from pathlib import Path
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from pywebpush import webpush, WebPushException
from py_vapid import Vapid01
from accounts.decorators import login_required

SUBSCRIPTIONS_CSV = Path(settings.BASE_DIR) / "static" / "data" / "poubelle_subscriptions.csv"


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


@login_required
@require_http_methods(["POST"])
def enable_poubelle_notifications(request):
    """Enable poubelle notifications - save subscription to CSV and set cookie"""
    user_name = request.COOKIES.get('user_name')
    subscription_json = request.POST.get('subscription')

    if not subscription_json:
        return HttpResponse('<div id="poubelle-toggle" class="text-red-600">Erreur: subscription manquante</div>')

    try:
        subscription_data = json.loads(subscription_json)

        # Ensure CSV directory exists
        SUBSCRIPTIONS_CSV.parent.mkdir(parents=True, exist_ok=True)

        # Read existing subscriptions
        existing_subs = []
        if SUBSCRIPTIONS_CSV.exists():
            with open(SUBSCRIPTIONS_CSV, 'r', newline='') as f:
                reader = csv.DictReader(f)
                existing_subs = [row for row in reader if row['user_name'] != user_name]

        # Add new subscription
        existing_subs.append({
            'user_name': user_name,
            'endpoint': subscription_data['endpoint'],
            'p256dh': subscription_data['keys']['p256dh'],
            'auth': subscription_data['keys']['auth']
        })

        # Write back to CSV
        with open(SUBSCRIPTIONS_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['user_name', 'endpoint', 'p256dh', 'auth'])
            writer.writeheader()
            writer.writerows(existing_subs)

        # Update cookie with nested structure
        notifications_enabled_json = request.COOKIES.get('notifications_enabled', '{}')
        notifications_enabled = json.loads(notifications_enabled_json)
        notifications_enabled['poubelle'] = True

        # Return updated button HTML
        response = HttpResponse('''
            <div id="poubelle-toggle" class="flex flex-col items-center gap-4">
                <button
                    hx-post="/notification/disable-poubelle/"
                    hx-target="#poubelle-toggle"
                    hx-swap="outerHTML"
                    class="px-6 py-3 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-lg shadow-md transition-all">
                    je veux plus les notifs pour la poubelle jaune c'était trop chiant
                </button>
                <p class="text-green-600 text-sm">✓ Notifications activées ! (lundi, mercredi, vendredi à 18h)</p>
            </div>
        ''')
        response.set_cookie('notifications_enabled', json.dumps(notifications_enabled), max_age=31536000)
        return response

    except Exception as e:
        return HttpResponse(f'<div id="poubelle-toggle" class="text-red-600">Erreur: {str(e)}</div>')


@login_required
@require_http_methods(["POST"])
def disable_poubelle_notifications(request):
    """Disable poubelle notifications - remove from CSV and unset cookie"""
    user_name = request.COOKIES.get('user_name')

    try:
        # Remove from CSV
        if SUBSCRIPTIONS_CSV.exists():
            with open(SUBSCRIPTIONS_CSV, 'r', newline='') as f:
                reader = csv.DictReader(f)
                remaining_subs = [row for row in reader if row['user_name'] != user_name]

            with open(SUBSCRIPTIONS_CSV, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['user_name', 'endpoint', 'p256dh', 'auth'])
                writer.writeheader()
                writer.writerows(remaining_subs)

        # Update cookie with nested structure
        notifications_enabled_json = request.COOKIES.get('notifications_enabled', '{}')
        notifications_enabled = json.loads(notifications_enabled_json)
        notifications_enabled['poubelle'] = False

        # Return updated button HTML
        response = HttpResponse('''
            <div id="poubelle-toggle" class="flex flex-col items-center gap-4">
                <button
                    onclick="subscribeToPoubelleNotifications()"
                    class="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-lg shadow-md transition-all">
                    stp envoie des notifications pour la poubelle jaune
                </button>
                <p class="text-gray-600 text-sm">Notifications désactivées</p>
            </div>
        ''')
        response.set_cookie('notifications_enabled', json.dumps(notifications_enabled), max_age=31536000)
        return response

    except Exception as e:
        return HttpResponse(f'<div id="poubelle-toggle" class="text-red-600">Erreur: {str(e)}</div>')


@csrf_exempt
@require_http_methods(["POST", "GET"])
def send_poubelle_reminders(request):
    """
    Scheduled endpoint to send poubelle reminders to all subscribed users.
    Should be called at 18:00 on Monday, Wednesday, and Friday.
    Can be triggered by GitHub Actions or external cron service.
    """
    # Optional: Add a secret token for security
    auth_token = request.GET.get('token') or request.POST.get('token')
    expected_token = settings.SECRET_KEY[:32]  # Use part of secret key

    if auth_token != expected_token:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    if not SUBSCRIPTIONS_CSV.exists():
        return JsonResponse({"success": True, "message": "No subscriptions found", "sent": 0})

    try:
        # Read all active subscriptions from CSV
        with open(SUBSCRIPTIONS_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            subscriptions = list(reader)

        if not subscriptions:
            return JsonResponse({"success": True, "message": "No active subscriptions", "sent": 0})

        # Prepare push notification payload
        payload = json.dumps({
            "title": "Poubelle jaune 🗑️",
            "body": "C'est ce soir qu'il faut sortir la poubelle jaune !",
            "icon": "/static/icons/icon-192x192.png",
        })

        # Setup VAPID
        private_key_pem = settings.VAPID_PRIVATE_KEY.strip('\'"').replace('\\n', '\n')
        vapid = Vapid01.from_pem(private_key_pem.encode())

        # Send to all subscribers
        sent_count = 0
        failed = []

        for sub in subscriptions:
            subscription_info = {
                "endpoint": sub['endpoint'],
                "keys": {
                    "p256dh": sub['p256dh'],
                    "auth": sub['auth']
                }
            }

            try:
                webpush(
                    subscription_info=subscription_info,
                    data=payload,
                    vapid_private_key=vapid,
                    vapid_claims={"sub": f"mailto:{settings.VAPID_ADMIN_EMAIL}"}
                )
                sent_count += 1
            except WebPushException as e:
                failed.append({"user": sub['user_name'], "error": str(e)})

        return JsonResponse({
            "success": True,
            "sent": sent_count,
            "failed": len(failed),
            "failures": failed
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
