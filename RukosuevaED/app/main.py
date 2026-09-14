import logging
import sys
import time
import uuid
from itertools import count

from fastapi import FastAPI, HTTPException, Request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("method", "path", "status_code", "duration_ms", "request_id"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return str(payload).replace("'", '"')


def configure_logging() -> logging.Logger:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())

    logger = logging.getLogger("notes_app")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


logger = configure_logging()

app = FastAPI(title="Notes API")

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of HTTP requests received by the application",
    ["method", "path", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "app_request_duration_seconds",
    "Duration of HTTP requests in seconds",
    ["method", "path"],
)


@app.middleware("http")
async def metrics_and_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start
    route = request.scope.get("route")
    path_template = route.path if route is not None else request.url.path

    REQUEST_COUNT.labels(
        method=request.method,
        path=path_template,
        status_code=response.status_code,
    ).inc()
    REQUEST_LATENCY.labels(method=request.method, path=path_template).observe(duration)

    logger.info(
        "request completed",
        extra={
            "method": request.method,
            "path": path_template,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "request_id": request_id,
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response


class NoteIn(BaseModel):
    title: str
    content: str


class Note(NoteIn):
    id: int


_notes: dict[int, Note] = {}
_id_counter = count(1)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    from starlette.responses import Response

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/notes", response_model=list[Note])
def list_notes() -> list[Note]:
    return list(_notes.values())


@app.post("/notes", response_model=Note, status_code=201)
def create_note(note_in: NoteIn) -> Note:
    note_id = next(_id_counter)
    note = Note(id=note_id, **note_in.model_dump())
    _notes[note_id] = note
    logger.info("note created", extra={"path": "/notes", "method": "POST"})
    return note


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int) -> Note:
    note = _notes.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int) -> None:
    if note_id not in _notes:
        raise HTTPException(status_code=404, detail="Note not found")
    del _notes[note_id]
