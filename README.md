# scrapersample

Example of a scraper project with the use of 
IP rotation (round robin) and captcha solver.
This particular sciprt registers new users on reddit.

For configuration, use following environment variables.
```
SAMPLESCRAPER_2CAPCTHA_API_KEY=<API key for 2Captcha (captcha solving service)>
SAMPLESCRAPER_PROXIES=<file with proxy list in format username:password@host:port>
SAMPLESCRAPER_N=<number of users to register>
SAMPLESCRAPER_HEADLESS=<if use headless browser>
SAMPLESCRAPER_SCREENSHOT_FOLDER=<foder to save result>
```

Run script as usual python script. Via virtual env:
```
# create virtual env
python3 -m venv venv

# activate it
. venv/bin/activate

# this is to export env variables, if they are saved in .env file
set -x
. .env

# run script
python main.py
```
