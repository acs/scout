# -*- coding: utf-8 -*-
#
# Stackoverflow backend for scout
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

from datetime import datetime
import json
import logging
import os

from scout.datasource import DataSource


class Stackoverflow(DataSource):
    """ Get events from Stackoverflow using the Stackexchange API """

    def create_tables(self):
        """ The name of the fields are the same than CSV from Data Explorer """
        query = "CREATE TABLE IF NOT EXISTS stackoverflow_events (" + \
                "id int(11) NOT NULL AUTO_INCREMENT," + \
                "question_id VARCHAR(255) NOT NULL," + \
                "url VARCHAR(255) NULL," + \
                "author VARCHAR(255) NULL," + \
                "author_url VARCHAR(255) NULL," + \
                "title VARCHAR(255) NULL," + \
                "tags TEXT NULL," + \
                "creation_date DATETIME NOT NULL," + \
                "last_activity_date DATETIME," + \
                "answer_count int(11)," + \
                "view_count int(11)," + \
                "score int(11)," + \
                "owner_link VARCHAR(255) NULL," + \
                "body TEXT," + \
                "PRIMARY KEY (id)" + \
                ") ENGINE=MyISAM DEFAULT CHARSET=utf8"
        self.db.dsquery.ExecuteQuery(query)

        self.drop_indexes()
        self.create_indexes()

    def drop_tables(self):
        query = "DROP TABLE IF EXISTS stackoverflow_events"
        self.db.dsquery.ExecuteQuery(query)

    def get_indexes(self):
        return (self.TableIndex('sotitle', 'stackoverflow_events', 'title'),
                self.TableIndex('socreation', 'stackoverflow_events',
                                'creation_date'))

    def download_events(self):
        # https://api.stackexchange.com/2.2/search?
        # order=desc&sort=creation&intitle=centos
        # &site=stackoverflow&pagesize=100

        limit = 100  # max 100
        url = "https://api.stackexchange.com/2.2/search?"
        url += "&order=desc&sort=creation"
        url += "&site=stackoverflow"
        url += "&pagesize="+str(limit)
        url += "&filter=withbody"

        url_title = url + "&intitle="+self.keyword
        url_tag = url + "&tagged="+self.keyword

        cache_file = "data/stackoverflow_cache-"+self.keyword+".json"

        if not os.path.isfile(cache_file):
            import requests
            r = requests.get(url_title, verify=False,
                             headers={'user-agent': 'scout'})
            data = r.json()
            # r = requests.get(url_tag, verify=False,
            #                 headers={'user-agent': 'scout'})
            # z = x.copy()
            # z.update(y)
            with open(cache_file, 'w') as f:
                f.write(json.dumps(data))
        else:
            with open(cache_file) as f:
                data = json.loads(f.read())

        for question in data['items']:
            # [u'body', u'is_answered', u'view_count', u'tags',
            # u'last_activity_date', u'answer_count', u'creation_date',
            # u'score', u'link', u'owner', u'title', u'question_id']
            question_id = question['question_id']
            title = question['title']
            tags = ",".join(question['tags'])
            creation_date = question['creation_date']
            creation_date = datetime.fromtimestamp(question['creation_date'])
            creation_date = creation_date.strftime('%Y-%m-%d %H:%M:%S')
            body = question['body']
            url = question['link']
            author = question['owner']['display_name']
            author_url = question['owner']['link']
            score = question['score']
            view_count = question['view_count']
            answer_count = question['answer_count']
            self.insert_event(question_id, title, tags, creation_date, body,
                              url, author, author_url, score, view_count,
                              answer_count)

    def insert_event(self, question_id, title, tags, creation_date, body,
                     url, author, author_url, score, view_count, answer_count):
        fields = ['question_id', 'title', 'tags', 'creation_date', 'url']
        fields += ['body', 'author', 'author_url']
        fields += ['score', 'view_count', 'answer_count']
        query = "INSERT INTO stackoverflow_events ("
        for field in fields:
            query += field + ","
        query = query[:-1]
        query += ") "
        query += "VALUES ("
        body = body.replace("'", "\\'")
        title = title.replace("'", "\\'")
        values = "','".join([str(question_id), title, tags, creation_date,
                             url, body, author, author_url, str(score),
                             str(view_count), str(view_count)
                             ])

        values = "'"+values+"'"
        # Convert to Unicode to support unicode values
        query = u' '.join((query, values, ")")).encode('utf-8')

        self.db.dsquery.ExecuteQuery(query)
        self.db.conn.commit()

    def get_events(self):
        table = "stackoverflow_events"
        # Common fields for all events: date, summmary, url
        q = "SELECT url, creation_date as date, title as summary, "
        q += "view_count as views, score, answer_count, "
        q += "body, author_url, author"
        q += " FROM " + table
        q += " ORDER BY date DESC "
        if self.limit is not None:
            q += " LIMIT  " + self.limit
        return self.db.dsquery.ExecuteQuery(q)
