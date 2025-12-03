# apps/tutoring/services.py
from django.db import transaction
from .models import Session, TutorGroup


@transaction.atomic
def generate_plan_sessions_for_group(group, activities):
    """
    Genera/actualiza las 12 sesiones PLAN para un grupo de tutoría.

    activities: lista de dicts:
      {
        "number": 1..12,
        "title": "...",
        "description": "...",
        "date": datetime | None,
        "file": UploadedFile | None
      }
    """
    tutor = group.tutor
    period = group.period

    for act in activities:
        number = act["number"]
        title = act.get("title", "")
        description = act.get("description", "")
        date = act.get("date")
        file = act.get("file")

        session, created = Session.objects.get_or_create(
            group=group,
            tutor=tutor,
            period=period,
            kind=Session.Kind.PLAN,
            activity_number=number,
            defaults={
                "activity_title": title,
                "activity_description": description,
                "scheduled_date": date or period.start_date,  # o alguna fecha base
                "status": Session.Status.SCHEDULED,
            },
        )

        session.activity_title = title
        session.activity_description = description
        if date is not None:
            session.scheduled_date = date
        if file is not None:
            session.activity_material = file
        session.save()
