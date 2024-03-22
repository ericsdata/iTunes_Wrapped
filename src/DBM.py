# -*- coding: utf-8 -*-
"""
Created on Sun Dec 13 10:10:40 2020

@author: eachr
"""

import db_ec
import os
import sqlite3


class DBM():
    ''' 
    '''
    
    def __init__(self,targetDB):
        self.targetDB = targetDB
        self.sqls = r'..\SQL'
        created = self.dbExists()
        ## if Database has not been created, create Conn and Tables
        if not created:
            print('Creating Database\n')
            self.createConn()
            self.ExecuteScripts('create')
            
        ## Otherwise just create connection to DB
        else:
            self.createConn()
        
        
        
        
    def dbExists(self):
        """Function tests whether the sqlite database file exists

        Returns:
            ret (bool): binary of result of existence
        """        
        
        if os.path.isfile(self.targetDB):            
            ret = True
            
        else:
            ret = False
        
        print('Database Existence Status:   ' + str(ret))
        return ret
    
    def createConn(self):
        '''
        Function to assign db connection to DBM obect
        '''
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.targetDB)
            self.cur = self.conn.cursor()
 
        except sqlite3.Error as e:
            print(e)
            
 
        
    def ExecuteScripts(self, sql_sub_folder):
        '''Function that executes a set of SQL scripts  (tables)

        (Param) sql_sub_folder: Folder location with SQL statements to execute
        
        
        '''
        sql_loc = os.path.join(self.sqls,sql_sub_folder)

        sql_files = [os.path.join(sql_loc,f) for f in os.listdir(sql_loc) if f.endswith('.sql')] ## get only sql files 
        
        table_stats = [] ## init list of statements
        ##loop through and read sql statements
        for sql_file in sql_files:
            with open(sql_file, 'r') as f:
                print("Executing SQL Script:  " +  sql_file)
                sql_script = f.read()
                self.conn.cursor().executescript(sql_script)
                self.conn.commit()
                print('Execution Complete \n\n')


        

    def fixCorruptedDateAdded(self):
        """A manual corruption of Date Added data occurred for ~40 songs on April 20, 2020
        This function manually fixes the data that was corrupted
        """        
        
        ls_replace = [["FE8D87C0C0EA7D8C", "2014-10-27T00:00:45Z"],
                [ "FBC49C4E88776631", "2010-04-10T01:33:45Z"],
                ["B7165B3AED85299C", "2014-12-29T02:52:13Z"],
                ["6F6D32F2BD2EE3F4", "2014-12-28T18:46:51Z"],
                [ "D99AF260D41F6C4F", "2014-11-30T05:33:44Z"],
                ["5DE99AB605F43ACF","2014-12-15T03:29:11Z"],
                ["6010874DFB77FC72", "2014-10-27T00:19:36Z"],
                [ "79037EE5BA6BF8D2","2014-10-25T21:59:20Z"],
                ["370B2D3D1C57803B", "2014-12-14T21:36:33Z"],
                [ "91E9F16139D90692", "2015-01-11T04:06:04Z"],
                [ "F1C0383263A96725", "2014-11-21T01:37:51Z"],
                [ "3EBEC321DFDC1C2F", "2014-11-26T05:19:26Z"],
                [ "79F1A264D0A1A945", "2014-12-28T18:19:50Z"],
                ["BE6855A2C6E948F7", "2014-10-27T00:00:24Z"],
                [ "8ADE906EED0E0D2C", "2014-11-25T03:18:43Z"],
                [ "16064C06E8ACFD0D", "2014-12-21T02:12:24Z"],
                [ "C7E8F7F3F7CF0149", "2014-12-21T06:50:15Z"],
                [ "6C2039C2B7C8E8DE", "2015-01-03T20:48:23Z"],
                [ "DBA50B3EEA16F649", "2010-04-13T01:46:49Z"],
                [ "95C71792FC4CCB11", "2014-12-29T02:50:07Z"],
                ["CEE93D5E371A5A6A", "2015-01-17T05:16:39Z"],
                [ "6ADC22FD6945B388", "2015-02-11T05:20:30Z"],
                [ "DD996F95B3A48C73", "2014-12-29T02:47:42Z"],
                [ "892D58CB1C3B86ED", "2015-01-09T05:03:00Z"],
                [ "00095014C9DEE61F", "2015-01-18T20:32:10Z"],
                [ "F877F1F1E740443D", "2014-12-28T18:20:13Z"],
                ["6BBEE703523760C0", "2015-02-11T05:19:21Z"],
                [ "2753FC4D58E4E963", "2015-05-08T00:43:36Z"],
                [ "E5AD0BF1A303DA73", "2015-05-08T00:43:38Z"],
                [ "2B022BAE4851CF8F","2015-05-08T00:47:02Z"],
                [ "926254C858A07830", "2015-05-08T00:47:24Z"],
                [ "FE654DEB406FE6C6", "2015-02-23T01:59:02Z"],
                [ "C383A97AECD388C2", "2015-02-21T21:55:34Z"],
                ["1CBC1AED9A284B2A", "2016-07-11T21:16:47Z" ],
                ["756C4B7C3CE4DD23", "2016-07-11T21:16:47Z" ],
                ["53193B4B112A37C0","2016-07-11T21:16:47Z" ]]
        
        try:
            conn = db_ec.connect_db(self.targetDB)
            cur = conn.cursor()
          
            for item in ls_replace:
                
                cur.execute('''UPDATE metaMusic
                                SET Date_Added = ?
                                WHERE persistent_id = ?;''',(item[1], item[0]))
                           
                conn.commit()
                
                
                cur.execute('''UPDATE metaMusic
                                SET Date_Added_Simple = ?
                                WHERE persistent_id = ?;''',(item[1].split("T")[0], item[0]))
                conn.commit()
      
        finally:
            conn.close()
            
    def play_differentials(self,start_lib, end_lib, initializeByDateAdd = False, initalizeAddedSongs = True):
        """Function execute SQL script to calculate the number of plays, skips, and days between two library dates

        Args:
            start_lib (_type_): _description_
            end_lib (_type_): _description_
            initializeByDateAdd (bool, optional): _description_. Defaults to False.
            initalizeAddedSongs (bool, optional): _description_. Defaults to True.
        """    
        ## Calculation is done via SQL Script
        sql_loc = os.path.join(self.sqls,'cal_playdiffs.sql')
        ## Open and read SQL Script
        with open(sql_loc, 'r') as f:
                print("Executing SQL Script:  " +  sql_loc)
                sql_script = f.read()
        ## Execute SQL Script and fill parameters
        self.cur.execute(sql_script% (start_lib,end_lib,start_lib))
        ## Fetch results 
        res = self.cur.fetchall()
        
        if initializeByDateAdd == True:            
            #if initailize track on date added
            #add record with 0 days, 0 skips, 0 plays for songs added 
            
            # Select ids that were added between start and end libraries
            stat2 = '''SELECT persistent_id,
                            date_added_simple
                        FROM metaMusic
                        WHERE date_added_simple > ? AND date_added_simple <= ?;'''
                        
            self.cur.execute(stat2, (start_lib,end_lib))
            
            res2 = self.cur.fetchall()
            res2_list = []
        
            for item in res2:
                try:
                    res2_list.append((item[0],item[1], item[1], 0, 0,0))
                except: 
                    pass
                
            returnable = res + res2_list
            
        else:
            returnable = res
            
            
        if initalizeAddedSongs == True:
             #if initailize track on date added
            #add record with 0 days, 0 skips, 0 plays
            
            # Select ids that were added between start and end libraries
            stat2 = '''SELECT persistent_id,
                            ?
                        FROM metaMusic
                        WHERE date_added_simple > ? AND date_added_simple < ?;'''
                        
            self.cur.execute(stat2, (start_lib,start_lib,end_lib))
            
            res2 = self.cur.fetchall()
            res2_list = []
        
            for item in res2:
                try:
                    res2_list.append((item[0],item[1], item[1], 0, 0,0))
                except: 
                    pass
                
            returnable = res + res2_list
            
        else:
            returnable = res
            
            
        
        return(returnable)
            
            
    def createPlayDifferential(self, library_dates, new = True):
        """Function that adds play differentials between two different library dates, 
        A way to track how many times an individual song was played between two different
        timestamps

        Args:
            library_dates (list): list of library dates to create comparisons between
            new (bool, optional): Whether these calculations are new. Defaults to True.
        """        
        
        import numpy as np
        
        if new == True:
            try:
                ## Fetch all libraries dates already loaded to differentials table
                self.cur.execute('SELECT DISTINCT(StartLib) FROM playdiffs;') 
                ## extract
                loaded = [item[0] for item in self.cur.fetchall()]
                ## Only take dates if they havent been loaded already
                library_dates = sorted([lib for lib in library_dates if lib not in loaded])
                
            except sqlite3.OperationalError:
                pass
 
        
        lib_idx = list(range(0,len(library_dates))) #create index of all library dates
        lib_count = len(lib_idx) #count library dates
        to_db = [] #initialize
        
        #calculate differentials
        
        for start_lib in range(0,lib_count): #begin loop at first library to go through a libraries
            
            for end_lib in range(start_lib+1,lib_count): #start next loop at library one head of start
                ## Function creates row
                result = self.play_differentials(library_dates[lib_idx[start_lib]], library_dates[lib_idx[end_lib]])
                
                for row in result:
                    to_db.append(row)
                
                print("Differentials Calculated for ", library_dates[lib_idx[start_lib]], " and " ,library_dates[lib_idx[end_lib]])
        
        
        ## create view
                
        vstat1 = "DROP TABLE IF EXISTS differentials;"
                    
        vstat2 = '''CREATE TABLE differentials(persistent_id,
                                            start_lib, 
                                            end_lib, 
                                            days, 
                                            plays, 
                                            skips,
                                            
                                            primary key(persistent_id, start_lib, end_lib));'''
                    
        
        
        try:

            conn = db_ec.connect_db(self.targetDB)
            cur = conn.cursor()

            cur.execute(vstat1)
            conn.commit()

            cur.execute(vstat2)
            conn.commit()
            
            
        except:
            print("Error creating view")
            
        
        try:
            cur.executemany("INSERT OR REPLACE INTO differentials(persistent_id, start_lib, end_lib, days, plays, skips) VALUES(?,?,?,?,?,?);" ,
                            to_db)
                        
            conn.commit()
            
        except:
            print("Error loading table")
            
        finally:
            print("Differentials Loaded")
            conn.close()
            
    def QueryToCSV(self, statement, output, returnRaw = False):
        import pandas as pd
        
        try:
            conn = db_ec.connect_db(self.targetDB)
    
            statDF = pd.read_sql_query(statement, conn)
            
        except:
            print("Error in Query")
            
        finally:
            conn.close()
        
        statDF.to_csv(output, index=False)
            
        if returnRaw == True:
            return statDF
        
    def fetchLyrics(self, APIcode):
        import lyricsgenius
        import pandas as pd
        
        genius = lyricsgenius.Genius(APIcode)
        
        statement = '''SELECT  persistent_id, 
                            album_artist,
                            title,
                            lyrics
                            
                            FROM metaMusic;'''
        try:
            conn = db_ec.connect_db(self.targetDB)
            
            metaDF = pd.read_sql_query(statement, conn)
            metaDF = metaDF[metaDF['lyrics'].isnull()]
            
        except:
            print("Failed to connect to MetaMusic Table")
        finally:
            conn.close()
        
        def geniusAdd(songName, ArtistName):
            try:
                song = genius.search_song(songName,ArtistName)
                lyrics = song.lyrics
            except:
                lyrics = ""
            
            return lyrics

        metaDF['lyrics'] = metaDF.apply(lambda x: geniusAdd(x.title,x.album_artist),axis = 1)
        metaDF_filter = metaDF[['persistent_id', 'lyrics']]
        to_DB = tuple(metaDF.to_records(index = False))
        update_stat = '''UPDATE metaMusic
                        SET lyrics = ?
                        WHERE persistent_id = ?;'''
        
        try:
             conn = db_ec.connect_db(self.targetDB)
             cur = conn.cursor()
             
             cur.executemany(update_stat, to_DB)
             
             conn.commit()
             
        except:
            print("Error loading lyrics")
            
        finally: 
            conn.close()
        
            
        
            