import logging
from pathlib import Path
from typing import Dict

import uvicorn
from litestar import Litestar, post,get
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.response_containers import Template
from litestar.static_files.config import StaticFilesConfig
from litestar.template import TemplateConfig

from app.lucky import get_random_word
from app.query import qry_mdx_def

log = logging.getLogger(__name__)
# disable elasticsearch INFO log
logging.getLogger('elasticsearch').setLevel(logging.WARN)


@post(path="/query")
async def query(data: Dict[str, str]) -> str:
    word = data["word"]
    log.info(f">>> query for={word}")
    return qry_mdx_def(word)


@post(path="/lucky")
async def feeling_lucky() -> str:
    word = get_random_word()
    log.info(f">>> lucky for={word}")
    return qry_mdx_def(word)


@get(path="home")
def home() -> Template:
    return Template(name="home.html")


app = Litestar(
    route_handlers=[home, query, feeling_lucky],
    template_config=TemplateConfig(
        directory=Path("resources/templates"),
        engine=JinjaTemplateEngine,
    ),
    static_files_config=[
        StaticFilesConfig(path="/", directories=[Path("resources/static")]),
    ]
)

if __name__ == '__main__':
    """
    阅读readme和config.ini
    """
    uvicorn.run(
        app
    )
