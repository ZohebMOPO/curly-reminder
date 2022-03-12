import slack
import os
from pathlib import pathlib
from dotenv import load_dotenv

#load environment variable file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)