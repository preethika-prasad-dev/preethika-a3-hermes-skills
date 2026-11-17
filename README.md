# Preethika's Hermes skills

This public skill tap contains the original **Forecast Window** skill created for
USC CSCI 599 Assignment 3. It produces a date- and timezone-specific two-day
forecast for daily briefings and outdoor plans, with source attribution and a
validated National Weather Service fallback.

## Install with Hermes

```sh
hermes skills tap add preethika-a3-hermes-skills
hermes skills install forecast-window
```

After installation, Hermes can use the skill when a request needs briefing
weather or weather-sensitive planning. The helper can also be tested directly:

```sh
python3 ~/.hermes/skills/forecast-window/scripts/forecast.py 34.0522 -118.2437
```

The skill does not require a key. It sends approximate coordinates only to
Open-Meteo or the U.S. National Weather Service, validates the response shape,
and prints the cited source URL.

## Layout

Hermes discovers each subdirectory under `skills/` that contains a `SKILL.md`.
The pinned public commit and clean-install transcript are included in the
Assignment 3 submission evidence.

