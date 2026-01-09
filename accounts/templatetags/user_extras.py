from django import template

register = template.Library()

@register.filter
def has_patient_profile(user):
    return hasattr(user, "patient_profile")
