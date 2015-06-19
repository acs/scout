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

import logging
import sys

from datetime import datetime
from optparse import OptionParser

from Scout.database import Database
from Scout.utils import DSQuery, createJSON


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
                      help="Backend to use for the events " +
                            "(stackoverflow, github, ...)")
    parser.add_option("-j", "--json",
                      action="store",
                      dest="json_file",
                      help="Generate a JSON file with the events.")
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

    if not (opts.dbname and opts.dbuser):
        parser.error("--database --db-user are needed")

    return opts


def load_reddit(keyword, db, backend):
    """Load reddit items in MySQL"""
    # Right now only 100 events are gathered. No pagination done.
    # Around two weeks in centos
    import os
    import json

    # https://www.reddit.com/search.json?q=centos&sort=new
    limit = 100  # max 100
    url = "https://www.reddit.com/search.json?q="+keyword
    url += "&sort=new"
    url += "&limit="+str(limit)

    cache_file = "data/reddit_cache.json"

    if not os.path.isfile(cache_file):
        import requests
        r = requests.get(url, verify=False, headers={'user-agent': 'scout'})
        data = r.json()
        with open(cache_file, 'w') as f:
            f.write(json.dumps(data))
    else:
        with open(cache_file) as f:
            data = json.loads(f.read())
    for child in data['data']['children']:
        if child['kind'] != "t3":
            logging.warn("Only t3 (links) supported in reddit " +
                         child['kind'])
            continue

        cdata = child['data']
        reddit_id = cdata['id']
        title = cdata['title']
        created = datetime.fromtimestamp(cdata['created'])
        created = created.strftime('%Y-%m-%d %H:%M:%S')
        url = cdata['permalink']
        author = cdata['author']
        body = cdata['selftext']
        score = cdata['score']
        likes = cdata['likes']
        ncomments = cdata['num_comments']
        db.reddit_insert_event(reddit_id, title, created, url, author,
                               body, score, likes, ncomments)


def load_csv_file(filepath, db, backend):
    """Load a CSV events file in MySQL"""
    import csv
    if backend not in ("stackoverflow", "github", "mail"):
        raise ("Backend not supported: " + backend)
    try:
        # mail csv file is ASCII. The rest is UTF8
        if backend in ["mail", "stackoverflow"]:
            infile = open(filepath, 'rt')
        elif backend in ["github"]:
            import codecs
            infile = codecs.open(filepath, "rt", "utf-8")

    except EnvironmentError as e:
        raise Error("Cannot open %s for reading: %s" % (filepath, e))

    count_events = 0
    count_events_new = 0
    # last_date = db.get_last_date(channel_id)

    if backend == "github":
        # Don't use CSV module for this format. Not easy to parse with it.
        pass
    elif backend == "mail":
        data = csv.reader(infile, delimiter=',', quotechar='"',
                          escapechar='\\')
    else:
        data = csv.reader(infile, delimiter=',', quotechar='"')

    try:
        fields = None
        if backend in ["mail", "stackoverflow"]:
            for event_data in data:
                if backend != "mail":
                    # In mail CSV we don't have fields in the first row
                    if fields is None:
                        # first row are the fields names
                        fields = event_data
                        continue
                # TODO: Loosing " inside the body. To be fixed. Quick hack.
                event_data = [fevent.replace('"', '') for fevent in event_data]
                event_data_str = '"' + '","'.join(event_data) + '"'
                if backend == "stackoverflow":
                    db.stackoverflow_insert_event(event_data_str, fields)
                elif backend == "github":
                    db.github_insert_event(event_data, fields)
                elif backend == "mail":
                    db.mail_insert_event(event_data_str)
            count_events_new += 1
        elif backend in ["github"]:
            lines = infile.readlines()
            for event_data in lines:
                if fields is None:
                    # first row are the fields names
                    fields = event_data[:-1].split(",")
                    continue
                db.github_insert_event(event_data, fields)

    except Exception as e:
        import traceback
        print traceback.format_exc()
        raise Error("Error parsing %s file: %s" % (filepath, e))
    finally:
        infile.close()
    return count_events, count_events_new


def create_events(filepath, backend):
    dsquery = DSQuery(opts.dbuser, opts.dbpassword, opts.dbname)

    def get_stackoverflow_events():
        table = "stackoverflow_events"
        url_posts = "http://stackoverflow.com/questions/"
        url_user = "http://stackoverflow.com/users/"
        # Common fields for all events: date, summmary, url
        q = "SELECT CONCAT('"+url_posts+"',Post_Link) as url, " + \
            "CreationDate as date, title as summary, "
        q += "ViewCount as views, Score as score, PostTypeId as type, body, "
        q += "CONCAT('"+url_user+"',User_Link) as author_url, "
        q += "DisplayName as author"
        q += " FROM " + table
        q += " ORDER BY date DESC "
        return dsquery.ExecuteQuery(q)

    def get_github_events():
        table = "github_events"
        # Common fields for all events: date, summmary, url
        q = "SELECT repo_url as url, created_at as date, " + \
            "repo_name as summary, type, body, status, actor_url as author "
        q += " FROM " + table
        q += " ORDER BY date DESC "
        return dsquery.ExecuteQuery(q)

    def get_mail_events():
        table = "mail_events"
        # Common fields for all events: date, summmary, url
        q = "SELECT url, sent_at as date, subject as summary, body, author "
        q += " FROM " + table
        q += " ORDER BY date DESC "
        return dsquery.ExecuteQuery(q)

    def get_reddit_events():
        table = "reddit_events"
        url_posts = "https://www.reddit.com/"
        url_user = "https://www.reddit.com/user/"
        # Common fields for all events: date, summmary, url
        q = "SELECT CONCAT('"+url_posts+"',url) as url, " + \
            "created as date, title as summary, body, "
        q += "CONCAT('"+url_user+"',author) as author, "
        q += "score, likes, num_comments"
        q += " FROM " + table
        q += " ORDER BY date DESC "
        return dsquery.ExecuteQuery(q)

    if backend == "stackoverflow":
        res = {"stackoverflow": get_stackoverflow_events()}
        createJSON(res, filepath)

    elif backend == "github":
        res = {"github": get_github_events()}
        createJSON(res, filepath)

    elif backend == "mail":
        res = {"mail": get_mail_events()}
        createJSON(res, filepath)

    elif backend == "reddit":
        res = {"reddit": get_reddit_events()}
        createJSON(res, filepath)

    elif backend is None:
        # Generate all events
        res = {"stackoverflow": get_stackoverflow_events(),
               "github": get_github_events(),
               "mail": get_mail_events(),
               "reddit": get_reddit_events()}
        createJSON(res, filepath)


def create_tables(backend):
    if opts.backend == "stackoverflow":
        db.create_tables_stackoverflow()
    elif opts.backend == "github":
        db.create_tables_github()
    elif opts.backend == "mail":
        db.create_tables_mail()
    elif opts.backend == "reddit":
        db.create_tables_reddit()
    else:
        logging.error(opts.backend + " not supported")
        raise

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

    opts = read_options()
    db = Database(opts.dbuser, opts.dbpassword, opts.dbname)
    db.open_database()
    try:
        if opts.json_file:
            create_events(opts.json_file, opts.backend)
        else:
            create_tables(opts.backend)
            if opts.backend != "reddit":
                load_csv_file(opts.events_file, db, opts.backend)
            else:
                keyword = "centos"  # right now it is hard coded in others
                load_reddit(keyword, db, opts.backend)
    except Error as e:
        print(e)

    db.close_database()
    sys.exit(0)
