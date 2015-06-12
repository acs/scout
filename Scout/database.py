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
#   Santiago Dueñas <sduenas@bitergia.com>
#
#

import logging
import MySQLdb
from collections import namedtuple
import json

# Tuple for managing table indexes
TableIndex = namedtuple('TableIndex', 'name table field')


class Database(object):

    INDEXES_stackoverflow = (TableIndex('sotitle', 'stackoverflow_events',
                                        'title'),
                             TableIndex('socreation', 'stackoverflow_events',
                                        'CreationDate'))
    INDEXES_github = (TableIndex('ghrepo', 'github_events', 'repo_name'),
                      TableIndex('ghcreation', 'github_events', 'created_at'))
    INDEXES_mail = (TableIndex('mailsubject', 'mail_events', 'subject'),
                    TableIndex('mailcreation', 'mail_events', 'sent_at'))

    def __init__(self, myuser, mypassword, mydb):
        self.myuser = myuser
        self.mypassword = mypassword
        self.mydb = mydb
        self.conn = None

    def create_db(self, name):
        conn = MySQLdb.Connect(host="127.0.0.1",
                               port=3306,
                               user=self.myuser,
                               passwd=self.mypassword)
        cursor = conn.cursor()
        query = "CREATE DATABASE " + name + " CHARACTER SET utf8"
        cursor.execute(query)
        conn.close()
        logging.info(name+" created")

    def open_database(self):
        try:
            conn = MySQLdb.Connect(host="127.0.0.1",
                                   port=3306,
                                   user=self.myuser,
                                   passwd=self.mypassword,
                                   db=self.mydb)
            self.conn = conn
            self.cursor = self.conn.cursor()
        except:
            logging.error(self.mydb + " does not exists")
            self.create_db(self.mydb)
            self.open_database()

    def close_database(self):
        self.conn.close()

    # Management functions
    def create_tables_stackoverflow(self):
        """ The name of the fields are the same than CSV from Data Explorer """
        query = "CREATE TABLE IF NOT EXISTS stackoverflow_events (" + \
                "id int(11) NOT NULL AUTO_INCREMENT," + \
                "Post_Link VARCHAR(255) NULL," + \
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
        self.cursor.execute(query)

        self.drop_indexes("stackoverflow")
        self.create_indexes("stackoverflow")

    # Management functions
    def create_tables_github(self):
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
        self.cursor.execute(query)

        self.drop_indexes("github")
        self.create_indexes("github")

    # Management functions
    def create_tables_mail(self):
        # type,repo_name,repo_url,created_at,payload
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
        self.cursor.execute(query)

        self.drop_indexes("mail")
        self.create_indexes("mail")

    def drop_tables_stackoverflow(self):
        query = "DROP TABLE IF EXISTS stackoverflow_events"
        self.cursor.execute(query)

    def drop_tables_github(self):
        query = "DROP TABLE IF EXISTS github_events"
        self.cursor.execute(query)

    def drop_tables_mail(self):
        query = "DROP TABLE IF EXISTS mail_events"
        self.cursor.execute(query)

    def create_indexes(self, backend="stackoverflow"):
        if backend == "stackoverflow":
            indexes = Database.INDEXES_stackoverflow
        elif backend == "github":
            indexes = Database.INDEXES_github
        elif backend == "mail":
            indexes = Database.INDEXES_mail
        else:
            return
        for idx in indexes:
            try:
                query = "CREATE INDEX %s ON %s (%s);" % (idx.name,
                                                         idx.table, idx.field)
                self.cursor.execute(query)
                self.conn.commit()
            except MySQLdb.Error as e:
                print("Warning: Creating %s index" % idx.name, e)

    def drop_indexes(self, backend="stackoverflow"):
        if backend == "stackoverflow":
            indexes = Database.INDEXES_stackoverflow
        elif backend == "github":
            indexes = Database.INDEXES_github
        elif backend == "mail":
            indexes = Database.INDEXES_mail
        else:
            return

        for idx in indexes:
            try:
                query = "DROP INDEX %s ON %s;" % (idx.name, idx.table)
                self.cursor.execute(query)
                self.conn.commit()
            except MySQLdb.Error as e:
                print("Warning: Dropping %s index" % idx.name, e)

    def stackoverflow_insert_event(self, event, fields):
        query = "INSERT INTO stackoverflow_events ("
        for field in fields:
            query += field.replace(" ", "_") + ","
        query = query[:-1]
        query += ") "
        query += "VALUES ("
        # Convert to Unicode to support unicode values
        # query = u' '.join((query, event, ")")).encode('utf-8')
        query = query + event + ")"
        self.cursor.execute(query)
        self.conn.commit()

    def github_insert_event(self, event, fields):
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
        self.cursor.execute(query)
        self.conn.commit()

    def mail_insert_event(self, event):
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

        self.cursor.execute(query)
        self.conn.commit()
