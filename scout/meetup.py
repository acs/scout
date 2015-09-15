# -*- coding: utf-8 -*-
#
# Meetup backend for scout
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
import requests
import traceback


from scout.datasource import DataSource


class Meetup(DataSource):
    """ Get events from groups using https://secure.meetup.com/meetup_api
    """

    def create_tables(self):
        query = "CREATE TABLE IF NOT EXISTS meetup_events (" + \
                "id int(11) NOT NULL AUTO_INCREMENT," + \
                "meetup_id varchar(255)," + \
                "title varchar(255)," + \
                "created DATETIME NOT NULL," + \
                "url varchar(255)," + \
                "author varchar(255)," + \
                "body TEXT," + \
                "score int(11)," + \
                "yes_rsvp_count int(11), " + \
                "status varchar(255), " + \
                "PRIMARY KEY (id)" + \
                ") ENGINE=MyISAM DEFAULT CHARSET=utf8"
        self.db.dsquery.ExecuteQuery(query)

        self.drop_indexes()
        self.create_indexes()

    def drop_tables(self):
        query = "DROP TABLE IF EXISTS meetup_events"
        self.cursor.execute(query)

    def get_indexes(self):
        return (self.TableIndex('meetupsubject', 'meetup_events', 'title'),
                self.TableIndex('meetupcreation', 'meetup_events', 'created'))

    def download_events(self):
        # Get the groups for the keywords selected
        # Get as events all activities in this groups

        # https://api.meetup.com/find/groups?&sign=true&photo-host=public
        # &text=centos&radius=global&page=20
        url = "https://api.meetup.com"
        url += "/find/groups"
        url += "?radius=global"
        url += "&key="+self.key
        # url += "&page=20"

        # the cache file includes all groups and the events
        cache_file = "data/meetup_groups_cache-"
        cache_file += ",".join(self.keywords)+".json"

        if not os.path.isfile(cache_file):
            groups = []
            # We need a specific query for each keyword and then join results
            for keyword in self.keywords:
                events = {}
                kurl = url + "&text="+keyword
                r = requests.get(kurl, verify=False,
                                 headers={'user-agent': 'scout'})
                if r.status_code == 401:
                    logging.error("Not authorized API key for Meetup")
                    return

                groups += r.json()

            # Now we need to get all events for groups

            for group in groups:
                logging.info("Getting events for group: " + group['name'])
                url = "https://api.meetup.com"
                url += "/2/events?"
                url += "&group_id="+str(group['id'])
                url += "&status=upcoming,past"
                url += "&key="+self.key
                url += "&order=time"
                r = requests.get(url, verify=False,
                                 headers={'user-agent': 'scout'})
                events_data = r.json()
                # print (events_data)
                events[group['name']] = events_data

            f = open(cache_file, 'w')
            f.write(json.dumps({"groups": groups, "events": events}))
            f.close()

        with open(cache_file) as f:
            raw_data = f.read()
            try:
                data = json.loads(raw_data)
            except:
                logging.error("Wrong JSON received in Meetup")
                logging.info("Data: " + raw_data)
                logging.info("Cache file used: " + cache_file)
                traceback.print_exc()
                return

        for group in data['events']:
            gevents = data['events'][group]
            for event in gevents['results']:

                try:
                    meetup_id = event['id']
                    title = event['name']
                    created = datetime.fromtimestamp(event['created']/1000)
                    created = created.strftime('%Y-%m-%d %H:%M:%S')
                    url = event['event_url']
                    author = event['group']['urlname']
                    if 'description' in event:
                        body = event['description']
                    else:
                        body = ''
                    if 'rating' in event:
                        score = event['rating']['average']
                    else:
                        score = 0  # hack: it should be NULL in MySQL
                    yes_rsvp_count = event['yes_rsvp_count']
                    status = event['status']
                    self.insert_event(meetup_id, title, created, url,
                                      author, body, score, yes_rsvp_count,
                                      status)
                except:
                    logging.error("Error processing meetup event")
                    logging.error(event)
                    traceback.print_exc()

    def insert_event(self, meetup_id, title, created,
                     url, author, body, score, yes_rsvp_count, status):
        # fields not included in CSV file
        fields = ['meetup_id', 'title', 'created', 'url', 'author', 'body']
        fields += ['score', 'yes_rsvp_count', 'status']
        query = "INSERT INTO meetup_events ("
        for field in fields:
            query += field + ","
        query = query[:-1]
        query += ") "
        query += "VALUES ("
        body = body.replace("'", "\\'")
        title = title.replace("'", "\\'")
        values = "','".join([meetup_id, title, created, url, author,
                             body, str(score), str(yes_rsvp_count),
                             str(status)])
        values = "'"+values+"'"
        # Convert to Unicode to support unicode values
        query = u' '.join((query, values, ")")).encode('utf-8')

        self.db.dsquery.ExecuteQuery(query)
        self.db.conn.commit()

    def get_events(self):
        table = "meetup_events"
        url_meetup = "https://www.meetup.com/"
        # Common fields for all events: date, summmary, url
        q = "SELECT url, created as date, title as summary, body, "
        q += "CONCAT('"+url_meetup+"',author) as author, "
        q += "score, yes_rsvp_count, status"
        q += " FROM " + table
        q += " ORDER BY date DESC "
        if self.limit is not None:
            q += " LIMIT  " + self.limit

        return self.db.dsquery.ExecuteQuery(q)
