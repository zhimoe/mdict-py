import configparser
import os
from dataclasses import dataclass

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..'))


@dataclass
class ESConfig:
    host: str
    port: str
    enable: bool

    def __init__(self, parser: configparser.ConfigParser):
        self.host = parser["ES"]["host"]
        self.port = parser["ES"]["port"]
        self.enable = parser["ES"]["enable"] == "Y"


@dataclass
class AIConfig:
    enable: bool

    def __init__(self, parser: configparser.ConfigParser):
        self.enable = parser["AI"]["enable"] == "Y"


def _init():
    parser = configparser.ConfigParser()
    parser.read(os.path.join(ROOT_DIR, "config.ini"))
    global es_config
    es_config = ESConfig(parser)
    global ai_config
    ai_config = ESConfig(parser)


es_config = None
ai_config = None
_init()  # initialize the config object when import
