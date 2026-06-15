
select
    played_at,
    album_id,
    track_id,
    track_name,
    track_uri,
    context_type as playback_source,
    track_number,
    track_duration_ms as duration_ms,
    track_explicit as is_explicit,
    track_disc_number as disc_number

from {{ ref("int_recently_played") }}