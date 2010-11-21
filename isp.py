# (c) 2010 Marc-Antoine Ruel. No right reserved.
"""Define code required to scrape the ISP pages to return the bandwidth usage.
"""

import re
import sys
import time


def get_webdriver():
  try:
    from selenium.firefox import webdriver
  except ImportError:
    print >> sys.stderr, 'Run sudo easy_install selenium'
    sys.exit(1)
  return webdriver.WebDriver()


class Videotron(object):
  """Videotron's Residential cable service."""

  def __init__(self, usr, pwd):
    # Untested.
    self.initial_url = 'https://www.videotron.com/client/Espace-client'
    self.usage_url = (
        'https://www.videotron.com/client/secur/ConsoAffaires.do'
        '?lang=FRENCH')
    self.usr = usr
    self.pwd = pwd

  def get_usage(self):
    """Fetches bandwidth usage from the ISP pages and returns as a dict.

    {
      'day': { <day>: (DownloadInKb, UploadInKb), ... },
      'month': { <month>: (DownloadInKb, UploadInKb), ... },
    }
    """
    # I wanted to use mechanize but Omniture crappy javascript code does
    # cross-site cookie setting that are checked server-side upon login.
    start = time.time()
    def shame(msg):
      print('%4.1fs %s' % (time.time() - start, msg))
    shame('Loading firefox')
    # TODO:
    # server_num = 99
    # subprocess.Popen(['xvfb-run', '--server-num=%d' % server_num,
    # '--server-args=-screen 0, 800x600x24', 'firefox'])
    # pid = int(open('/tmp/.X%d-lock' % server_num).read().strip())
    # os.kill(pid, signal.SIGINT)
    wd = get_webdriver()
    try:
      shame('Loading initial page to create cookies')
      wd.get(self.initial_url)
      shame('Loading login page')
      wd.find_element_by_link_text('Entrez maintenant').click()
      shame('Loging in')
      wd.find_element_by_name('codeUtil').send_keys(self.usr)
      wd.find_element_by_name('motDePasse').send_keys(self.pwd)
      wd.find_element_by_name('btnSubmit').submit()
      shame('Visit consumption link')
      wd.get(self.usage_url)
      shame('Done, now loading data from WebDriver')
      results = { 'month': {}, 'day': {} }
      # TODO This part is really slow, we should find out a way to improve the
      # performance.
      tables = wd.find_elements_by_class_name('data')
      monthly = tables[0].find_element_by_tag_name('tbody')
      for tr in monthly.find_elements_by_tag_name('tr'):
        tds = tr.find_elements_by_tag_name('td')
        month = re.sub(r'\s+', ' ', str(tds[0].get_text().strip()))
        results['month'][month] = (
            float(tds[2].get_text().strip())*1024.,
            float(tds[4].get_text().strip())*1024.)
      daily = tables[1].find_element_by_tag_name('tbody')
      for tr in daily.find_elements_by_tag_name('tr'):
        tds = tr.find_elements_by_tag_name('td')
        day = str(tds[0].get_text().strip())
        results['day'][day] = (
            float(tds[1].get_text().strip()),
            float(tds[3].get_text().strip()))
      shame('Done fetching data\n')
      return results
    finally:
      wd.close()
      wd.quit()


class VideotronBusiness(Videotron):
  """Videotron's Business cable service."""

  def __init__(self, *args):
    super(VideotronBusiness, self).__init__(*args)
    self.initial_url = (
        'https://affaires.videotron.com/affaires/fr/espace-client/index.jsp')
    self.usage_url = (
        'https://affaires.videotron.com/affaires/secur/ConsoAffaires.do'
        '?lang=FRENCH')
