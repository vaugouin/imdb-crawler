import time
import requests
import pymysql.cursors
import json
import citizenphil as cp
from datetime import datetime, timedelta
import gzip
import shutil
import csv
import os

datnow = datetime.now(cp.paris_tz)
# Compute the date and time for J-1 (yesterday)
# So we are sure to find the IMDb Id export files
delta = timedelta(days=1)
datjminus1 = datnow - delta
#strdatjminus1 = datjminus1.strftime("%Y-%m-%d %H:%M:%S")
strdattodayminus1 = datjminus1.strftime("%Y-%m-%d")
strdattodayminus1us = datjminus1.strftime("%m_%d_%Y")
strimdbdatprev = cp.f_getservervariable("strimdbcrawlerimportdate",0)
print(f"strimdbdatprev={strimdbdatprev}")

try:
    conn = cp.f_getconnection()
    with conn:
        with conn.cursor() as cursor:
            cursor3 = conn.cursor()
            intdownloadok = True
            if strdattodayminus1 > strimdbdatprev:
                # Start timing the script execution
                start_time = time.time()
                strnow = datetime.now(cp.paris_tz).strftime("%Y-%m-%d %H:%M:%S")
                cp.f_setservervariable("strimdbcrawlerstartdatetime",strnow,"Date and time of the last start of the IMDb crawler",0)
                strprocessesexecutedprevious = cp.f_getservervariable("strimdbcrawlerprocessesexecuted",0)
                strprocessesexecuteddesc = "List of processes executed for the download of the IMDb ID import files"
                cp.f_setservervariable("strimdbcrawlerprocessesexecutedprevious",strprocessesexecutedprevious,strprocessesexecuteddesc + " (previous execution)",0)
                strprocessesexecuted = ""
                cp.f_setservervariable("strimdbcrawlerprocessesexecuted",strprocessesexecuted,strprocessesexecuteddesc,0)

                strtotalruntimedesc = "Total runtime of the IMDb crawler"
                strtotalruntimeprevious = cp.f_getservervariable("strimdbcrawlertotalruntime",0)
                cp.f_setservervariable("strimdbcrawlertotalruntimeprevious",strtotalruntimeprevious,strtotalruntimedesc + " (previous execution)",0)
                strtotalruntime = "RUNNING"
                cp.f_setservervariable("strimdbcrawlertotalruntime",strtotalruntime,strtotalruntimedesc,0)
                # Now let's import the IMDb data files
                print("This is a newer date, so we must download the IMDb data files and import them into the MySQL database")
                arrimdbfile = {1: 'title.ratings', 2: 'title.basics', 3: 'title.akas', 4: 'title.principals', 5: 'name.basics', 6: 'title.episode', 7: 'title.crew'}
                arrimdbfile = {1: 'title.ratings'}
                #arrimdbfile = {2: 'title.basics'}
                #arrimdbfile = {3: 'title.akas'}
                #arrimdbfile = {4: 'title.principals'}
                #arrimdbfile = {5: 'name.basics'}
                #arrimdbfile = {6: 'title.episode'}
                #arrimdbfile = {7: 'title.crew'}
                for intimdbfile,strimdbfilename in arrimdbfile.items():
                    strcurrentprocess = f"{intimdbfile}: processing " + strimdbfilename + " data from IMDb"
                    cp.f_setservervariable("strimdbcrawlercurrentprocess",strcurrentprocess,"Current process in the IMDb crawler",0)
                    if intimdbfile == 1:
                        # title.ratings
                        strsqltablename = "T_WC_IMDB_MOVIE_RATING_IMPORT"
                    elif intimdbfile == 2:
                        # title.basics
                        strsqltablename = "T_WC_IMDB_MOVIE_BASIC_IMPORT"
                    elif intimdbfile == 3:
                        # title.akas
                        strsqltablename = "T_WC_IMDB_MOVIE_AKA_IMPORT"
                    elif intimdbfile == 4:
                        # title.principals
                        strsqltablename = "T_WC_IMDB_MOVIE_PRINCIPAL_IMPORT"
                    elif intimdbfile == 5:
                        # name.basics
                        strsqltablename = "T_WC_IMDB_PERSON_BASIC_IMPORT"
                    elif intimdbfile == 6:
                        # title.episode
                        strsqltablename = "T_WC_IMDB_SERIE_EPISODE_IMPORT"
                    elif intimdbfile == 7:
                        # title.crew
                        strsqltablename = "T_WC_IMDB_PERSON_MOVIE_IMPORT"
                    else:
                        strsqltablename = ""
                    if strsqltablename != "":
                        strprocessesexecuted += str(intimdbfile) + ", "
                        cp.f_setservervariable("strimdbcrawlerprocessesexecuted",strprocessesexecuted,strprocessesexecuteddesc,0)
                        strimdbimportdatevarname = "strimdbcrawler"+strimdbfilename.replace(".","")+"importdate"
                        strimdbchangescountvarname = "strimdbcrawler"+strimdbfilename.replace(".","")+"importcount"
                        strnow = datetime.now(cp.paris_tz).strftime("%Y-%m-%d %H:%M:%S")
                        cp.f_setservervariable(strimdbimportdatevarname,strnow,"Date and time of the last download of the IMDb "+strimdbfilename,0)
                        strimdbratingsfileurl = f"https://datasets.imdbws.com/{strimdbfilename}.tsv.gz"
                        strlocalgzfilename = '/shared/' + strimdbfilename + '.tsv.gz'
                        strlocaltsvfilename = '/shared/' + strimdbfilename + '.tsv'
                        print(f"Download from {strimdbratingsfileurl} to {strlocalgzfilename}")
                        response = requests.get(strimdbratingsfileurl, stream=True)
                        # Check if the request was successful
                        if response.status_code == 200:
                            # Open a file in binary write mode
                            #strlocalgzfilename = strimdbfilename + '.tsv.gz'
                            #strlocaltsvfilename = strimdbfilename + '.tsv'
                            print(f"Extract {strlocalgzfilename} to {strlocaltsvfilename}")
                            with open(strlocalgzfilename, 'wb') as file:
                                # Iterate over the response data in chunks
                                for chunk in response.iter_content(chunk_size=8192):
                                    # Write each chunk to the local file
                                    file.write(chunk)
                                # file.write(response.content)
                            # Extract gz to tsv
                            with gzip.open(strlocalgzfilename, 'rb') as f_in:
                                # Open a new file in write-binary mode
                                with open(strlocaltsvfilename, 'wb') as f_out:
                                    # Copy the decompressed data to the new file
                                    shutil.copyfileobj(f_in, f_out)
                            print(f"Remove {strlocalgzfilename}")
                            os.remove(strlocalgzfilename)
                            # Open and read the tsv file
                            print(f"Import {strlocaltsvfilename} to {strsqltablename}")
                            strsqlbefore = f"""SET autocommit = 0; 
SET unique_checks = 0; 
SET foreign_key_checks = 0; 
ALTER TABLE {strsqltablename} DISABLE KEYS; 
TRUNCATE TABLE {strsqltablename}; """
                            strsqlload = f"""LOAD DATA INFILE '{strlocaltsvfilename}' 
INTO TABLE {strsqltablename} 
FIELDS TERMINATED BY '\t' 
ENCLOSED BY '' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS; """
                            strsqlafter = f"""ALTER TABLE {strsqltablename} ENABLE KEYS; 
SET foreign_key_checks = 1; 
SET unique_checks = 1; 
COMMIT; 
SET autocommit = 1; """
                            # Step 1: Execute pre-import SQL
                            for statement in strsqlbefore.strip().split(';'):
                                if statement.strip():
                                    cursor.execute(statement)
                            # Step 2: Execute LOAD DATA
                            cursor.execute(strsqlload)
                            # Step 3: Execute post-import SQL
                            for statement in strsqlafter.strip().split(';'):
                                if statement.strip():
                                    cursor.execute(statement)
                            # Final commit if needed (though COMMIT is in strsqlafter)
                            #connection.commit()
                            print(f"Import {strlocaltsvfilename} to {strsqltablename} done!")
                            print(f"Remove {strlocaltsvfilename}")
                            os.remove(strlocaltsvfilename)
                        else:
                            # Failed to download one file
                            print("Failed to download the file.")
                            intdownloadok = False
                strcurrentprocess = ""
                cp.f_setservervariable("strimdbcrawlercurrentprocess",strcurrentprocess,"Current process in the IMDb crawler",0)
                strnow = datetime.now(cp.paris_tz).strftime("%Y-%m-%d %H:%M:%S")
                cp.f_setservervariable("strimdbcrawlerenddatetime",strnow,"Date and time of the IMDb crawler ending",0)
                # Calculate total runtime and convert to readable format
                end_time = time.time()
                strtotalruntime = int(end_time - start_time)  # Total runtime in seconds
                cp.f_setservervariable("strimdbcrawlertotalruntimeseconds",str(strtotalruntime),strtotalruntimedesc,0)
                readable_duration = cp.convert_seconds_to_duration(strtotalruntime)
                cp.f_setservervariable("strimdbcrawlertotalruntime",strtotalruntime,strtotalruntimedesc,0)
                print(f"Total runtime: {strtotalruntime} seconds ({readable_duration})")
                if intdownloadok:
                    # All files were downloaded so we save the date and time of the last completed download of IMDb data files
                    cp.f_setservervariable("strimdbcrawlerimportdate",strdattodayminus1,"Date of the last download of the IMDb ID import files",0)
    
    print("Process completed")
    
except pymysql.MySQLError as e:
    print(f"❌ MySQL Error: {e}")
    conn = getattr(cp, "connectioncp", None)
    if conn is not None and getattr(conn, "open", False):
        conn.rollback()
    
