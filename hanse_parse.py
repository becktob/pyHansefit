# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET
import datetime
from typing import List, Union

from mechanize import Browser
import re
import warnings

if os.path.isfile("settings.py"):
    import settings

strptime = datetime.datetime.strptime  # cannot "import .. as .." for some reason?
strftime = datetime.datetime.strftime

dateformat = "%d.%m.%Y %H:%M:%S"

data_url = "https://cas.hansefit.de/redlink/cas/report/check_ins/for_customer"
authentication_url = 'https://cas.hansefit.de/login'
credentials_filename = 'credentials'  # contains two lines: username \n password
ua = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0'


class Checkin:
    def __init__(self, init: Union[str, ET.Element]):
        self.name = ""
        self.location = ""
        self.date_start = None
        self.date_end = None
        self.duration = None

        if isinstance(init, ET.Element):
            self.init_from_tr(init)
        elif isinstance(init, str):
            self.init_from_repr(init)

    def init_from_tr(self, tree_tr):
        tds = tree_tr.findall("td")
        texts = [td.text.strip(" \n") for td in tds]

        self.name = texts[2] +" "+ texts[1]
        self.location = texts[3]
        start_string = texts[4]
        self.date_start = strptime(start_string, dateformat)
        end_string = texts[5]
        try:
            self.date_end = strptime(end_string, dateformat)
        except ValueError:
            warnstring = "End time not found ({}, {})".format(self.location, self.date_start)
            warnings.warn(warnstring)
            self.date_end = self.date_start + datetime.timedelta(hours=2)
        self.duration = self.date_end - self.date_start

        if self.date_end.time() > datetime.time(hour=23, minute=55):
            warnstring = u"limited a {} check-in to two hours.".format(self.location)
            warnings.warn(warnstring)
            self.duration = datetime.timedelta(hours=2)

    def init_from_repr(self, repr_str:str):
        repr_re = "<Checkin start=\"(?P<start>.+?)\" end=\"(?P<end>.+?)\" loc=\"(?P<loc>.+?)\">"
        match = re.match(repr_re, repr_str)
        self.date_start = strptime(match.group("start"), dateformat)
        self.date_end = strptime(match.group("end"), dateformat)
        self.duration = self.date_end - self.date_start
        self.location = match.group("loc")

    def __repr__(self):
        string = "<Checkin start=\"{}\" end=\"{}\" loc=\"{}\">"
        repr_start = strftime(self.date_start, dateformat)
        repr_end = strftime(self.date_end, dateformat)
        return string.format(repr_start, repr_end, self.location)

    def __str__(self):
        date_string = self.date_start.strftime("%d.%m.%Y")
        string = u"Training am {} bei {} ({})".format(date_string, self.location, self.duration)
        return string


class HanseBrowser:
    def __init__(self):
        self.username, self.password = self.load_credentials(credentials_filename)

        self.browser = Browser()
        self.submit_login()
        self.html = self.get_usage_page()

    def load_credentials(self, filename):
        filehandle = open(filename)
        user, password = "", ""
        try:
            user = filehandle.readline().rstrip()  # strip newline returned by readline()
            password = filehandle.readline().rstrip()
        except:
            print("password file does not contain two lines")
        if filehandle.readline():
            print("password file too long")
        return user, password

    def submit_login(self):
        self.browser.addheaders = [('User-agent', ua)]
        self.browser.open(authentication_url)
        self.browser.select_form(nr=0)
        self.browser.form['_username'] = self.username
        self.browser.form['_password'] = self.password
        self.browser.submit()

    def get_usage_page(self):
        self.browser.open(data_url)
        html = self.browser.response().read()
        return html

    def get_checkins(self):
        #  the entire file is invalid xml, so we get the tbody with a regex
        searcher = re.compile(b"(<tbody.*?tbody>)", re.DOTALL)  # DOTALL: dot includes newlines
        tbody = searcher.search(self.html).groups()[0]

        #  now this can be parsed and we can work safely with a tree from here
        tree = ET.fromstring(tbody)
        tree_tr = tree.findall("tr")

        checkins = [Checkin(tr) for tr in tree_tr]
        return checkins


def load_checkins(fname: str) -> List[Checkin]:
    if not os.path.isfile(fname):
        return []

    with open(fname) as fhandle:
        return [Checkin(line) for line in fhandle]


def save_checkins(fname: str, checkins: List[Checkin]):
    old_checkins = load_checkins(fname)
    print("found {} old checkins".format(len(old_checkins)))

    last_checkin_date = datetime.datetime(year=2000, month=1, day=1)
    if len(old_checkins) > 0:
        last_checkin = old_checkins[-1].date_start

    new = 0
    with open(fname, "a") as fhandle:

        for ch in (ch for ch in checkins if ch.date_start > last_checkin_date):
            fhandle.write(repr(ch) + "\n")
            new += 1
    print("wrote {} checkins to {}, skipped {}".format(new, fname, len(checkins)-new))


if __name__ == '__main__':
    hanse = HanseBrowser()
    checkin_list = hanse.get_checkins()
    print("{} Checkins:".format(len(checkin_list)))
    for checkin in checkin_list:
        print(checkin)

    save_checkins("checkins.dat", checkin_list)
