"""Create configparser & provide app config file."""
from configparser import ConfigParser
from backend.app.utils import paths

parser: ConfigParser = ConfigParser()
parser.read(paths.Project.settings_path())
