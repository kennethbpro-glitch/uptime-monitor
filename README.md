## Overview
Automated website uptime monitoring script built in Python with AWS CloudShell, S3, and SNS. Checks multiple URLs, logs results, and sends alerts for downtime.

## Features
Monitors uptime for multiple websites (`Mysites.txt`)  
- Logs results locally (`logs/`) and uploads to S3* 
- Sends SNS Notifications* for downtime  
- CloudShell-safe and configurable via environment variables  
- Ready for automation (cron or AWS Lambda)

##Project Structure
monitor.py # main script
Mysites.txt # URLs to monitor
requirements.txt # dependencies
logs/ # runtime logs
.gitignore # excludes logs and temp files
README.md # this file

Setup and Usage 

Clone repo: git clone https://github.com/kennethbpro-glitch/uptime-monitor.git
cd uptime-monitor

Install dependecies: python3 -m pip install --user -r requirements.txt

Set environment variables: 
export S3_bucket=kenstackbucket1
export SNS_Topic_arn.........uptime-alerts

Run script:
python3 monitoor.py

Next Steps / Improvements

Schedule hourly monitoring via Lambda or cron
Build a dashboard for visual uptime metrics
Extend alerts to Slack, Teams, or other channels
