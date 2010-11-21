#!/usr/bin/python
# (c) 2010 Marc-Antoine Ruel. No right reserved.
"""Screen scrape the ISP pages to return the bandwidth usage.

Run as a cron job to alert when you're nearing quota.
"""

import ConfigParser
import json
import optparse
import os
import re
import sys

import alert
import cap
import isp


def clean_list(module):
  return [i for i in dir(module)
      if ((i[0] != '_') and not re.match(r'[a-z]+', i))]


class Config(object):
  def __init__(self):
    self.base_dir = 'data'
    config = ConfigParser.SafeConfigParser()
    config.read(os.path.join(self.base_dir, 'bandwidth_monitor.ini'))
    section = 'monitor'

    def load_item(name):
      data = [x.strip() for x in config.get(section, name).split(',')]
      return data[0], data[1:]

    self.isp, self.isp_args = load_item('isp')
    isp_choices = clean_list(isp)
    if not self.isp in isp_choices:
      raise Exception('Unknown ISP %s\nAvailable ISPs: %s' % (
          self.isp, ', '.join(isp_choices)))

    self.cap, self.cap_args = load_item('cap')
    cap_choices = clean_list(cap)
    if not self.cap in cap_choices:
      raise Exception('Unknown cap type %s\nAvailable caps: %s' % (
          self.cap, ', '.join(cap_choices)))

    self.alert, self.alert_args = load_item('alert')
    alert_choices = clean_list(alert)
    if not self.alert in alert_choices:
      raise Exception('Unknown alert type %s\nAvailable alerts: %s' % (
          self.alert, ', '.join(cap_choices)))

  def get_isp(self):
    return getattr(isp, self.isp)(*self.isp_args)

  def get_cap(self, data):
    return getattr(cap, self.cap)(data, *self.cap_args)

  def get_alert(self):
    return getattr(alert, self.alert)(*self.alert_args)

  def load_old_results(self):
    """Loads data from a json file."""
    filename = os.path.join(self.base_dir, 'bandwidth.json')
    try:
      return json.load(open(filename, 'r'))
    except IOError:
      return {}
    except ValueError:
      # Toss it away.
      if os.path.exists(filename + '.old'):
        os.remove(filename + '.old')
      os.rename(filename, filename + '.old')
      return {}

  def save_results(self, data):
    """Saves the data as a human readable json file."""
    filename = os.path.join(self.base_dir, 'bandwidth.json')
    if os.path.exists(filename + '.old'):
      os.remove(filename + '.old')
    if os.path.exists(filename):
      os.rename(filename, filename + '.old')
    json.dump(data, open(filename, 'w'), sort_keys=True, indent=2)


def main():
  parser = optparse.OptionParser()
  parser.add_option('--no-fetch', action='store_true')
  parser.add_option('--no-load', action='store_true')
  parser.add_option('--no-save', action='store_true')
  parser.add_option('--daily', action='store_true')
  parser.add_option('--run_custom_cmd', help=optparse.SUPPRESS_HELP)
  parser.add_option('--alert', type=float, help='Percent to return 2')
  options, args = parser.parse_args()
  if args:
    parser.error('Unsupported args: %s' % args)

  config = Config()
  if not options.no_load:
    results = config.load_old_results()
  else:
    results = {}
  if not options.no_fetch:
    ispobj = config.get_isp()
    results.update(ispobj.get_usage())

  capobj = config.get_cap(results)
  fraction = capobj.monthly()
  if options.daily:
    print('')
    capobj.daily()
  if not options.no_save and not options.no_fetch:
    config.save_results(results)
  if options.alert is not None:
    if (fraction * 100.) >= options.alert:
      msg = 'Using too much bandwidth! %.1f%% of %s' % (
          fraction * 100., cap.nice(capobj.max_kb))
      alertobj = config.get_alert()
      alertobj.alert('Oops!', msg)
      print >> sys.stderr, '\n' + msg
      return 1
  return 0


if __name__ == '__main__':
  sys.exit(main())

