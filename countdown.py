#!/usr/bin/python

import argparse
import datetime
import os
import sys


DISPLAY_DAYS = 1
DISPLAY_MONTHS = 2
DISPLAY_YEARS = 3


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

   def relative_days(self):
      '''Returns relative date, such as 5 (if remaining) or -5 (if past).

      '''
      days = (self.when - datetime.date.today()).days
      if days > 0:
         return days + (1 if self.inclusive else 0)
      else:
         return days - (1 if self.inclusive else 0)

   def relative_months(self):
      days = self.relative_days()
      return float(days) / 30.

   def relative_years(self):
      days = self.relative_days()
      return float(days) / 365.

   def to_string(self, display):
      # Get the value
      if display == DISPLAY_DAYS:
         delta = self.relative_days()
      elif display == DISPLAY_MONTHS:
         delta = self.relative_months()
      elif display == DISPLAY_YEARS:
         delta = self.relative_years()

      if delta > 0:
         dir_text = 'left'
      else:
         delta *= -1
         dir_text = 'ago'

      # Format it
      if display == DISPLAY_DAYS:
         delta = '%6u days %-4s' % (delta, dir_text)
      elif display == DISPLAY_MONTHS:
         delta = '%5.2f months %-4s' % (delta, dir_text)
      elif display == DISPLAY_YEARS:
         delta = '%5.2f years %-4s' % (delta, dir_text)

      return '%s - %s' % (delta, self.description)

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

   def to_string(self, display):
      res = '-- %s ' % (self.description)
      res += '-'*(50-len(res))
      for event in self.events:
         res += '\n%s' % (event.to_string(display))
      res += '\n'
      return res

class Countdown(object):
   def __init__(self, filename, display):
      default_section = Section('Default Group')
      self.sections = [default_section]
      self.current_section = default_section

      if display:
         self.display = display
      else:
         self.display = DISPLAY_DAYS

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
            res += '%s%s' % (nl, sec.to_string(self.display))
            nl = '\n'
      return res


if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   group = parser.add_mutually_exclusive_group()
   group.add_argument('-d', action='store_const',const=DISPLAY_DAYS,
         dest='display', help='display in days')
   group.add_argument('-m', action='store_const', const=DISPLAY_MONTHS,
         dest='display', help='display in months')
   group.add_argument('-y', action='store_const', const=DISPLAY_YEARS,
         dest='display', help='display in years')
   args, rest = parser.parse_known_args()

   if len(rest):
      filename = rest[0]
   else:
      filename = os.path.join(os.environ.get('HOME'), '.countdownrc')
   c = Countdown(filename, args.display)

   print c
