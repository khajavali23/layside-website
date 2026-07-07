from django import template
register = template.Library()

@register.filter
def has_role(user, roles):
    return getattr(user.summary, 'role', None) in roles.split(',')