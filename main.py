import time
from typing import List

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import HttpUrl
from schemas.request import PredictionRequest, PredictionResponse
from utils.logger import setup_logger
from rag.rag import RAG
from config import seacher_folder_id, seacher_api_token, sammarizer_api_token

# Initialize
app = FastAPI()
logger = None


@app.on_event("startup")
async def startup_event():
    global logger
    logger = await setup_logger()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    body = await request.body()
    await logger.info(
        f"Incoming request: {request.method} {request.url}\n"
        f"Request body: {body.decode()}"
    )

    response = await call_next(request)
    process_time = time.time() - start_time

    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk

    await logger.info(
        f"Request completed: {request.method} {request.url}\n"
        f"Status: {response.status_code}\n"
        f"Response body: {response_body.decode()}\n"
        f"Duration: {process_time:.3f}s"
    )

    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )


@app.post("/api/request", response_model=PredictionResponse)
async def predict(body: PredictionRequest):
    try:
        await logger.info(f"Processing prediction request with id: {body.id}")

        rag = RAG(seacher_folder_id, seacher_api_token, sammarizer_api_token)

        
        answer_text, answer_num, links = rag.process(body.query)

        sources: List[HttpUrl] = [HttpUrl(link) for link in links]

        if answer_num == -1:
            response = PredictionResponse(
            id=body.id,
            answer=None,
            reasoning=answer_text,
            sources=sources,
        )
        else:    
            response = PredictionResponse(
                id=body.id,
                answer=answer_num,
                reasoning=answer_text,
                sources=sources,
            )

        await logger.info(f"Successfully processed request {body.id}")
        return response
    except ValueError as e:
        error_msg = str(e)
        await logger.error(f"Validation error for request {body.id}: {error_msg}, {body.query}")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        await logger.error(f"Internal error processing request {body.id}: {str(e)}, {body.query}")
        raise HTTPException(status_code=500, detail="Internal server error")
