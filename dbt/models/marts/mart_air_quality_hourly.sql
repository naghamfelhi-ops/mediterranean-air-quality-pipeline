with openaq as (
    select
        city,
        observed_at,
        avg(case when parameter = 'pm25' then value end) as pm25_measured,
        avg(case when parameter = 'pm10' then value end) as pm10_measured,
        count(distinct location_id) as n_stations
    from {{ ref('stg_openaq') }}
    group by city, observed_at
)

select
    a.city,
    a.observed_at,
    a.pm25 as pm25_modeled,
    a.pm10 as pm10_modeled,
    a.no2 as no2_modeled,
    a.o3 as o3_modeled,
    w.temperature_c,
    w.humidity_pct,
    w.precipitation_mm,
    w.wind_speed_kmh,
    w.wind_direction_deg,
    o.pm25_measured,
    o.pm10_measured,
    o.n_stations
from {{ ref('stg_air_quality_modeled') }} a
join {{ ref('stg_weather') }} w
    on a.city = w.city and a.observed_at = w.observed_at
left join openaq o
    on a.city = o.city and a.observed_at = o.observed_at