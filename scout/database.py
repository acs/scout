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
from scout.utils import DSQuery

# Tuple for managing table indexes
TableIndex = namedtuple('TableIndex', 'name table field')


class Database(object):
    """ Utils for accessing database in Scout. Currently MySQL oriented """

    def __init__(self, dbuser, dbpassword, dbname):
        """ Configure params for accessing the database """
        self.dbuser = dbuser
        self.dbpassword = dbpassword
        self.dbname = dbname
        self.conn = None

    def create_db(self, name):
        """ Create a new database """
        conn = MySQLdb.Connect(host="127.0.0.1",
                               port=3306,
                               user=self.dbuser,
                               passwd=self.dbpassword)
        cursor = conn.cursor()
        query = "CREATE DATABASE " + name + " CHARACTER SET utf8"
        cursor.execute(query)
        conn.close()
        # logging.info(name+" created")

    def drop_db(self, name):
        """ Remove the database """
        conn = MySQLdb.Connect(host="127.0.0.1",
                               port=3306,
                               user=self.dbuser,
                               passwd=self.dbpassword)
        cursor = conn.cursor()
        query = "DROP DATABASE IF EXISTS " + name
        cursor.execute(query)
        conn.close()
        # logging.info(name+" dropped")

    def open_database(self, cleandb = True):
        """ Open the database, creating it if not exists """
        try:
            if cleandb:
                self.drop_db(self.dbname)
                self.create_db(self.dbname)

            conn = MySQLdb.Connect(host="127.0.0.1",
                                   port=3306,
                                   user=self.dbuser,
                                   passwd=self.dbpassword,
                                   db=self.dbname)
            self.conn = conn
            self.cursor = self.conn.cursor()
            self.dsquery = DSQuery(self.dbuser,
                                   self.dbpassword, self.dbname)
        except:
            logging.error(self.dbname + " does not exists")
            self.create_db(self.dbname)
            self.open_database()

    def close_database(self):
        """ Close the connection to the database """
        self.conn.close()
