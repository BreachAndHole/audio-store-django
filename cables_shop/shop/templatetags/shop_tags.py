from django import template
from shop.models import *


register = template.Library()


@register.simple_tag
def get_all_cable_types():
    return CableType.objects.all().order_by('pk')
