from django import template
from django.contrib.auth.models import Group 
from datetime import datetime, timedelta
import re

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name): 
    group = Group.objects.get(name=group_name) 
    return True if group in user.groups.all() else False
    
@register.filter
def duration_days(td):
    if td:
        try: 
            return 'Day %s' % str(int(td)+1)
        except:
            return 'Day %s' % str(int(td.days)+1)
    return "Day 1"

@register.filter
def duration_progress(td, extension=0):
    if td:
        length = 84 + extension
        if float(td) > length:
            return 100
        else:
            return round((float(td)+1)/length*100)
    return "1"
    
@register.filter
def max_time(td):
    return datetime.now()+timedelta(hours=12)

@register.filter
def elapsed(td, extended=0):
    difference = datetime.now().date()-(td+timedelta(days=extended))
    return difference.days

@register.filter
def parse_url(url):
    pattern = "(.*uc\?id=.*)\&export=()"
    try:
        parsed = re.match(pattern, url).groups()[0]
    except:
        parsed = None
    
    return parsed
    

    
