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
