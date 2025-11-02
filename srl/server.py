from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shlex
import io
import traceback
from rich.console import Console
from srl.cli import build_parser
from srl.storage import ensure_data_dir
import uvicorn
from typing import Optional, List

router = APIRouter()
parser = None


class RunRequest(BaseModel):
    argv: Optional[List[str]] = None
    cmd: Optional[str] = None


@router.post("/run")
async def run(req: RunRequest):
    argv = req.argv
    if req.cmd and not argv:
        argv = shlex.split(req.cmd)

    if not isinstance(argv, list):
        raise HTTPException(
            status_code=400, detail="Provide 'argv' (list) or 'cmd' (string)"
        )

    try:
        ensure_data_dir()

        global parser
        if parser is None:
            parser = build_parser()

        try:
            args = parser.parse_args(argv)
        except SystemExit as se:
            buf = io.StringIO()
            parser.print_help(file=buf)
            return JSONResponse(
                status_code=400, content={"output": buf.getvalue(), "exit": se.code}
            )

        console = Console(record=True)

        if hasattr(args, "handler"):
            try:
                result = args.handler(args, console)
                if hasattr(result, "__await__"):
                    await result
            except Exception as e:
                tb = traceback.format_exc()
                return JSONResponse(
                    status_code=500,
                    content={
                        "output": console.export_text(),
                        "error": str(e),
                        "traceback": tb,
                    },
                )
        else:
            buf = io.StringIO()
            parser.print_help(file=buf)
            return {"output": buf.getvalue(), "exit": 0}

        return {"output": console.export_text(), "exit": 0}
    except Exception as e:
        tb = traceback.format_exc()
        return JSONResponse(status_code=500, content={"error": str(e), "traceback": tb})


def create_app() -> FastAPI:
    app = FastAPI(title="srl CLI HTTP API")
    app.include_router(router)
    return app


def run_server(host: str = "127.0.0.1", port: int = 8080, reload: bool = False):
    app = create_app()
    uvicorn.run(app, host=host, port=port, reload=reload)
