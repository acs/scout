# -*- coding: utf-8 -*-
#
# Reddit backend for scout
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


class Reddit(DataSource):
    """ Get events from https://www.reddit.com/ using the search API at
    https://www.reddit.com/search.json?q=<keyword>&sort=top
    """

    def create_tables(self):
        query = "CREATE TABLE IF NOT EXISTS reddit_events (" + \
                "id int(11) NOT NULL AUTO_INCREMENT," + \
                "reddit_id varchar(255)," + \
                "title varchar(255)," + \
                "created DATETIME NOT NULL," + \
                "url varchar(255)," + \
                "author varchar(255)," + \
                "body TEXT," + \
                "score int(11)," + \
                "likes int(11), " + \
                "num_comments int(11), " + \
                "PRIMARY KEY (id)" + \
                ") ENGINE=MyISAM DEFAULT CHARSET=utf8"
        self.db.dsquery.ExecuteQuery(query)

        self.drop_indexes()
        self.create_indexes()

    def drop_tables(self):
        query = "DROP TABLE IF EXISTS reddit_events"
        self.cursor.execute(query)

    def get_indexes(self):
        return (self.TableIndex('redditsubject', 'reddit_events', 'title'),
                self.TableIndex('redditcreation', 'reddit_events', 'created'))

    def download_events(self, events_file):
        # Right now only 100 events are gathered. No pagination done.
        # Around two weeks in centos

        # https://www.reddit.com/search.json?q=centos&sort=new
        limit = 100  # max 100
        url = "https://www.reddit.com/search.json?q="+self.keyword
        url += "&sort=new"
        url += "&limit="+str(limit)

        cache_file = "data/reddit_cache.json"

        if not os.path.isfile(cache_file):
            import requests
            r = requests.get(url, verify=False,
                             headers={'user-agent': 'scout'})
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
            self.insert_event(reddit_id, title, created, url, author,
                              body, score, likes, ncomments)

    def insert_event(self, reddit_id, title, created,
                     url, author, body, score, likes, ncomments):
        # fields not included in CSV file
        fields = ['reddit_id', 'title', 'created', 'url', 'author', 'body']
        fields += ['score', 'likes', 'num_comments']
        query = "INSERT INTO reddit_events ("
        for field in fields:
            query += field + ","
        query = query[:-1]
        query += ") "
        query += "VALUES ("
        body = body.replace("'", "\\'")
        title = title.replace("'", "\\'")
        values = "','".join([reddit_id, title, created, url, author,
                             body, str(score), str(likes), str(ncomments)])
        values = "'"+values+"'"
        # Convert to Unicode to support unicode values
        query = u' '.join((query, values, ")")).encode('utf-8')

        self.db.dsquery.ExecuteQuery(query)
        self.db.conn.commit()

    def get_events(self):
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
        return self.db.dsquery.ExecuteQuery(q)
