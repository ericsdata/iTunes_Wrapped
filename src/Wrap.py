# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 12:12:15 2020

@author: eachr
"""
import xml.etree.ElementTree as ET
import collections
import db_ec


class LibraryHandler:
       
    def __init__(self, location, lib_date, targetDB, reload = True):
        import os
        #init library meta data
        self.lib_date = lib_date
        self.lib_date_f = lib_date[:4]+'-'+lib_date[4:6] + '-'+lib_date[6:]
        self.location = os.path.join(location,"".join(["itunes.lib.",lib_date,".xml"]))
        self.targetDB = targetDB
        self.reload = reload
        
    
    def processXML(self, path):
        import xml.etree.ElementTree as ET
        import collections
        ##extract data from file
        
        lib_date = self.lib_date
        
        parser = ET.XMLParser(encoding = "utf-8") #init parser
        
        tree = ET.parse(path, parser = parser) #get XML Tree
        root = tree.getroot()
        
        main_dict = root.findall('dict') # find all indexed
        
        for item in list(main_dict[0]):
            if item.tag=="dict":
                tracks_dict=item
                break
            
        tracklist=list(tracks_dict.findall('dict'))
        
        #list(tracklist[0])
        
        musicXML = [] # Music added to library through subscription
        
        for item in tracklist:
            musicXML.append(list(item))
        
        return musicXML
    
    
    def XMLheaders(self,kind):
         cols=[]
         for i in range(len(kind)):
             for j in range(len(kind[i])):
                 if kind[i][j].tag=="key":
                     cols.append(kind[i][j].text)
         return set(cols)
    
    
    def updateTableData(self, XML, XMLheaders, columnNames, db_location, table):
        import collections
        import db_ec as edbd
        
        to_DB = [] #list to send as rows to DB
        #headers
        mucols = columnNames
        music_cols = XMLheaders
        
        for i in range(len(XML)):
            ##Go track at a time
            dict1={} #initiate dictionary for values
            for m in music_cols:
                dict1[m] = 'NULL'
            
           #loop thru headers and grab values
            for j in range(len(XML[i])):
                if XML[i][j].tag=="key":             
                    dict1[XML[i][j].text]=XML[i][j+1].text
                    #add library date column
                    dict1['Library Date'] = self.lib_date_f
                
            
            
            ##make dictionary of just keys
                    
            XMLKeydict = {} #
            XMLKeydict = {key:val for key, val in dict1.items() if key in  mucols}
            
            if "Date Added" in XMLKeydict.keys():
            ##creat simplifed date added
                temp = XMLKeydict['Date Added'].split("T")
                XMLKeydict['Date Added Simple'] = temp[0]
            
        
            ##Sort
            OD_dict = collections.OrderedDict(sorted(XMLKeydict.items())) 
            
            meta_values=[i for i in OD_dict.values()]
            meta_keys=[j for j in OD_dict.keys()]
            
            
    
            ##meat data load
            to_DB.append(meta_values)
            
        ### Send to DB
        if table == "metaMusic":
        
            try: 
                conn = edbd.connect_db(db_location)
                cur = conn.cursor()
                
                cur.executemany('''
                                INSERT OR REPLACE INTO metaMusic ('album', 'album_artist','artist','date_added', 'date_added_simple','disc_number', 'disc_count', 
                                                                  'genre','title','persistent_id', 'total_time','track_count',
                                                                  'trackID','track_number','year') 
                                
                                VALUES(?,?,?,?,?,?,
                                       ?,?,?,?,?,?,
                                       ?,?,?);''', 
                                to_DB
                                )
                conn.commit()
            
                print("\nMetadata loaded: ",self.lib_date)
            
            finally:
                conn.close()
                

        elif table == "activity":
            try: 
                conn = edbd.connect_db(db_location)
                cur = conn.cursor()
                
                cur.executemany('''
                                INSERT OR REPLACE INTO activity ('library_date','persistent_id', 'play_count', 'skip_count') 
                                
                                VALUES(?,?,?,?);''', 
                                to_DB
                                )
                conn.commit()
                print("Activity Data loaded: ", self.lib_date, "\n")
    
            finally:
                conn.close()
       
        else:
            print("Not a valid table")
            
        
    
    
    
# =============================================================================
# library = LibraryHandler("..\LibData","20170809","iTunes.db")
# loc = library.location
# 
# XMLdata = library.processXML(loc)
# XMLheads = library.XMLheaders(XMLdata)
# =============================================================================

