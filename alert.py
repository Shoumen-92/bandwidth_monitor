#!/usr/bin/python
# (c) 2010 Marc-Antoine Ruel. No right reserved.
"""Alert types definitions."""

from email.mime.text import MIMEText
import smtplib


class Email(object):
  """Send an email upon alert."""

  def __init__(self, host, fromaddr, toaddr, usr, pwd):
    self.host = host
    self.usr = usr
    self.pwd = pwd
    self.fromaddr = fromaddr
    self.toaddr = toaddr

  def alert(self, subject, text):
    smtp = smtplib.SMTP(self.host)
    #smtp.login(self.usr, self.pwd)
    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = self.fromaddr
    msg['To'] = self.toaddr
    smtp.sendmail(self.fromaddr, [self.toaddr], msg.as_string())
    smtp.quit()
