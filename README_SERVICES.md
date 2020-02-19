# Archive3 Services

## processor.py
The processor handles the most important tasks, such as the actual creation of screenshots.
```
[Unit]
Description=Archive3 Processor
After=syslog.target

[Service]
Type=simple
ExecStart=/var/www/www.archive3.com/venv/bin/python3 /var/www/www.archive3.com/archive3/processor.py
WorkingDirectory=/var/www/www.archive3.com
User=www-data
Group=www-data
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

## queue_processor.py
The queue processor handles scheduling of actions and events.
```
[Unit]
Description=Archive3 Queue Processor
After=syslog.target

[Service]
Type=simple
ExecStart=/var/www/www.archive3.com/venv/bin/python3 /var/www/www.archive3.com/archive3/queue_processor.py
WorkingDirectory=/var/www/www.archive3.com
User=www-data
Group=www-data
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

## uwsgi
The UWSGI server handles execution of Python scripts for the web server. UWSGI is just one of several possible ways to run Python scripts with a webserver.
```
[Unit]
Description=Archive3 uWSGI
After=syslog.target

[Service]
ExecStart=/usr/bin/uwsgi --ini /var/www/www.archive3.com/uwsgi.ini
Restart=always
RestartSec=5
KillSignal=SIGQUIT
Type=notify
NotifyAccess=all

[Install]
WantedBy=multi-user.target
```
