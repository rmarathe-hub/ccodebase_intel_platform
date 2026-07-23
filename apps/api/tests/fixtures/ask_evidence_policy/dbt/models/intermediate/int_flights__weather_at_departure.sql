-- Intermediate: nearest weather observation at origin departure.
select
    f.flight_id,
    f.origin,
    f.dest,
    f.dep_time_utc,
    w.station_id,
    w.temp_c,
    w.wind_speed_knots,
    w.precip_1hr_inches,
    w.weather_obs_lag_minutes,
    case
        when w.station_id is null then 'no_obs_in_window'
        when abs(w.weather_obs_lag_minutes) <= 30 then 'matched_near'
        when abs(w.weather_obs_lag_minutes) <= 120 then 'matched_window'
        else 'matched_far'
    end as weather_match_status
from {{ ref('int_flights__departure_context') }} f
left join weather_candidates w
    on f.flight_id = w.flight_id
    and w.row_num = 1
