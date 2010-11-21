#!/usr/bin/python
# (c) 2010 Marc-Antoine Ruel. No right reserved.
"""ISP Caps types definitions."""


def nice(value):
  """Returns nicer printout for a value in kb."""
  if value > (1024*1024*10240):
    return '%.2fTb' % (value / (1024. * 1024. * 1024.))
  elif value > (1024*10240):
    return '%.2fGb' % (value / (1024. * 1024.))
  elif value > 10240:
    return '%.2fMb' % (value / 1024.)
  else:
    return '%dKb' % value


class Unlimited(object):
  """Unlimited bandwidth usage."""

  def __init__(self, data):
    self.data = data

  def monthly(self):
    blob = self.data['month']
    for moment in sorted(blob.keys()):
      values = blob[moment]
      print('%s: %10s %10s' % (moment,  nice(values[0]), nice(values[1])))
    return 0.

  def daily(self):
    blob = self.data['day']
    for moment in sorted(blob.keys()):
      values = blob[moment]
      print('%s: %10s %10s' % (moment,  nice(values[0]), nice(values[1])))
    return 0.


class CombinedMonthly(object):
  """Monthly cap where the cap is the sum of your upload and download."""
  def __init__(self, data, max_kb):
    self.data = data
    self.max_kb = float(max_kb)

  def monthly(self):
    """Prints out information about bandwidth usage. Expects values in kb.

    Returns the current's month bandwidth usage fraction."""
    print('Max: %s' % nice(self.max_kb))
    blob = self.data['month']
    total = 0
    for moment in sorted(blob.keys()):
      values = blob[moment]
      total = values[0] + values[1]
      print('%s: %5.1f%%; %10s' % (
          moment, (100. * total / self.max_kb), nice(total)))
    if not self.max_kb:
      return 0.
    return total / self.max_kb

  def daily(self):
    """Prints out information about bandwidth usage. Expects values in kb.

    Returns the current's day bandwidth usage fraction."""
    print('Max: %s' % nice(self.max_kb / 30.))
    blob = self.data['day']
    total = 0
    for moment in sorted(blob.keys()):
      values = blob[moment]
      total = values[0] + values[1]
      print('%s: %5.1f%%; %10s' % (
          moment, (100. * total / self.max_kb * 30.), nice(total)))
    if not self.max_kb:
      return 0.
    # TODO: count the number of days left in the month.
    return total / self.max_kb * 30.


class SeparateMonthly(object):
  """Monthly cap with individual download and upload caps."""
  def __init__(self, data, max_dn_kb, max_up_kb):
    self.data = data
    self.max_dn_kb = float(max_dn_kb)
    self.max_up_kb = float(max_up_kb)

  def monthly(self):
    """Prints out information about bandwidth usage. Expects values in kb.

    Returns the current's month bandwidth usage fraction."""
    print('Max: %s - %s' % (nice(self.max_dn_kb), nice(self.max_up_kb)))
    blob = self.data['month']
    values = (0., 0.)
    for moment in sorted(blob.keys()):
      values = blob[moment]
      print('%s: %5.1f%% - %10s; %5.1f%% - %10s' % (
          moment,
          (100. * values[0] / self.max_dn_kb), nice(values[0]),
          (100. * values[1] / self.max_up_kb), nice(values[1])))
    if not self.max_dn_kb:
      max_dn = 0
    else:
      max_dn = values[0] / self.max_dn_kb
    if not self.max_up_kb:
      max_up = 0
    else:
      max_up = values[1] / self.max_up_kb
    return max(max_dn, max_up)

  def daily(self):
    """Prints out information about bandwidth usage. Expects values in kb.

    Returns the current's day bandwidth usage fraction."""
    # TODO: count the number of days left in the month.
    print('Max: %s - %s' % (
        nice(self.max_dn_kb / 30.), nice(self.max_up_kb / 30.)))
    blob = self.data['day']
    values = (0., 0.)
    for moment in sorted(blob.keys()):
      values = blob[moment]
      print('%s: %5.1f%% - %10s; %5.1f%% - %10s' % (
          moment,
          (100. * values[0] / self.max_dn_kb * 30.), nice(values[0]),
          (100. * values[1] / self.max_up_kb * 30.), nice(values[1])))
    if not self.max_dn_kb:
      max_dn = 0
    else:
      max_dn = values[0] / self.max_dn_kb * 30.
    if not self.max_up_kb:
      max_up = 0
    else:
      max_up = values[1] / self.max_up_kb * 30.
    return max(max_dn, max_up)
