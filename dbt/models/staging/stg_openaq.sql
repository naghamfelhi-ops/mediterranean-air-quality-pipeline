select
    city,
    timezone('UTC', time) as observed_at,
    parameter,
    value,
    location_id,
    location_name
from {{ source('raw', 'openaq_measurements') }}
where value is not null
  and value >= 0
qualify row_number() over (
    partition by city, timezone('UTC', time), parameter, sensor_id
    order by ingested_at desc
) = 1