# AI Modular Input App

## Setup

1. Set `disabled = 0` to enable the modular input in `./local/inputs/inputs.conf`.
2. Restart Splunk.
3. Verify our modular input entry is listed in Splunk Web -> Settings -> Data inputs.
4. Look for the enriched events by searching `index="main" sourcetype="ai_modinput_app:weather"`.

    ```txt
    {
        date: 2012-01-04
        human_readable: On January 4, 2012, it was rainy with 20.3 mm of precipitation, temperatures ranged from 5.6°C to 12.2°C, and there was a light wind of 4.7 m/s.
        It was probably not a great day to go outside for most people, due to the rainy weather.
        precipitation: 20.3
        temp_max: 12.2
        temp_min: 5.6
        weather: rain
        wind: 4.7
    }
    ```

## Troubleshooting

- See if there are any debug logs from the app

```spl
index="main" sourcetype="ai_modinput_app:debug_log"
```

- See if there's anything about the app in the logs

```spl
index="_internal" ai_modinput_app
```
