from os import access
from django import template
from datetime import datetime, date, timedelta
from ..models import Department, Id_table
import pandas as pd
import os.path
from django.db.models import Q

register = template.Library()

@register.simple_tag
def current_time():
    return datetime.now().strftime ("%Y-%m-%d")

@register.simple_tag
def departments():
    return Department.objects.all()

@register.simple_tag
def check_access(user_id, access_id):
    user_access = Id_table.objects.filter(Q(user_id=user_id) & Q(access__id = access_id))
    if user_access:
        return False
    else:
        return True