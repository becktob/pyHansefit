# -*- coding: utf-8 -*-
import xml.dom
import xml.dom.minidom
import xml.etree.ElementTree as ET
import mechanize  # pip install mechanize
import datetime
import re
import warnings

try:
    import settings
except:
    pass

dateformat = "%d.%m.%Y %H:%M:%S"

data_url = "https://cas.hansefit.de/redlink/cas/report/check_ins/for_customer"
authentication_url = 'https://cas.hansefit.de/login'
credentials_filename = 'credentials'  # contains two lines: username \n password
ua = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0'


class Checkin:
    def __init__(self, tree_tr):
        assert isinstance(tree_tr, xml.etree.ElementTree.Element)
        tds = tree_tr.findall("td")
        texts = [td.text.strip(" \n") for td in tds]

        self.nr = int(texts[0])
        self.name = texts[2] +" "+ texts[1]
        self.location = texts[3]
        start_string = texts[4]
        self.date_start = datetime.datetime.strptime(start_string, dateformat)
        end_string = texts[5]
        try:
            self.date_end = datetime.datetime.strptime(end_string, dateformat)
        except ValueError:
            warnstring = "End time not found ({}, {})".format(self.location, self.date_start)
            warnings.warn(warnstring)
            self.date_end = self.date_start + datetime.timedelta(hours=2)
        self.duration = self.date_end - self.date_start

        if self.date_end.time() > datetime.time(hour=23, minute=55):
            warnstring = u"limited a {} check-in to two hours.".format(self.location)
            warnings.warn(warnstring)
            self.duration = datetime.timedelta(hours=2)

    def __repr__(self):
        date_string = self.date_start.strftime("%d.%m.%Y")
        repr = u"Training am {} bei {} ({})".format(date_string, self.location, self.duration)
        return repr


class HanseBrowser:
    def __init__(self):
        self.username, self.password = self.load_credentials(credentials_filename)

        self.browser = mechanize.Browser()
        self.submit_login()
        self.html = self.get_usage_page()

    def load_credentials(self, filename):
        filehandle = open(filename)
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
        html = self.browser.submit()

    def get_usage_page(self):
        self.browser.open(data_url)
        html = self.browser.response().read()
        return html

    def get_checkins(self):
        #  the entire file is invalid xml, so we get the tbody with a regex
        searcher = re.compile(b"(<tbody.*?tbody>)", re.DOTALL)  # DOTALL: dot includes newlines
        tbody = searcher.search(self.html).groups()[0]

        #  no this can be parsed and we can work safely with a tree from here
        dom = xml.dom.minidom.parseString(tbody)
        tree = ET.fromstring(tbody)

        tree_tr = tree.findall("tr")

        checkins = [Checkin(tr) for tr in tree_tr]

        return checkins


if __name__ == '__main__':
    hanse = HanseBrowser()
    checkins = hanse.get_checkins()
    print("{} Checkins:".format(len(checkins)))
    for checkin in checkins:
        print(checkin)
