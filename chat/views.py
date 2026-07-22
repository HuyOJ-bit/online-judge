import re

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from judge.models import Contest

from .models import ChatMessage

ROOM_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{0,78}$")


def _valid_room(room):
    if not ROOM_RE.match(room):
        return False
    if room == "global":
        return True
    if room.startswith("contest-"):
        return Contest.objects.filter(slug=room[len("contest-"):]).exists()
    return False


@login_required
def room_global(request):
    return render(request, "chat/room.html", {
        "room": "global",
        "room_title": "Global chat",
        "back_url": None,
    })


@login_required
def room_contest(request, slug):
    contest = get_object_or_404(Contest, slug=slug)
    return render(request, "chat/room.html", {
        "room": f"contest-{contest.slug}",
        "room_title": f"Contest chat — {contest.title}",
        "back_url": contest.get_absolute_url(),
    })


@login_required
@require_GET
def api_messages(request, room):
    if not _valid_room(room):
        return HttpResponseBadRequest("bad room")
    try:
        after = int(request.GET.get("after", 0))
    except ValueError:
        after = 0
    qs = ChatMessage.objects.filter(room=room).select_related("user")
    if after:
        qs = qs.filter(id__gt=after)
        msgs = list(qs[:100])
    else:
        msgs = list(qs.order_by("-id")[:50])[::-1]
    return JsonResponse({
        "messages": [
            {
                "id": m.id,
                "user": m.user.username,
                "content": m.content,
                "time": timezone.localtime(m.created_at).strftime("%H:%M"),
                "mine": m.user_id == request.user.id,
            }
            for m in msgs
        ]
    })


@login_required
@require_POST
def api_send(request, room):
    if not _valid_room(room):
        return HttpResponseBadRequest("bad room")
    content = (request.POST.get("content") or "").strip()
    if not content:
        return HttpResponseBadRequest("empty")
    if len(content) > 500:
        content = content[:500]

    # Light flood protection: max 1 message per 2 seconds per user.
    last = (ChatMessage.objects.filter(user=request.user)
            .order_by("-created_at").first())
    if last and (timezone.now() - last.created_at).total_seconds() < 2:
        return JsonResponse({"ok": False, "error": "Slow down a little…"},
                            status=429)

    msg = ChatMessage.objects.create(user=request.user, room=room, content=content)
    return JsonResponse({"ok": True, "id": msg.id})
