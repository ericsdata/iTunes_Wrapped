CREATE TABLE IF NOT EXISTS activity(
                        library_date text,
                        persistent_id text,
                        play_count integer,
                        skip_count integer,
                        
                        
                        primary key(persistent_id, library_date),
                        foreign key(persistent_id) references metaMusic(persistent_id));


