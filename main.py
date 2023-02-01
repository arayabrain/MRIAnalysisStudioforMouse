import argparse
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware

from backend.routers import auth
from studio.routers import (algolist, experiment, files, hdf5, outputs, params,
                            run)

load_dotenv()

DIRPATH = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(docs_url="/docs", openapi_url="/openapi")
app.include_router(auth.router, prefix='/auth')
app.include_router(algolist.router)
app.include_router(files.router)
app.include_router(outputs.router)
app.include_router(params.router)
app.include_router(run.router)
app.include_router(hdf5.router)
app.include_router(experiment.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory=f"{DIRPATH}/frontend/build/static"),
    name="static",
)

templates = Jinja2Templates(directory=f"{DIRPATH}/frontend/build")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    args = parser.parse_args()
    uvicorn.run("main:app", host=args.host, port=8000, reload=True)


if __name__ == "__main__":
    main()
