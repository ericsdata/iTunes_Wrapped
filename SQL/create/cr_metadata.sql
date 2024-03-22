/*Create table with cols*/

CREATE TABLE IF NOT EXISTS metaMusic(
                        trackID integer,
                        title text,
                        artist text,
                        album text,
                        album_artist text,
                        date_added  text,
                        date_added_simple text,
                        disc_count integer,
                        disc_number integer,
                        genre text, 
                        total_time real,
                        track_number integer,
                        track_count integer,
                        year integer, 
                        persistent_id text,
                        lyrics text,
                    
                        primary key(persistent_id));
/*Add index on ID of track*/
CREATE INDEX track_id ON metaMusic(persistent_id);