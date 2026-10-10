-- Ce test réussit s'il ne renvoie aucune ligne : pas de valeur absurde
select *
from {{ ref('mart_air_quality_hourly') }}
where pm25_modeled < 0 or pm25_modeled > 1000
   or wind_speed_kmh < 0 or wind_speed_kmh > 300
   or temperature_c < -50 or temperature_c > 60