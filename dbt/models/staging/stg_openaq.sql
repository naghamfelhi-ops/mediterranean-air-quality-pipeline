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