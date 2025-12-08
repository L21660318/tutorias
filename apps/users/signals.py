# apps/users/signals.py
from django.dispatch import receiver
from allauth.account.signals import user_signed_up


@receiver(user_signed_up)
def set_role_tutee_for_matehuala(sender, request, user, **kwargs):
    email = (user.email or "").lower()
    if email.endswith("@matehuala.tecnm.mx"):
        user.role = "TUTEE"
        user.save()
