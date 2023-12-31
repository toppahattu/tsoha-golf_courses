# pylint: disable=unused-import, wrong-import-position

from os import getenv
from flask import Flask

app = Flask(__name__)
app.secret_key = getenv('SECRET_KEY')
app.config['TEMPLATES_AUTO_RELOAD'] = True

import routes.course
import routes.group
import routes.index
import routes.remove
import routes.review
import routes.user
