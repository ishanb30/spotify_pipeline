
select
    RAW_DATA:played_at::timestamp_tz as played_at,
    RAW_DATA:track:id::varchar as track_id,
    RAW_DATA:track:album as track_album,
    RAW_DATA:track:artists as track_artists,
    RAW_DATA:track:disc_number::int as track_disc_number,
    RAW_DATA:track:duration_ms::int as track_duration_ms,
    RAW_DATA:track:explicit::boolean as track_explicit,
    RAW_DATA:track:name::varchar as track_name,
    RAW_DATA:track:track_number::int as track_number,
    RAW_DATA:track:uri::varchar as track_uri,
    RAW_DATA:track:is_local::boolean as track_is_local,
    RAW_DATA:context:type::varchar(15) as context_type

from {{ source("raw", "RECENTLY_PLAYED") }}