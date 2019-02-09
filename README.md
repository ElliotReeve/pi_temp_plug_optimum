<h1>Raspberry PI Temperature Controller - TP Link</h1>

Run API: `sudo python3 app_temp.py &> /dev/null &`
Add Script to Crontab: `*/10 * * * * /usr/bin/python3 your/url/path/reached_temp.py`

<h3>Endpoints</h3>
`/get-temp` - returns the current temperature
`/set-temp` - turns on tp-link plug to reach an optimum temperature of 20C
`/stop-temp` - turns off tp-link and stops trying to reach optimum temperature
