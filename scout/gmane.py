# -*- coding: utf-8 -*-
#
# Gmane backend for scout
#
# Copyright (C) 2012-2015 Bitergia
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
#
#

import codecs
from datetime import datetime
import logging
import os

from scout.datasource import DataSource


class Gmane(DataSource):
    """ Get events from http://search.gmane.org/ using the NOV format at
    http://search.gmane.org/nov.php?query=<keyword>&sort=date&HITSPERPAGE=999

    999 is the max HITSPERPAGE using this format.
    """

    def create_tables(self):
        query = "CREATE TABLE IF NOT EXISTS gmane_events (" + \
                "id int(11) NOT NULL AUTO_INCREMENT," + \
                "gmane_id varchar(255)," + \
                "title varchar(255)," + \
                "created DATETIME NOT NULL," + \
                "url varchar(255)," + \
                "author varchar(255)," + \
                "body TEXT," + \
                "PRIMARY KEY (id)" + \
                ") ENGINE=MyISAM DEFAULT CHARSET=utf8"
        self.db.dsquery.ExecuteQuery(query)

        self.drop_indexes()
        self.create_indexes()

    def drop_tables(self):
        query = "DROP TABLE IF EXISTS gmane_events"
        self.cursor.execute(query)

    def get_indexes(self):
        return (self.TableIndex('gmanesubject', 'gmane_events', 'title'),
                self.TableIndex('gmanecreation', 'gmane_events', 'created'))

    def download_events(self, events_file):

        # http://search.gmane.org/nov.php?query=centos
        # &sort=date&HITSPERPAGE=999
        limit = 100  # max 999
        url = "http://search.gmane.org/nov.php?query="+self.keyword
        url += "&sort=date"
        url += "&HITSPERPAGE="+str(limit)
        article_url = 'http://article.gmane.org/'

        cache_file = "data/gmane_cache.csv"

        if not os.path.isfile(cache_file):
            import requests
            r = requests.get(url, verify=False,
                             headers={'user-agent': 'scout'})
            data = r.text
            with codecs.open(cache_file, 'w', encoding='utf8') as f:
                f.write(data)
        with codecs.open(cache_file, 'r', encoding='utf8') as f:
            data = f.readlines()
            import re
            for cdata in data:
                fields = re.split(r'\t+', cdata)
                # counter,subject,author,date,gmane_id,score
                if len(fields) < 5:
                    continue
                gmane_id = fields[4].replace("Xref: search ", "")
                title = fields[1]
                created = fields[3]
                # http://bugs.python.org/issue6641: removed timezone +0000
                created = created[:-6]
                created = datetime.strptime(created, '%a, %d %b %Y %H:%M:%S')
                created = created.strftime('%Y-%m-%d %H:%M:%S')
                # http://article.gmane.org/gmane.comp.apache.tika.devel
                # /16806/match=centos
                url = article_url+gmane_id.replace(":", "/")
                url += "/match=" + self.keyword
                author = fields[2]
                body = ''  # NOV output does not include body
                self.insert_event(gmane_id, title, created, url, author, body)

    def insert_event(self, gmane_id, title, created, url, author, body):
        # fields not included in CSV file
        fields = ['gmane_id', 'title', 'created', 'url', 'author', 'body']
        query = "INSERT INTO gmane_events ("
        for field in fields:
            query += field + ","
        query = query[:-1]
        query += ") "
        query += "VALUES ("
        title = title.replace("'", "\\'")
        values = "','".join([gmane_id, title, created, url, author, body])
        values = "'"+values+"'"
        # Convert to Unicode to support unicode values
        query = u' '.join((query, values, ")")).encode('utf-8')

        self.db.dsquery.ExecuteQuery(query)
        self.db.conn.commit()

    def get_events(self):
        table = "gmane_events"
        # Common fields for all events: date, summmary, url
        q = "SELECT url, created as date, title as summary, body, author"
        q += " FROM " + table
        q += " ORDER BY date DESC "
        return self.db.dsquery.ExecuteQuery(q)
