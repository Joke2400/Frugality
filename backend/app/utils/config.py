"""Create a configparser & read the config file."""
import sys
from dotenv import load_dotenv
from configparser import ConfigParser
from app.utils import paths, patterns
from app.utils.util_funcs import get_envvar

parser: ConfigParser = ConfigParser()
parser.read(paths.Project.settings_path())


class ENV(metaclass=patterns.SingletonMeta):
    """Singleton that fetches & stores the app envvars."""

    postgres_user: str
    postgres_password: str
    postgres_db: str

    debug: bool
    in_container: bool = False

    def __init__(self) -> None:
        # Check if -'-container=True' in launch args
        for arg in sys.argv[1:]:
            if "--container" in arg:
                if arg.split("=")[1].lower() == "true":
                    self.in_container = True
                    break
        # Load environment variables from .env file
        if self.in_container:
            load_dotenv(dotenv_path="../env/prod.env")
        else:
            load_dotenv(dotenv_path="../env/dev.env")
        self.postgres_user = get_envvar(key="POSTGRES_USER")
        self.postgres_password = get_envvar(key="POSTGRES_PASSWORD")
        self.postgres_db = get_envvar(key="POSTGRES_DB")
        self.debug = get_envvar(key="DEBUG") in ("True", "true")

        if self.debug and self.in_container:
            raise ValueError(
                "The flag '--container' & envvar 'DEBUG' cannot both be True.")
