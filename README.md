# Esketit Robo-investor

# About

This bot invests automatically on Esketit's primary and secondary markets.

Esketit already has a robo-investor built-in, but for some reason it does not invest fast enough, causing cash drag.

# Install

Requires python 3.9+

`pip install -r requirements.txt`

# Run

Set up a cron job for this command:

`ESKETIT_EMAIL=your_email ESKETIT_PASSWORD=your_password python /path/to/project/main.py`

