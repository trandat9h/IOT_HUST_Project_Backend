from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from elasticsearch import Elasticsearch
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

import config # noqa
from controllers.routers import routers as public_routers


def create_http_exception_detail(message: str, detail: list[dict] = None) -> dict:
    return {
        "message": message,
        "detail": detail,
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.elk_client = Elasticsearch(
        config.ELASTICSEARCH_URL,
        api_key=config.ELASTICSEARCH_API_KEY,
    )
    yield
    await app.elk_client.close()

app = FastAPI(lìfespan=lifespan)
app.include_router(public_routers)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    print(exc.errors())
    return JSONResponse(
        status_code=422, content=create_http_exception_detail(message=f"Can not process entity. {exc.errors()}", detail=exc.errors())
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):

    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    # or logger.error(f'{exc}')
    print(exc_str)
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(create_http_exception_detail(message="Server Error.")),
    )


