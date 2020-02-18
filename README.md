# Archive3

[![Build Status](https://travis-ci.com/RigidBit/archive3.svg?branch=master)](https://travis-ci.com/RigidBit/archive3)
[![Requirements Status](https://requires.io/github/RigidBit/archive3/requirements.svg?branch=master)](https://requires.io/github/RigidBit/archive3/requirements/?branch=master)
![Status](https://img.shields.io/uptimerobot/status/m784351886-ad46f26677bcc9e5b890aaf4)
![Uptime](https://img.shields.io/uptimerobot/ratio/m784351886-ad46f26677bcc9e5b890aaf4)
[![Twitter Follow](https://img.shields.io/twitter/follow/archive3?style=social)](https://twitter.com/archive3)

This is the primary codebase for the Archive3 web application.

## Development Prerequisites

Before developing on this application you should have working knowledge of the following technologies and toolchains:

* HTML 5 / CSS 3 / Javascript (ECMAScript 6)
* SASS (https://sass-lang.com/)
* Npm (https://www.npmjs.com/)
* Python3 (https://www.python.org/)
* Selenium (https://selenium.dev/)
* Webpack (https://webpack.js.org/)

You should also have working experience with the following frameworks and libraries:

* jQuery (http://jquery.com/)

You must have the following installed in your development environment to properly build:

* Node.js (Via NVM is recommended: https://github.com/creationix/nvm#install-script)
* Npm (Automatically installed by nvm.)
* Npx (Automatically installed by nvm.)

## Production Server Prerequisites

* Apache or Nginx with WSGI/UWSGI capability.
* Beanstalkd (https://beanstalkd.github.io/)
* PostgreSQL (https://www.postgresql.org/)
* RigidBit (https://www.rigidbit.com/)
* Selenium server with Chrome webdriver.

### Production Server Fonts

Websites in languages that do not use Roman characters may require additional fonts to display correctly. The fonts DejaVu and Noto are free fonts that can be installed which handle many of the common languages.

* fonts-noto (https://www.google.com/get/noto/)
* ttf-dejavu (https://dejavu-fonts.github.io/)

## Basic Webserver Setup Procedure
* Create a web directory and create an initialized venv directory within it.
* Install dependencies within the venv.
* Populate .env with secrets and settings.
* Configure webserver to use WSGI with the venv and serve static content from the static and data directories.

## Development Setup

### Using a venv is recommended.
```
python -m venv init venv
source venv/bin/activate
```

### Installing dependencies:
```
source venv/bin/activate
pip install -r requirements.txt
```

### Saving dependencies:
Using `pipreqs` is recommended over `pip`. While in an active venv use the following to regenerate `requirements.txt`.
```
pipreqs --ignore node_modules --force
```

### Starting the development server:
```
source venv/bin/activate
```
or
```
FLASK_APP=archive3/web.py FLASK_DEBUG=1 python -m flask run -h 0.0.0.0 -p 5001
```

### Starting the development CSS builder:
```
npm start
```

### Starting the processing service:
```
source venv/bin/activate
python3 processor.py
```

### Starting the queue processing service:
```
source venv/bin/activate
python3 queue_processor.py
```

### Building static assets for production:
```
npm build
```
