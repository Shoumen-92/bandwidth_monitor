#!/usr/bin/python
# (c) 2010 Marc-Antoine Ruel. No right reserved.
"""Screen scrape the ISP pages to return the bandwidth usage.

Run as a cron job to alert when you're nearing quota.
"""

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
    env = {'isp': None, 'cap': None, 'alert': None}
    def do(module):
      for i in clean_list(module):
        assert not i in env
        env[i] = getattr(module, i)
    do(isp)
    do(cap)
    do(alert)
    execfile(os.path.join(self.base_dir, 'bandwidth_monitor.cfg'), env)
    self.isp = env['isp']
    self.cap = env['cap']
    self.alert = env['alert']

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
    results.update(config.isp.get_usage())

  fraction = config.cap.monthly(results)
  if options.daily:
    print('')
    config.cap.daily(results)
  if not options.no_save and not options.no_fetch:
    config.save_results(results)
  if options.alert is not None:
    if (fraction * 100.) >= options.alert:
      msg = 'Using too much bandwidth! %.1f%% of %s' % (
          fraction * 100., cap.nice(config.cap.max_kb))
      config.alert.alert('Oops!', msg)
      print >> sys.stderr, '\n' + msg
      return 1
  return 0


if __name__ == '__main__':
  sys.exit(main())

