/*Where Album Artist Field is Missing, use Artist field to fill*/
UPDATE metaMusic
SET album_artist = artist
WHERE  album_artist = 'NULL'
;