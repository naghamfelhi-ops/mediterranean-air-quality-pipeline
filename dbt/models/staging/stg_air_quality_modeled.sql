select
    city,
    cast(time as timestamp) as observed_at,
    pm10,
    pm2_5 as pm25,
    nitrogen_dioxide as no2,
    ozone as o3,
    sulphur_dioxide as so2,
    carbon_monoxide as co
from {{ source('raw', 'air_quality_modeled') }}