# -*- coding: utf-8 -*-
#
# Github backend for scout
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

import json
from scout.datasource import DataSource


class Github(DataSource):
    """ Get events from github using the events API and github archive """

    def create_tables(self):
        """ The name of the fields are the same than Big Query tables  """
        # type,repo_name,repo_url,created_at,payload
        query = "CREATE TABLE IF NOT EXISTS github_events (" + \
                "id int(11) NOT NULL AUTO_INCREMENT," + \
                "type varchar(32)," + \
                "repo_name VARCHAR(255) NULL," + \
                "repo_url VARCHAR(255) NULL," + \
                "payload TEXT NULL," + \
                "created_at DATETIME NOT NULL," + \
                "actor_url VARCHAR(255) NULL," + \
                "body TEXT NULL," + \
                "status VARCHAR(32) NULL," + \
                "PRIMARY KEY (id)" + \
                ") ENGINE=MyISAM DEFAULT CHARSET=utf8"
        self.db.dsquery.ExecuteQuery(query)

        self.drop_indexes()
        self.create_indexes()

    def drop_tables(self):
        query = "DROP TABLE IF EXISTS github_events"
        self.db.dsquery.ExecuteQuery(query)

    def get_indexes(self):
        return (self.TableIndex('ghrepo', 'github_events', 'repo_name'),
                self.TableIndex('ghcreation', 'github_events', 'created_at'))

    def download_events(self, events_file):
        return self._load_csv_file(events_file, self.db, "github")

    def insert_event(self, event, fields):
        from datetime import datetime
        # type,repo_name,repo_url,created_at,actor_url,payload
        status = None  # for pull requests, issues ...
        body = ''  # body data for the event
        event_data = event[:-1].split(",", 5)
        timestamp = int(float(event_data[3]))
        # url  https://api.github.com/repos/mahiso/ArduinoCentOS7
        # should be changed to https://github.com/mahiso/ArduinoCentOS7
        event_data[2] = event_data[2].replace("api.", "").replace("repos/", "")
        event_data[3] = \
            datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        # author should be changed to https://github.com/user_id
        event_data[4] = event_data[4].replace("api.", "").replace("users/", "")
        # Work with payload
        payload = event_data[5][:-1][1:]
        payload = payload.replace('""', '"')
        payload = json.loads(payload)
        all_types = ["PushEvent", "CreateEvent", "IssuesEvent", "WatchEvent",
                     "ForkEvent", "DeleteEvent",
                     "PullRequestEvent", "IssueCommentEvent", "GollumEvent",
                     "CommitCommentEvent", "ReleaseEvent", "MemberEvent"]
        types_on = ["CreateEvent", "PullRequestEvent"]
        if event_data[0] not in types_on:
            # Don't register not active events
            return
        if event_data[0] == "CreateEvent" and \
                payload['ref_type'] != "repository":
            # Store just create repository events
            return
        event_data[5] = event_data[5].replace("'", "\\'")
        if event_data[0] == "CreateEvent":
            body = payload['description']
        elif event_data[0] == "PullRequestEvent":
            status = payload['pull_request']['state']
            if payload['pull_request']['title'] is not None:
                body += payload['pull_request']['title'] + "\n"
            if payload['pull_request']['body'] is not None:
                body += payload['pull_request']['body']
            event_data[2] = payload['pull_request']['html_url']
        event = "','".join(event_data)
        event = "'" + event + "'"
        query = "INSERT INTO github_events ("
        for field in fields:
            query += field.replace(" ", "_") + ","
        query = query[:-1]  # remove last ,
        # Add body depending in the type of event
        if body is not None:
            query += ", body"
            body = body.replace("'", "\\'")
            # Convert to Unicode to support unicode values
            event = unicode(event)
            # body = unicode(body)
            # event = u' '.join((event, ",'", body,"'")).encode('utf-8')
            event += ",'" + body + "'"
        if status is not None:
            query += ", status"
            event += ",'"+status+"'"
        query += ") "
        query += "VALUES ("
        # Convert to Unicode to support unicode values
        query = u' '.join((query, event, ")")).encode('utf-8')
        self.db.dsquery.ExecuteQuery(query)
        self.db.conn.commit()

    def get_events(self):
        table = "github_events"
        # Common fields for all events: date, summmary, url
        q = "SELECT repo_url as url, created_at as date, " + \
            "repo_name as summary, type, body, status, actor_url as author "
        q += " FROM " + table
        q += " ORDER BY date DESC "
        if self.limit is not None:
            q += " LIMIT  " + self.limit

        return self.db.dsquery.ExecuteQuery(q)
