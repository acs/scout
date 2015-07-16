# -*- coding: utf-8 -*-
#
# Grimoire Mailman backend for scout
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


class Mail(DataSource):
    """ Get events from Grimoire Mailman data source """

    def create_tables(self):
        query = "CREATE TABLE IF NOT EXISTS mail_events (" + \
                "id int(11) NOT NULL AUTO_INCREMENT," + \
                "message_id varchar(255)," + \
                "subject varchar(255)," + \
                "sent_at DATETIME NOT NULL," + \
                "url varchar(255)," + \
                "mailing_list varchar(255)," + \
                "author varchar(255)," + \
                "body TEXT," + \
                "PRIMARY KEY (id)" + \
                ") ENGINE=MyISAM DEFAULT CHARSET=utf8"
        self.db.dsquery.ExecuteQuery(query)

        self.drop_indexes()
        self.create_indexes()

    def drop_tables(self):
        query = "DROP TABLE IF EXISTS mail_events"
        self.db.dsquery.ExecuteQuery(query)

    def get_indexes(self):
        return (self.TableIndex('mailsubject', 'mail_events', 'subject'),
                self.TableIndex('mailcreation', 'mail_events', 'sent_at'))

    def download_events(self, events_file):
        return self._load_csv_file(events_file, self.db, "mail")

    def insert_event(self, event, fields):
        # fields not included in CSV file
        fields = ['message_id', 'subject', 'sent_at', 'author',
                  'mailing_list', 'body']
        # Add now url. In CSV file we have the URL for the mailing lists.
        fields = ['url'] + fields
        # url not included in the event
        event_data = event.split(",", 5)
        from urllib import quote
        subject = event_data[1]
        url = "https://www.google.com/search?q="+quote(subject)
        event = '"'+url+'"'+','+event
        query = "INSERT INTO mail_events ("
        for field in fields:
            query += field + ","
        query = query[:-1]
        query += ") "
        query += "VALUES ("
        # Convert to Unicode to support unicode values
        # query = u' '.join((query, event, ")")).encode('utf-8')
        if event[-2:] == '\\"':
            event = event.replace('\\"', '\\ "')
        query = query + event + ")"

        self.db.dsquery.ExecuteQuery(query)
        self.db.conn.commit()

    def get_events(self):
        table = "mail_events"
        # Common fields for all events: date, summmary, url
        q = "SELECT url, sent_at as date, subject as summary, body, author "
        q += " FROM " + table
        q += " ORDER BY date DESC "
        return self.db.dsquery.ExecuteQuery(q)
