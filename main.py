import logging
from pathlib import Path
from typing import Dict

import uvicorn
from starlite import Starlite, TemplateConfig, StaticFilesConfig, Template, get, post
from starlite.contrib.jinja import JinjaTemplateEngine

from app.lucky import get_random_word
from app.query import qry_mdx_def

log = logging.getLogger(__name__)


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


@get(path="/")
def index() -> Template:
    return Template(name="index.html")


app = Starlite(
    route_handlers=[index, query, feeling_lucky],
    template_config=TemplateConfig(
        directory=Path("resources/templates"),
        engine=JinjaTemplateEngine,
    ),
    static_files_config=StaticFilesConfig(
        path="static",
        directories=[Path("resources/static")]
    )
)

if __name__ == '__main__':
    """
    阅读readme和config.ini
    """
    uvicorn.run(
        app
    )
