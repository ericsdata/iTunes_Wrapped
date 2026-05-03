# -*- coding: utf-8 -*-
"""
Created on Wed Dec 9 18:47:17 2020

@author: eachr
"""

import os
import re
from Library import Library
from DBM import DBM


## iTunes Data Loaded
db_loc = "iTunes.db"


### Columns to use
metaCols = ['Track ID', 'Name', 'Artist', 'Album', 'Album Artist', 'Date Added', 
            'Disc Count', 'Disc Number', 'Genre', 'Total Time', 'Track Count', 
            'Track Number', 'Year','Persistent ID']
activityCols = ['Library Date','Persistent ID','Play Count', 'Skip Count' ]
       

data_folder = r"lib_data"

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
    ### I've labeled file names with dates of libraries -- eight digits in a row
    pattern = r"\d{8}"
    
    libs = set()
    ## Loop through XML files and get dates and format
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            if ".xml" in name:
                ### Find date in file name and format
                match = re.search(pattern, name)
                if match:
                    date = match.group(0)
                    date_f = date[:4]+'-'+date[4:6] + '-'+date[6:]
                    libs.add(date_f)
    
    libs = list(libs)

    return sorted(libs)

library_dates = getlibDates(data_folder)

print(f"\nFound {len(library_dates)} library snapshots: {library_dates}\n")

## Use library dates to clean and update data
for lib in library_dates:
    lib_unformatted = lib.replace("-","")
    print(f"Processing library snapshot: {lib}")
    
    try:
        library = Library(data_folder, lib_unformatted, DB.conn)
        
        loc = library.location
        print(f"  Loading XML from: {loc}")

        XMLdata = library.processXML(loc)
        XMLheads = library.XMLheaders(XMLdata)

        library.updateTableData(XMLdata, XMLheads, metaCols, db_loc, "metaMusic")
        library.updateTableData(XMLdata, XMLheads, activityCols, db_loc, "activity")
        print(f"  ✓ Successfully loaded {lib}\n")
        
    except Exception as e:
        print(f"  ✗ Error processing {lib}: {e}\n")
        continue


## Execute cleaning scripts
print("Executing data cleaning scripts...")
try:
    DB.ExecuteScripts('clean')
    print("✓ Cleaning scripts executed\n")
except Exception as e:
    print(f"✗ Error executing cleaning scripts: {e}\n")

## Fix corrupted date data
print("Fixing corrupted date entries...")
try:
    DB.fixCorruptedDateAdded()
    print("✓ Date corruption fixes applied\n")
except Exception as e:
    print(f"✗ Error fixing corrupted dates: {e}\n")

## Create play differentials
print("Calculating play differentials...")
try:
    DB.createPlayDifferential(library_dates)
    print("✓ Play differentials calculated\n")
except Exception as e:
    print(f"✗ Error calculating play differentials: {e}\n")

## Fetch lyrics (optional - requires API key)
print("Attempting to fetch lyrics...")
try:
    if os.path.exists("genius_token.txt"):
        with open("genius_token.txt", 'r') as genius_api:
            gen_pw = genius_api.readline().strip()
        
        if gen_pw:
            DB.fetchLyrics(gen_pw)
            print("✓ Lyrics fetched\n")
        else:
            print("⚠ No Genius API token found in genius_token.txt\n")
    else:
        print("⚠ genius_token.txt not found - skipping lyrics fetch\n")
except Exception as e:
    print(f"⚠ Warning: Could not fetch lyrics: {e}\n")
    print("  This is optional and not required for the app to work\n")

print("=" * 60)
print("✓ WORKER.py completed successfully!")
print("=" * 60)

