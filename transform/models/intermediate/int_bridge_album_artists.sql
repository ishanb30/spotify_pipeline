
{{ config(materialized="table") }}

select distinct
    album_id,
    artist.value:id::varchar as artist_id

from {{ ref("int_recently_played") }},
lateral flatten (input => album_artists) as artist