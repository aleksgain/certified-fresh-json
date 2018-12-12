# Certified Fresh Parser

This is a parser for Rotten Tomato's Certified Fresh movie list. It returns a JSON list compatible with automation software and has a nice light front end for browsing.

![alt text](https://github.com/aleksgain/certified-fresh-json/blob/master/screenshot.png)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the following packages:

```bash
pip install imdbpy
pip install flask
pip install flask_session
pip install flask_paginate
```

## Usage

```python
flask run
```
The application runs as a service and updates once a day. During the update the database is refreshed and a json file is generated. Can be used as a standalone json generator by removing the html/flask code.

## Contributing
Pull requests are welcome!
