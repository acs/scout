# -*- coding: utf-8 -*-
#
# Database storage module
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

from scout.datasource import DataSource


class Stackoverflow(DataSource):
    """ Get events from Stackoverflow using the Stackexchange API """

    def create_tables(self):
        """ The name of the fields are the same than CSV from Data Explorer """
        query = "CREATE TABLE IF NOT EXISTS stackoverflow_events (" + \
                "id int(11) NOT NULL AUTO_INCREMENT," + \
                "Post_Link VARCHAR(255) NULL," + \
                "DisplayName VARCHAR(255) NULL," + \
                "title VARCHAR(255) NULL," + \
                "tags TEXT NULL," + \
                "CreationDate DATETIME NOT NULL," + \
                "LastActivityDate DATETIME," + \
                "LastEditDate DATETIME," + \
                "ClosedDate DATETIME," + \
                "PostTypeId int(11) NOT NULL," + \
                "AnswerCount int(11)," + \
                "ViewCount int(11)," + \
                "Score int(11)," + \
                "User_Link VARCHAR(255) NULL," + \
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
                                'CreationDate'))

    def download_events(self, events_file):
        return self._load_csv_file(events_file, self.db, "stackoverflow")

    def insert_event(self, event, fields):
        query = "INSERT INTO stackoverflow_events ("
        for field in fields:
            query += field.replace(" ", "_") + ","
        query = query[:-1]
        query += ") "
        query += "VALUES ("
        # Convert to Unicode to support unicode values
        # query = u' '.join((query, event, ")")).encode('utf-8')
        query = query + event + ")"
        self.db.dsquery.ExecuteQuery(query)
        self.db.conn.commit()

    def get_events(self):
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
        return self.db.dsquery.ExecuteQuery(q)
