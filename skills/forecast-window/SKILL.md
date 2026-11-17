---
name: forecast-window
description: Fetch a date- and timezone-specific weather forecast for a daily briefing or upcoming outdoor plan.
version: 0.1.0
---

# Forecast Window

Use this skill for today's briefing, tomorrow's preview, and weather-sensitive
plans. Use the configured city center or ask for a city if the user has not
specified a location. Use approximate city coordinates only.

1. Run the bundled `scripts/forecast.py` with Python 3, passing latitude and
   longitude as decimal numbers. Example for Los Angeles:

   ```sh
   python3 scripts/forecast.py 34.0522 -118.2437
   ```

2. Use the date and timezone returned by the helper. In a daily briefing, give
   the high, low, and maximum precipitation probability for today's date. Add
   tomorrow only when a preview is requested.
3. If precipitation probability is 50% or higher, suggest one concrete
   adjustment for outdoor plans. Cite the returned Open-Meteo or National
   Weather Service source URL. If a date or value is unavailable, report the
   gap instead of inventing it.

