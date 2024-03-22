/*iTunes track lenght is measured in 1000th of a second, fit to  base seconds*/
UPDATE metaMusic
SET total_time = total_time/1000
                        ;