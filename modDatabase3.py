# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 00:17:06 2019

@author: LIM YUAN QING
"""

import pyodbc
import itertools
import datetime
import enum

import modUtils3 as utils

@enum.unique
class ENUM_DATABASE_TYPE(enum.Enum):
    ACCESS = 1
    POSTGRE = 2

@enum.unique
class ENUM_QUERY_TYPE(enum.Enum):
    CREATE = 1
    READ = 2
    UPDATE = 3
    DELETE = 4

class Database():
    """
    Each instance of the Database object represents a database connection.
        
    Parameters
    ----------
    enum_database_type : ENUM_DATABASE_TYPE
        Enumeraton representing the type of database to connect to
            ENUM_DATABASE_TYPE.ACCESS
            ENUM_DATABASE_TYPE.POSTGRE
    str_database : string
        Full path of database, including its name and file extension
    str_user_name : string
        Database username
    str_password : string
        Database password
    str_server : string
        IP address of serving hosting the database
    int_port : integer
        Port to connect to
    """
    
    __int_count = 0
    def __init__(self, 
                 enum_database_type,
                 str_database, 
                 str_user_name = None, 
                 str_password = None,
                 str_server = None,
                 int_port = None):
        self.__enum_database_type = enum_database_type
        self.__str_database = str_database
        self.__str_user_name = str_user_name
        self.__str_password = str_password
        self.__str_server = str_server
        self.__int_port = int_port
        self.__obj_conn = None
        Database.__int_count += 1
                
    def __del__(self):
        if self.__obj_conn != None:
            self.__obj_conn.close()
        Database.__int_count -= 1
        
    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                str(self.__enum_database_type) + ',"' +
                str(self.__str_database) + '",' +
                str(self.__str_user_name) + ',' +
                str(self.__str_password) + ',' +
                str(self.__str_server) + ',' +
                str(self.__int_port) + ')')
        
    def __str__(self):
        if self.__enum_database_type == ENUM_DATABASE_TYPE.ACCESS:
            str_output = ('''
            ==================================================
            Database #{int_count}
            Database Type: {enum_database_type}
            Database Path: {str_database}
            User: {str_user_name}
            ==================================================
            ''').format(int_count = Database.__int_count,
                        enum_database_type = self.__enum_database_type.name,
                        str_database = self.__str_database,
                        str_user_name = self.__str_user_name)
        elif self.__enum_database_type == ENUM_DATABASE_TYPE.POSTGRE:
            str_output = ('''
            ==================================================
            Database #{int_count}
            Database: {enum_database_type}
            Database: {str_database}
            User: {str_user_name}
            IP Address: {str_server}
            Port: {int_port}
            ==================================================
            ''').format(int_count = Database.__int_count,
                        enum_database_type = self.__enum_database_type.name,
                        str_database = self.__str_database,
                        str_user_name = self.__str_user_name,
                        str_server = self.__str_server,
                        int_port = self.__int_port
                        )        
        
        return str_output
    
    def __len__(self):
        pass

    def start_conn(self):
        """
        Start pyodbc database connection.
           
        Returns
        -------
        connection
            Connection object
        """
        if self.__enum_database_type == ENUM_DATABASE_TYPE.ACCESS:            
            str_odbc_conn = (('Driver={Microsoft Access Driver (*.mdb, *.accdb)};' +  
                                'DBQ={database}; UID={username}; PWD={password}').format(
                            database=self.__str_database, 
                            username=self.__str_user_name, 
                            password=self.__str_password 
                            ))
            try:
                self.__obj_conn = pyodbc.connect(str_odbc_conn)
                return True
            except:
                return False
        elif self.__enum_database_type == ENUM_DATABASE_TYPE.POSTGRE:
            bit = utils.is_32_bit()*'86' + utils.is_64_bit()*'64'
            str_driver = 'DRIVER={PostgreSQL Unicode(x' + bit + ')}; '
            str_odbc_conn = (str_driver + ('SERVER={server}; PORT={port}; '+
                                'DATABASE={database}; UID={username}; ' +
                                'PWD={password}').format(
                            database=self.__str_database, 
                            username=self.__str_user_name, 
                            password=self.__str_password,
                            server = self.__str_server,
                            port = self.__int_port
                            ))            
#        return pyodbc.connect(str_odbc_conn)
#            import psycopg2 as pg2
#            try:
#                self.__obj_conn = pg2.connect(database=self.__str_database, 
#                                   user=self.__str_user_name,
#                                   password=self.__str_password,
#                                   host=self.__str_server, 
#                                   port=self.__int_port)
            try:
                self.__obj_conn = pyodbc.connect(str_odbc_conn)
                return True
            except:
                return False
            
    
    def get_cursor(self):
        """
        Get pyodbc cursor.
        
        Parameters
        ----------
        conn : Connection
            pyodbc Connection object
            
        Returns
        -------
        cursor
            pyodbc Cursor object    
        """
        return self.__obj_conn.cursor()
    
    def gen_insert_query(self, str_table_name, 
                         lst_header_names):
        """
        Helper function to generate insert statement.
        
        Parameters
        ----------
        str_table_name : string
            Database table name
        lst_header_names : list
            List of strings representing column headers of `str_table_name` Database
            table
        
        Returns
        -------
        string
            SQL statement to insert data
        """
        if self.__enum_database_type == ENUM_DATABASE_TYPE.ACCESS:
            str_header_names = ''.join('[' + name + '], ' for name in lst_header_names)[:-2]
        elif self.__enum_database_type == ENUM_DATABASE_TYPE.POSTGRE:
            str_header_names = ''.join('"' + name + '", ' for name in lst_header_names)[:-2]
        
        return ('INSERT INTO ' + str_table_name + ' (' + str_header_names + ') VALUES (' + 
                ('?, '*len(lst_header_names))[:-2] + ')')
    
    def log_transaction(self, 
                        cursor, 
                        str_table_name, 
                        *args):
        """
        Function to log a Database transaction and return value of primary key of 
        `str_table_name` Database table.
        
        Parameeters
        -----------
        cursor : cursor
            pyodbc Cursor object
        str_table_name : string
            Database table name
        *args : object
            variable arguments of types corresponding to data types of columns in
            `str_table_name` Database table
        
        Returns
        -------
        int
            primary key of `str_table_name` Database table for transaction that was 
            performed
        """
        header_names = self.get_table_header(cursor, str_table_name)[0][1:]
        str_query = self.gen_insert_query(str_table_name, header_names)
        lst_values = args
        primary_key = self.execute_query(cursor, str_query, lst_values)
        return primary_key
    
    def execute_query(self, 
                      cursor, 
                      str_query, 
                      lst_values = None, 
                      enum_query_type = ENUM_QUERY_TYPE.UPDATE):
        try:
            if lst_values == None:
                cursor.execute(str_query)
            else:
                cursor.execute(str_query, lst_values)
        except:
            return False
        
        if enum_query_type == ENUM_QUERY_TYPE.CREATE:
            primary_key = True
        elif enum_query_type == ENUM_QUERY_TYPE.READ:
            primary_key = True
        elif enum_query_type == ENUM_QUERY_TYPE.UPDATE:
            cursor.execute('SELECT @@IDENTITY')
            primary_key = cursor.fetchone()[0]
        elif enum_query_type == ENUM_QUERY_TYPE.DELETE:
            primary_key = True
            
        cursor.commit()
        return primary_key
    
    def get_foreign_key(self, 
                        cursor, 
                        str_unique_value, 
                        str_table_name, 
                        str_primary_col_name, 
                        str_foreign_col_name):
        str_table_name_new = str_table_name + '.[' + str_primary_col_name + ']'
        str_condition = str_unique_value
        str_query = 'SELECT {} FROM {} WHERE {} = ?;'.format(str_foreign_col_name,
                            str_table_name, str_table_name_new)
        cursor.execute(str_query, str_condition)
        row = cursor.execute(str_query, [str_condition]).fetchone()
        if row:
            return row[0]
        else:
            return None
    
    def get_table_header(self,
                         cursor, 
                         str_table_name):
        cursor.execute('SELECT * FROM ' + str_table_name)
        header = [[col_name[0], str(col_name[1]).split()[1][1:-2]] for col_name in cursor.description]
        return list(map(list, itertools.zip_longest(*header)))
    
    def close(self):
        try:
            self.__obj_conn.close()
            self.__obj_conn = None
            return True
        except:
            return False

if __name__ == '__main__':
#    Test codes for work   

#    DB_PATH = r'T:/Equity Warehousing/1. Trading/3. Data/1. Database/Warehousing.accdb'
#    DB_USER = ''
#    DB_PASSWORD = ''
#    ODBC_CONN_STR = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)}; DBQ=%s; UID=%s; PWD=%s' %\
#                        (DB_PATH, DB_USER, DB_PASSWORD)
#    conn = start_conn(DB_PATH, DB_USER, DB_PASSWORD)
#    cursor = get_cursor(conn)
#    try:
#        print(get_table_header(cursor, 'tblLog'))
#        foreign_key = get_foreign_key(cursor, 'tsdlyq', 'tblUsers', 'Username', 'ID')
#        print(foreign_key)
#        print(log_transaction(cursor, 'tblLog', 'tsdlyq', datetime.datetime.today().strftime('%d %b %Y %H:%M'), 'TEST', 'TESTTEST'))
#    finally:
#        conn.close()

#    ==================================================
#    Test codes for personal
    

    
#    conn = pg2.connect(database='dvdrental', user='postgres',password='HelloWorld$1',
#                       host='localhost', port=5432)
#    conn = start_conn(ENUM_DATABASE_TYPE.POSTGRE,
#                      'dvdrental',
#                      'postgres',
#                      'HelloWorld$1',
#                      'localhost',
#                      5432)
#    cur = conn.cursor()
#    cur.execute('SELECT * FROM film;')
#    print(cur.fetchall())
    pass
    