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

    def __init__(self, db, keyword, limit=None, key=None):
        """
        :param db: scout.database object
        :param keyword: keyword to be searched in the data source
        :param limit: Limit the number of events to be generated
        :param key: API key to be used for auth
        """
        self.db = db
        self.keyword = keyword
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

    def download_events(self, events_file=None):
        """Download the events from the remote data source

        Normally using http and in JSON format, the data is read from
        the upstream data source and it is stored in the database.

        If events_file is used, the events will come from it."""

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

    def _load_csv_file(self, filepath, db, backend):
        """Load a CSV events file into the database (currently MySQL) """
        import csv
        if backend not in ("stackoverflow", "github", "mail"):
            raise ("Backend not supported: " + backend)
        try:
            # mail csv file is ASCII. The rest is UTF8
            if backend in ["mail", "stackoverflow"]:
                infile = open(filepath, 'rt')
            elif backend in ["github"]:
                import codecs
                infile = codecs.open(filepath, "rt", "utf-8")

        except EnvironmentError as e:
            logging.error("Cannot open %s for reading: %s" % (filepath, e))
            raise

        count_events = 0
        count_events_new = 0
        # last_date = db.get_last_date(channel_id)

        if backend == "github":
            # Don't use CSV module for this format. Not easy to parse with it.
            pass
        elif backend == "mail":
            data = csv.reader(infile, delimiter=',', quotechar='"',
                              escapechar='\\')
        else:
            data = csv.reader(infile, delimiter=',', quotechar='"')

        try:
            fields = None
            if backend in ["mail", "stackoverflow"]:
                for event_data in data:
                    if backend != "mail":
                        # In mail CSV we don't have fields in the first row
                        if fields is None:
                            # first row are the fields names
                            fields = event_data
                            continue
                    # TODO: Loosing " inside the body. To be fixed. Quick hack.
                    event_data = [fevent.replace('"', '')
                                  for fevent in event_data]
                    event_data_str = '"' + '","'.join(event_data) + '"'
                    self.insert_event(event_data_str, fields)
                count_events_new += 1
            elif backend in ["github"]:
                lines = infile.readlines()
                for event_data in lines:
                    if fields is None:
                        # first row are the fields names
                        fields = event_data[:-1].split(",")
                        continue
                    self.insert_event(event_data, fields)

        except Exception as e:
            logging.error("Error parsing %s file: %s" % (filepath, e))
            raise
        finally:
            infile.close()
        return count_events, count_events_new
