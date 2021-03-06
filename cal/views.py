from datetime import datetime, timedelta

from icalendar import Calendar
from icalendar import Event as iCalEvent

from django.http import HttpResponse


def to_ics(events):
    cal = Calendar()
    cal.add('prodid', '-//cyb.no//')
    cal.add('version', '2.0')
    cal.add('X-WR-CALNAME', 'cyb.no')

    for event in events:
        e = iCalEvent()

        e.add('uid', '%d@cyb.no' % event.pk)

        e.add('dtstamp', datetime.utcnow())
        if not event.is_allday:
            e.add('dtstart', event.start)
            e.add('dtend', event.end)
        else:
            e.add('dtstart', event.start_date())
            e.add('dtend', event.end_date() + timedelta(days=1))

        e.add('summary', event.title)
        e.add('description', event.description)

        cal.add_component(e)

    response = HttpResponse(cal.to_ical())
    response['Content-Type'] = 'text/calendar'

    return response
