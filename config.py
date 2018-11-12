import os
from os.path import join, dirname

SECRET_KEY = os.environ.get('SECRET_KEY')
REDIS_URL = os.environ.get('REDIS_URL')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
