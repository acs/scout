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

import logging
import traceback
from collections import namedtuple


class DataSource(object):
    """Base class for all Scout data sources

    All data sources implementation should implement the API
    defined in this class in order to be integrated with Scout.
    """

    def __init__(self, db, keywords, limit=None, key=None):
        """
        :param db: scout.database object
        :param keywords: keywords to be searched in the data source
        :param limit: Limit the number of events to be generated
        :param key: API key to be used for auth
        """
        self.db = db
        self.keywords = keywords
        self.limit = limit
        self.key = key
        # user or creating indexes
        self.TableIndex = namedtuple('TableIndex', 'name table field')

    def create_tables(self):
        """Create the tables for storing the events"""

        raise NotImplementedError

    def drop_tables(self):
        """Remove the tables for storing the events"""

        raise NotImplementedError

    def get_indexes(self):
        """ Return indexes definition to improve events
            gathering from database."""

        raise NotImplementedError

    def download_events(self):
        """Download the events from the remote data source

        Normally using http and in JSON format, the data is read from
        the upstream data source and it is stored in the database. """

        raise NotImplementedError

    def get_events(self):
        """Get events from the event table in the database"""

        raise NotImplementedError

    def create_indexes(self):
        """ Create the indexes to improve events gathering from database """

        indexes = self.get_indexes()
        for idx in indexes:
            try:
                query = "CREATE INDEX %s ON %s (%s);" % (idx.name,
                                                         idx.table, idx.field)
                print query
                self.db.dsquery.ExecuteQuery(query)
                self.db.conn.commit()
            except:
                print traceback.format_exc()
                logging.warning("Warning: Creating %s index" % idx.name)

    def drop_indexes(self):
        """ Drop the indexes to improve events gathering from database """

        indexes = self.get_indexes()
        for idx in indexes:
            try:
                query = "DROP INDEX %s ON %s;" % (idx.name, idx.table)
                self.db.dsquery.ExecuteQuery(query)
                self.db.conn.commit()
            except:
                logging.warning("Warning: Dropping %s index" % idx.name)
