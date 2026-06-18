
{{ config(
    severity='error',
    warn_if='>0',
    error_if='>50'
) }}

select
    *
from {{ ref("stg_recently_played") }}
where played_at > current_timestamp
