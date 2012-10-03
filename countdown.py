#!/usr/bin/python

import datetime
import os
import sys


class Event(object):
   def __init__(self, description, when):
      self.description = description
      self.when = when

   @classmethod
   def from_string(cls, s):
      parts = s.split(' ')
      date = parts[0]
      description = ' '.join(parts[1:]).strip()

      try:
         when = datetime.datetime.strptime(date, '%Y-%m-%d').date()
      except ValueError:
         return None

      return Event(description, when)

   def relative_date(self, padding=0):
      '''Returns relative date, such as 5 (if remaining) or -5 (if past).

      '''
      return (self.when - datetime.date.today()).days

   def __str__(self):
      return 'event<%s @ %s>' % (self.description, self.when)

class Countdown(object):
   def __init__(self, filename=None):
      self.events = []

      with open(filename, "r") as fh:
         raw_data = fh.readlines()

      for raw_event in raw_data:
         event = Event.from_string(raw_event)
         if not event:
            raise ValueError("invalid event format: %s" % raw_event)
         self.events.append(event)

   def __str__(self):
      res = ''
      nl = ''
      for event in self.events:
         days = event.relative_date()
         if days > 0:
            dir_text = 'left'
         else:
            days *= -1
            dir_text = 'ago'
         res += '%(newline)s%(days)4d days %(dir)-5s - %(desc)s' % {
            'newline': nl,
            'days': days,
            'dir': dir_text,
            'desc': event.description,
         }
         nl = '\n'
      return res


if __name__ == '__main__':
   if len(sys.argv) > 1:
      filename = sys.argv[1]
   else:
      filename = os.path.join(os.environ.get('HOME'), '.countdownrc')
   c = Countdown(filename)

   print c
