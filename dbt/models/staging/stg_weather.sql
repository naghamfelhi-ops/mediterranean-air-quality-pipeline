select
    city,
    cast(time as timestamp) as observed_at,
    temperature_2m as temperature_c,
    relative_humidity_2m as humidity_pct,
    precipitation as precipitation_mm,
    wind_speed_10m as wind_speed_kmh,
    wind_direction_10m as wind_direction_deg
from {{ source('raw', 'weather') }}