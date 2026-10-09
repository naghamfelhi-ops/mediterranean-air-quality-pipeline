-- Ce test réussit s'il ne renvoie aucune ligne : une seule ligne par ville et par heure


select city, observed_at, count(*) as n
from {{ ref('mart_air_quality_hourly') }}
group by city, observed_at
having count(*) > 1