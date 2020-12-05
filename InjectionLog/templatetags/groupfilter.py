from django import template
from django.contrib.auth.models import Group 
from datetime import datetime, timedelta
import re
import pytz

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name): 
    group = Group.objects.get(name=group_name) 
    return True if group in user.groups.all() else False
    
    
@register.filter
def cure_duration(td):
    days = td - 168
    if days < 7:
        return "{:.0f} days".format(days)
    elif days <= 84:
        return "{:.0f} weeks".format(float(days/7))
    elif days <= 365:
        return "{:.1f} months".format(float(days/30))
    else:
       return "{:.1f} years".format(float(days/365)) 
        
    
    
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
            pct_complete = max(0,int(round(float(td)/length,2)*100))
            return pct_complete
    return "0"
    
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
    
@register.filter
def subtract(value, arg):
    return value - arg

    
@register.filter
def localize(value, arg):
    return value.replace(tzinfo=pytz.timezone(arg))

@register.filter
def date_diff(value, secondary):
    diff = secondary - value
    return diff.days
    
@register.filter 
def getday(value, arg):
    date, tzinfo = arg.split("|")
    local_time = pytz.timezone(tzinfo)
    days = local_time.fromutc(value.replace(tzinfo=local_time)).date() - datetime.strptime(date,"%m/%d/%Y").date()
    return days.days+1
    #return datetime.strptime(value.isoformat()[0:10],"%Y-%m-%d").date()

