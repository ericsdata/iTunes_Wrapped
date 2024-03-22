# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 12:12:15 2020

Class is used to extract raw XML data, transform in to python list, and load to a target database 

@author: eachr
"""



class Library:
    import xml.etree.ElementTree as ET
    import collections

    """
    A class to handle processing and updating of music library data.

    Attributes:
        location (str): The directory location of the XML file.
        lib_date (str): The date associated with the library data.
        conn: The connection object to the database.
        reload (bool): A flag indicating whether to reload the data.
    """
       
    def __init__(self, location, lib_date, conn, reload = True):
        """
        Initializes a Library object.

        Parameters:
            location (str): The directory location of the XML file.
            lib_date (str): The date associated with the library data.
            conn: The connection object to the database.
            reload (bool): A flag indicating whether to reload the data.
        """
        import os
        #init library meta data
        self.lib_date = lib_date
        self.lib_date_f = lib_date[:4]+'-'+lib_date[4:6] + '-'+lib_date[6:]
        self.location = os.path.join(location,"".join(["itunes.lib.",lib_date,".xml"]))
        self.reload = reload
        self.conn = conn
        
    
    def processXML(self, path):
        '''
       Function to parse XML library info and return python object

       (Param) path : XML file location
       (Returns) musicXML: Raw Data in List
        '''
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
        
       
        musicXML = [] # Music added to library through subscription
        
        for item in tracklist:
            musicXML.append(list(item))
        
        return musicXML
    
    
    def XMLheaders(self,kind):
        '''
         Extract the field names from XML data, to be used for column headers

         (param) kind: XMLdata generated
         '''
        cols=[]
        for i in range(len(kind)):
            for j in range(len(kind[i])):
                if kind[i][j].tag=="key":
                    cols.append(kind[i][j].text)
        return set(cols)
    
    
    def updateTableData(self, XML, XMLheaders, table_cols, db_location, table):
        '''Function handles the update of the database from raw data
        
        
        Parameters:
        XML (list): A list of raw data containing music metadata.
        XMLheaders (list): A list of  headers.
        columnNames (list): A list of column names for the database table.
        db_location (str): The path to the SQLite database file.
        table (str): The name of the table to update in the database.

        Returns:
        None: This function does not return any value. It updates the specified table in the database.

        '''
        
        import collections
        
        to_DB = [] #list to send as rows to DB

        
        for i in range(len(XML)):
            ##Go track at a time
            #initiate dictionary to hold values
            dict1={}
            for m in XMLheaders:
                dict1[m] = 'NULL'
            
           #use headers to loop through XML data and add values to dictionary
            for j in range(len(XML[i])):
                if XML[i][j].tag=="key":             
                    dict1[XML[i][j].text]=XML[i][j+1].text
                    #add library date column
                    dict1['Library Date'] = self.lib_date_f
                
            
            
            ##make dictionary of just keys       
            XMLKeydict = {key:val for key, val in dict1.items() if key in  table_cols}
            ##create simplifed date added
            if "Date Added" in XMLKeydict.keys():
                temp = XMLKeydict['Date Added'].split("T") ## Split timestamp on time
                XMLKeydict['Date Added Simple'] = temp[0] ## add just date

            ##Sort items in 
            OD_dict = collections.OrderedDict(sorted(XMLKeydict.items())) 

            lib_values=[i for i in OD_dict.values()]
            lib_keys=[j for j in OD_dict.keys()]
    
            ##meat data load
            to_DB.append(lib_values)
            
        ### Send to DB
        if table == "metaMusic":
        
            try: 
                cur = self.conn.cursor()
                
                cur.executemany('''
                                INSERT OR REPLACE INTO metaMusic ('album', 'album_artist','artist','date_added', 'date_added_simple','disc_number', 'disc_count', 
                                                                  'genre','title','persistent_id', 'total_time','track_count',
                                                                  'trackID','track_number','year') 
                                
                                VALUES(?,?,?,?,?,?,
                                       ?,?,?,?,?,?,
                                       ?,?,?);''', 
                                to_DB
                                )
                self.conn.commit()
            
                print("\nMetadata loaded: ",self.lib_date)
            except:
                print('Metadata Table upload failed')
                

        elif table == "activity":
            try: 
                cur = self.conn.cursor()
                
                cur.executemany('''
                                INSERT OR REPLACE INTO activity ('library_date','persistent_id', 'play_count', 'skip_count') 
                                
                                VALUES(?,?,?,?);''', 
                                to_DB
                                )
                self.conn.commit()
                print("Activity Data loaded: ", self.lib_date, "\n")
    
            except:
                print('Activity Table upload failed')
       
        else:
            print("Not a valid table")
            
        
    
    
    
# =============================================================================
# library = LibraryHandler("..\LibData","20170809","iTunes.db")
# loc = library.location
# 
# XMLdata = library.processXML(loc)
# XMLheads = library.XMLheaders(XMLdata)
# =============================================================================

