# spam-report
Script which compiles a daily summary of spam messages quarantined by amavis

## Credits
This work was inspired by [thelibrarian](https://github.com/thelibrarian)'s [sa-daily-report](https://github.com/thelibrarian/sa-daily-report), which unfortunately does not seem to work well with the quarantine directory structure employed by modern versions of amavis. Because I don't know Ruby and I didn't want to learn it today, I carried out a black-box reimplementation of the functionality in Python.

## Overview
This script will email you a report listing spam quarantined by amavis within the past day, orded by ascending X-Spam-Score (as to facilitate identification of false positives).

Configuration is simple:

- Set `spam_glob` to point to amavis's quarantine directory. The default works with Ubuntu 16.04 and probably other flavors of Debian.
- Choose `max_report` to set an upper bound on the number of messages which will be included in the report. This was necessary because I found that preparing and sending a report covering ~1,000 messages takes an inordinate amount of time.
- Specify where the report will be delivered via `to_name` and `to_address`.
- Describe the sender by choosing `from_name` and `from_address`.
- Point `smtp_server` and `smtp_port` toward wherever your outgoing mailserver lives.

Then, set up a cronjob to run the script daily. You may need to add your user to the group that owns the amavis quarantine in order for it to be readable. Unfortunately, Python's `glob` fails silently if you do not have permissions to read the directory, so you will simply get empty reports if this is a problem.

## Miscellanea
This work is released under the MIT License, which can be found in the accompanying LICENSE file.

If you find any problems or have ideas for improvements to this script, Issues and Pull Requests will be taken amiably.
