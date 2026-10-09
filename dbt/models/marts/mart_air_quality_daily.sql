with daily as (
    select
        city,
        cast(observed_at as date) as day,
        avg(pm25_modeled) as pm25_modeled_avg,
        avg(pm10_modeled) as pm10_modeled_avg,
        avg(no2_modeled) as no2_modeled_avg,
        avg(temperature_c) as temperature_avg_c,
        sum(precipitation_mm) as precipitation_total_mm,
        avg(wind_speed_kmh) as wind_speed_avg_kmh,
        count(pm25_measured) as pm25_measured_hours,
        case when count(pm25_measured) >= 18 then avg(pm25_measured) end as pm25_measured_avg,
        case when count(pm10_measured) >= 18 then avg(pm10_measured) end as pm10_measured_avg
    from {{ ref('mart_air_quality_hourly') }}
    group by city, cast(observed_at as date)
)

select
    *,
    pm25_modeled_avg > 15 as exceeds_who_pm25_modeled,
    pm10_modeled_avg > 45 as exceeds_who_pm10_modeled,
    no2_modeled_avg > 25 as exceeds_who_no2_modeled,
    pm25_measured_avg > 15 as exceeds_who_pm25_measured
from daily