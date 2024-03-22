CREATE TABLE IF NOT EXISTS playDiffs(
                        persistent_id text,
                        StartLib text,
                        EndLib text,
                        Days integer,
                        Plays integer,
                        Skips  integer,
                    
                        primary key(persistent_id, StartLib, EndLib));
    

CREATE INDEX track_LibDiff ON playDiffs(persistent_id, StartLib, EndLib);