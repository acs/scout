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

import logging, MySQLdb
from collections import namedtuple

# Tuple for managing table indexes
TableIndex = namedtuple('TableIndex', 'name table field')


class Database(object):

    INDEXES = (TableIndex('sotitle', 'stackoverflow_events', 'title'),
               TableIndex('socreation', 'stackoverflow_events', 'CreationDate'))

    def __init__(self, myuser, mypassword, mydb):
        self.myuser = myuser
        self.mypassword = mypassword
        self.mydb = mydb
        self.conn = None

    def open_database(self):
        conn = MySQLdb.Connect(host="127.0.0.1",
                               port=3306,
                               user=self.myuser,
                               passwd=self.mypassword,
                               db=self.mydb)
        self.conn = conn
        self.cursor = self.conn.cursor()

    def close_database(self):
        self.conn.close()

    # Management functions
    def create_tables(self):
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
                "PRIMARY KEY (id)" + \
                ") ENGINE=MyISAM DEFAULT CHARSET=utf8"
        self.cursor.execute(query)

        self.drop_indexes()
        self.create_indexes()

    def drop_tables(self):
        query = "DROP TABLE IF EXISTS stackoverflow_events"
        self.cursor.execute(query)

    def create_indexes(self):
        for idx in Database.INDEXES:
            try:
                query = "CREATE INDEX %s ON %s (%s);" % (idx.name, idx.table, idx.field)
                self.cursor.execute(query)
                self.conn.commit()
            except MySQLdb.Error as e:
                print("Warning: Creating %s index" % idx.name, e)

    def drop_indexes(self):
        for idx in Database.INDEXES:
            try:
                query = "DROP INDEX %s ON %s;" % (idx.name, idx.table)
                self.cursor.execute(query)
                self.conn.commit()
            except MySQLdb.Error as e:
                print("Warning: Dropping %s index" % idx.name, e)

    # Queries (SELECT/INSERT) functions 

    def so_insert_event(self, event, fields):
        query =  "INSERT INTO stackoverflow_events ("
        for field in fields:
            query += field.replace(" ","_")+","
        query = query[:-1]
        query += ") "
        query += "VALUES ("
        # Convert to Unicode to support unicode values
        query = u' '.join((query, event, ")")).encode('utf-8')
        self.cursor.execute(query)
        self.conn.commit()

    def _escape(self, s):
        if not s:
            return None
        try:
            s = self.conn.escape_string(s)
        except UnicodeEncodeError:
            # Don't encode unicode
            pass
        return s
