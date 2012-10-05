#!/usr/bin/python

import datetime
import os
import sys


class Event(object):
   def __init__(self, description, when, inclusive=False):
      self.description = description
      self.when = when
      self.inclusive = inclusive

   @classmethod
   def from_string(cls, s):
      parts = s.split(' ')
      date = parts[0]
      description = ' '.join(parts[1:])

      inclusive = False
      if date[-1] == '!':
         inclusive = True
         date = date[:-1]

      try:
         when = datetime.datetime.strptime(date, '%Y-%m-%d').date()
      except ValueError:
         return None

      return Event(description, when, inclusive)

   def relative_date(self, padding=0):
      '''Returns relative date, such as 5 (if remaining) or -5 (if past).

      '''
      days = (self.when - datetime.date.today()).days
      if days > 0:
         return days + (1 if self.inclusive else 0)
      else:
         return days - (1 if self.inclusive else 0)

   def __str__(self):
      days = self.relative_date()
      if days > 0:
         dir_text = 'left'
      else:
         days *= -1
         dir_text = 'ago'

      return '%(days)4d days %(dir)-4s - %(desc)s' % {
         'days': days,
         'dir': dir_text,
         'desc': self.description,
      }

class Section(object):
   def __init__(self, description):
      self.description = description
      self.events = []

   def append(self, obj):
      self.events.append(obj)

   def sort(self):
      self.events.sort(lambda x,y: (x.when-y.when).days)

   def __len__(self):
      return len(self.events)

   def __str__(self):
      res = '-- %s ' % (self.description)
      res += '-'*(50-len(res))
      for event in self.events:
         res += '\n%s' % (str(event))
      res += '\n'
      return res

class Countdown(object):
   def __init__(self, filename=None):
      default_section = Section('Default Group')
      self.sections = [default_section]
      self.current_section = default_section

      with open(filename, "r") as fh:
         raw_data = fh.readlines()

      for raw_event in raw_data:
         raw_event = raw_event.strip()

         # skip comments and blank lines
         if not raw_event or raw_event[0] == '#':
            continue

         # New section
         if raw_event[0] == '-':
            sec = Section(raw_event[1:].strip())
            self.current_section = sec
            self.sections.append(sec)

         # New event
         else:
            event = Event.from_string(raw_event)
            if not event:
               raise ValueError("invalid event format: %s" % raw_event)
            self.current_section.append(event)

      for sec in self.sections:
         sec.sort()

   def __str__(self):
      res = ''
      nl = ''
      for sec in self.sections:
         if len(sec):
            res += '%s%s' % (nl, str(sec))
            nl = '\n'
      return res


if __name__ == '__main__':
   if len(sys.argv) > 1:
      filename = sys.argv[1]
   else:
      filename = os.path.join(os.environ.get('HOME'), '.countdownrc')
   c = Countdown(filename)

   print c
