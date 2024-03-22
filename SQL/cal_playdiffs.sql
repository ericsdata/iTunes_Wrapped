/*SQL Script to Calculate the change in Play and Skip Count between to library dates*/
SELECT EndID        
        ,CASE WHEN s.StartLib IS NULL THEN  '%s'
            ELSE  s.StartLib
            END Startlib
        ,  EndLib
        , Cast ((JulianDay(EndLib) - JulianDay(StartLib)) As Integer) as Days 
        ,CASE WHEN StartPlays IS NULL THEN EndPlays 
                ELSE EndPlays - StartPlays 
                END Plays
        ,CASE WHEN StartSkips IS NULL THEN  EndSkips
             ELSE  EndSkips - StartSkips 
                END Skips
                        
                    
FROM (/*Table to get data relating to the ending library*/
        select persistent_id as EndID,
                    library_date as EndLib,
                    play_count as EndPlays, 
                    skip_count as EndSkips 
            FROM activity 
            WHERE EndLib = '%s') l
            
LEFT JOIN (/*Table to get data relating to the starting library*/
            SELECT persistent_id as StartID, 
                    library_date as StartLib,
                    play_count as StartPlays, 
                    skip_count as StartSkips 
                    
            FROM activity 
            WHERE StartLib = '%s') s
    ON EndID = StartID