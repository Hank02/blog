from flask import Flask
import os

app = Flask(__name__)
config_path = os.environ.get("CONFIG_PATH", "blog.config.DevelopmentConfig")
if os.environ.get("TRAVIS"):
    print("** Hacking config_path to TravisConfig **")
    print("config_path was: "+config_path)
    config_path = "blog.config.TravisConfig"
app.config.from_object(config_path)

from . import views
from . import filters
from . import login
