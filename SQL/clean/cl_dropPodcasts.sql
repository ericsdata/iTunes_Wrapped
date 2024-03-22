/*For this project, only look at media that is Music
    Delete all podcasts, Voice Memo, and Performing Arts fro library */

DELETE FROM activity
WHERE persistent_id IN (SELECT persistent_id
                            FROM metaMusic
                            WHERE genre == 'Podcast' OR genre == 'Performing Arts'
                            OR genre == 'Voice Memo');

DELETE FROM metaMusic 
WHERE genre == 'Podcast' OR genre == 'Performing Arts' OR genre == 'Voice Memo'
                            ;
