#!/usr/bin/env python3

import sys
import configparser
from datetime import datetime, timedelta
import glob
import stat
import os
import gzip
import email.parser
import email.mime.text
import smtplib

class ns_dict (dict):
    def __getattr__(self, key):
        return self[key]

class get_config (object):

    _section = "spam_report"
    _types = {
        'spam_glob': '',
        'max_report': 'int',
        'to_address': '',
        'to_name': '',
        'from_address': '',
        'from_name': '',
        'smtp_server': '',
        'smtp_port': 'int'
    }

    def __init__(self, config_file):
        self._conf = configparser.ConfigParser()
        self._conf.read(config_file)

    def __getattr__(self, key):
        get = getattr(self._conf, "get" + self._types[key])
        return get(self._section, key)

def get_spam(spam_glob):
    def generator():
        time_thresh = (datetime.now() - timedelta(days=1)).timestamp()
        parser = email.parser.BytesHeaderParser()
        for match in glob.iglob(spam_glob):
            timestamp = os.stat(match)[stat.ST_CTIME]
            if timestamp > time_thresh:
                with gzip.open(match) as fh:
                    res = parser.parse(fh)
                    yield ns_dict({
                        'to'    : res['To'],
                        'frm'   : res['From'],
                        'subj'  : res['Subject'],
                        'id'    : res['X-Quarantine-ID'],
                        'score' : res['X-Spam-Score'],
                        'time'  : timestamp
                    })
    return list(generator())

def make_report_header(date, total, reported):
    header = \
"""
Spam report for %s

Total objects quarantined: %d
Top %d lowest-scoring messages follow

%s
"""
    header = header % (date, total, reported, "-" * 80)
    return header.strip()

def make_report_entry(spam):
    entry = \
"""
To:            %s
From:          %s
Subject:       %s
Spam Score:    %s
Quarantine ID: %s
"""
    entry = entry % (spam.to, spam.frm, spam.subj, spam.score, spam.id)
    return entry.strip()

def make_report_body(spam_list):
    return "\n\n".join(map(make_report_entry, spam_list))

def make_report_trailer():
    return "-" * 80

def make_report(spam_list, conf):
    date = datetime.now().strftime("%a %b %d %Y")
    spam_list = sorted(spam_list, key=lambda s: s.score)
    total_size = len(spam_list)
    spam_list = spam_list[:conf.max_report]

    msg = email.mime.text.MIMEText(make_report_header(date, total_size, len(spam_list))
                                   + "\n\n"
                                   + make_report_body(spam_list)
                                   + "\n\n"
                                   + make_report_trailer())

    msg['Subject'] = "Spam report for %s" % date
    msg['From'] = "%s <%s>" % (conf.from_name, conf.from_address)
    msg['To'] = "%s <%s>" % (conf.to_name, conf.to_address)

    return msg

def send_report(report, conf):
    with smtplib.SMTP(conf.smtp_server, conf.smtp_port) as smtp:
        smtp.sendmail(conf.from_address, [conf.to_address], report.as_string())

def main(config_file=None):

    if config_file is None:
        sys.stderr.write("usage: python %s <config_file.ini>\n" % sys.argv[0])
        return 1

    conf = get_config(config_file)
    spam = get_spam(conf.spam_glob)
    rept = make_report(spam, conf)
    send_report(rept, conf)

    return 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
