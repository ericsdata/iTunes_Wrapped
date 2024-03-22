/*Convert Null Values in Activity to 0*/
UPDATE activity
SET play_count = 0
WHERE  play_count = 'NULL'
                        ;

UPDATE activity
SET skip_count = 0
WHERE skip_count = 'NULL'
;