# -*- coding: utf-8 -*-
#
# Utils for Scout (misc stuff)
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
import MySQLdb


# Simplified from vizgrimoire.metrics.DSQuery in GrimoireLib
class DSQuery(object):
    """ Generic methods to control access to db """

    db_conn_pool = {}  # one connection per database

    def __init__(self, user, password, database,
                 identities_db=None, projects_db=None,
                 host="127.0.0.1", port=3306, group=None):
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        self.group = group
        if database in DSQuery.db_conn_pool:
            db = DSQuery.db_conn_pool[database]
        else:
            db = self.__SetDBChannel__(user, password, database, host,
                                       port, group)
            DSQuery.db_conn_pool[database] = db
        self.cursor = db.cursor()
        self.cursor.execute("SET NAMES 'utf8'")

        db = self.__SetDBChannel__(user, password, database, host, port, group)

        self.create_indexes()

    def create_indexes(self):
        """ Basic indexes used in each data source """
        pass

    def __SetDBChannel__(self, user=None, password=None, database=None,
                         host="127.0.0.1", port=3306, group=None):

        if group is None:
            db = MySQLdb.connect(user=user, passwd=password,
                                 db=database, host=host, port=port)
        else:
            db = MySQLdb.connect(read_default_group=group, db=database)

        return db

    def ExecuteQuery(self, sql):
        if sql is None:
            return {}
        # print sql
        result = {}
        self.cursor.execute(sql)
        rows = self.cursor.rowcount
        columns = self.cursor.description

        if columns is None:
            return result

        for column in columns:
            result[column[0]] = []
        if rows > 1:
            for value in self.cursor.fetchall():
                for (index, column) in enumerate(value):
                    result[columns[index][0]].append(column)
        elif rows == 1:
            value = self.cursor.fetchone()
            for i in range(0, len(columns)):
                result[columns[i][0]] = value[i]
        return result


# Simplified from vizgrimoire.GrimoireUtils in GrimoireLib
def convertDatetime(data):
    if (isinstance(data, dict)):
        for key in data:
            if (isinstance(data[key], datetime)):
                data[key] = str(data[key])
            elif (isinstance(data[key], list)):
                data[key] = convertDatetime(data[key])
            elif (isinstance(data[key], dict)):
                data[key] = convertDatetime(data[key])
    if (isinstance(data, list)):
        for i in range(0, len(data)):
            if (isinstance(data[i], datetime)):
                data[i] = str(data[i])
    return data


# Simplified from vizgrimoire.GrimoireUtils in GrimoireLib
def createJSON(data, filepath):
    checked_data = convertDatetime(data)
    json_data = json.dumps(checked_data, sort_keys=True)
    json_data = json_data.replace('NaN', '"NA"')
    jsonfile = open(filepath, 'w')
    jsonfile.write(json_data)
    jsonfile.close()
    return
