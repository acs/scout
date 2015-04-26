#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This script parses IRC logs and stores the extracted data in
# a database
# 
# Copyright (C) 2012-2013 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#   Alvaro del Castillo San Felix <acs@bitergia.com>
#   Santiago Dueñas <sduenas@bitergia.com>
#

import calendar
import io
import logging
import requests
import os
import sys
import re

from datetime import datetime
from optparse import OptionParser

from Scout.database import Database

class Error(Exception):
    """Application error."""


def read_options():
    parser = OptionParser(usage="usage: %prog [options]",
                          version="%prog 0.1")
    parser.add_option("--dir",
                      action="store",
                      dest="data_dir",
                      default="irc",
                      help="Directory with all IRC logs")
    parser.add_option("-f", "--file",
                      action="store",
                      dest="events_file",
                      help="File with the events to be loaded")
    parser.add_option("-b", "--backend",
                      action="store",
                      dest="backend",
                      default="stackoverflow",
                      help="Backend to use for the events (stackoverflow, github, ...)")
    parser.add_option("-d", "--database",
                      action="store",
                      dest="dbname",
                      help="Database where information is stored")
    parser.add_option("-u", "--db-user",
                      action="store",
                      dest="dbuser",
                      default="root",
                      help="Database user")
    parser.add_option("-p", "--db-password",
                      action="store",
                      dest="dbpassword",
                      default="",
                      help="Database password")
    parser.add_option("-g", "--debug",
                      action="store_true",
                      dest="debug",
                      default=False,
                      help="Debug mode")


    (opts, args) = parser.parse_args()

    if len(args) != 0:
        parser.error("Wrong number of arguments")

    if not (opts.dbname and opts.dbuser and opts.events_file):
        parser.error("--database --db-user --file are needed")

    return opts


def string_to_datetime(s, schema):
    """Convert string to datetime object"""
    try:
        return datetime.strptime(s, schema)
    except ValueError:
        raise Error("Parsing date %s to %s format" % (s, schema))

def parse_csv_file(filepath, db, backend = "stackoverflow"):
    """Parse a CSV events file."""
    if backend != "stackoverflow": 
        raise ("Backend not supported: " + backend)
    try:
        infile = io.open(filepath, 'rt')
    except EnvironmentError as e:
        raise Error("Cannot open %s for reading: %s" % (filepath, e))

    count_events = 0
    count_events_new = 0
    # last_date = db.get_last_date(channel_id)

    try:
        if backend == "stackoverflow":
            fields = None
            for event_data in infile:
                if fields is None:
                    fields = event_data[:-1].split(",")
                    continue
                db.so_insert_event(event_data, fields)
        count_events_new += 1
    except Exception as e:
        raise Error("Error parsing %s file: %s" % (filepath, e))
    finally:
        infile.close()
    return count_events, count_events_new


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')

    opts = read_options()

    db = Database(opts.dbuser, opts.dbpassword, opts.dbname)
    db.open_database()
    db.create_tables()
    count_events = count_events_new = count_events_drop = count_files_drop = 0
    count_special_events = 0


    try:
        parse_csv_file(opts.events_file, db)
    except Error as e:
        print(e)

    db.close_database()
#     print("Total events: %s" % (count_events))
#     print("Total special events: %s" % (count_special_events))
#     print("Total new events: %s" % (count_events_new))
#     print("Total drop events: %s" % (count_events_drop))
#     print("Total log files drop: %s" % (count_files_drop))
    sys.exit(0)
