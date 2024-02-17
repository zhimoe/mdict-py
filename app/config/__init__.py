import configparser
from dataclasses import dataclass
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).parent.parent.parent


def file_abspath(relative_path: str) -> str:
    """get file absolute path from project root"""
    return (project_root() / relative_path).as_posix()


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
    parser.read((project_root() / "config.ini"), encoding="utf8")
    global es_config
    es_config = ESConfig(parser)
    global ai_config
    ai_config = ESConfig(parser)


es_config = None
ai_config = None
_init()  # initialize the config object when import
