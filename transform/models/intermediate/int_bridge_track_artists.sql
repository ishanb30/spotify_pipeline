
{{ config(materialized="table") }}

select distinct
    artist.value:id::varchar as artist_id,
    track_id

from {{ ref("int_recently_played") }},
lateral flatten (input => track_artists) as artist