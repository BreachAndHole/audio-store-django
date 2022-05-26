from django import template
from shop.models import *

register = template.Library()


@register.simple_tag(name='get_title_photo')
def get_title_photo(cable: Cable):
    print(cable)
    return CablePhoto.objects.get(is_title=True, cable=cable)
