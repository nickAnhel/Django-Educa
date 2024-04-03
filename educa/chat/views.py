from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from courses.models import Course


@login_required
def course_chat_room(request: HttpRequest, course_id: int) -> HttpResponse | HttpResponseForbidden:
    try:
        course: Course = request.user.courses_joined.get(id=course_id)
    except Course.DoesNotExist:
        return HttpResponseForbidden()

    return render(request, "chat/room.html", {"course": course})
