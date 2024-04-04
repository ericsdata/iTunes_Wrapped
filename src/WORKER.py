# -*- coding: utf-8 -*-
"""
Created on Wed Dec 9 18:47:17 2020

@author: eachr
"""

from Library import Library
from DBM import DBM


## iTunes Data Loaded
db_loc = "../iTunes.db"


### Columns to use
metaCols = ['Track ID', 'Name', 'Artist', 'Album', 'Album Artist', 'Date Added', 
            'Disc Count', 'Disc Number', 'Genre', 'Total Time', 'Track Count', 
            'Track Number', 'Year','Persistent ID']
activityCols = ['Library Date','Persistent ID','Play Count', 'Skip Count' ]
       

data_folder = r"..\lib_data"

## Open Connection to Database, tables created if not already created
DB = DBM(db_loc)

def getlibDates(path):
    '''Function that extracts dates from XML library files
    Reads by regex search defined

    Params:

    path (str) : path where libraries reside

    Returns:
        libs : a list of dates of iTunes snapshots
    ''' 
    import re
    import os
    ### I've labeled file names with dates of libraries -- deight digts in a row
    pattern = r"\d{8}"
    
    libs = set()
    ## Loop through XML files and get dates and fromat
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            if ".xml" in name:
                ### Find date in file name and format
                date = re.search(pattern,name)[0]
                date_f = date[:4]+'-'+date[4:6] + '-'+date[6:]
                libs.add(date_f)
    
    libs = list(libs)

    return sorted(libs)

library_dates = getlibDates(data_folder)

## Use library dates to clean and update data
for lib in library_dates:
    lib = lib.replace("-","")
    library = Library(data_folder,lib,DB.conn)
        
    loc = library.location

    XMLdata = library.processXML(loc)
    XMLheads = library.XMLheaders(XMLdata)

    library.updateTableData(XMLdata, XMLheads, metaCols,db_loc, "metaMusic")
    library.updateTableData(XMLdata, XMLheads, activityCols,db_loc, "activity")


## Some functional 
DB.ExecuteScripts('clean')
DB.fixCorruptedDateAdded()

DB.createPlayDifferential(library_dates)

genius_api = open("genius_token.txt",'r')
gen_pw = genius_api.readline()
genius_api.close()


DB.fetchLyrics(gen_pw)

