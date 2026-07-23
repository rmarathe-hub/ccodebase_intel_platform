"""Pipeline helpers."""

WEATHER_MATCH_STATUS_VALUES = (
    "no_obs_in_window",
    "matched_near",
    "matched_window",
    "matched_far",
)


def weather_match_status(lag_minutes: int | None) -> str:
    """Return accepted weather_match_status values for a lag."""
    if lag_minutes is None:
        return "no_obs_in_window"
    abs_lag = abs(lag_minutes)
    if abs_lag <= 30:
        return "matched_near"
    if abs_lag <= 120:
        return "matched_window"
    return "matched_far"
