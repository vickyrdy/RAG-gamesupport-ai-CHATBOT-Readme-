import json
import re
import os
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from threading import Lock
from app.guardrails import check_input, redact_output
from fastapi import FastAPI
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver

from app.agent import ROOT, builder, text_of

chat_lock = Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    with SqliteSaver.from_conn_string(
        os.getenv("CHAT_DB_PATH", str(ROOT / "chat.sqlite"))
    ) as checkpointer:
        app.state.graph = builder.compile(
            checkpointer=checkpointer
        )
        yield


app = FastAPI(
    title="GameSupport AI",
    lifespan=lifespan,
)
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).resolve().parent / "static"),
    name="static",
)
@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(
        Path(__file__).resolve().parent / "static" / "index.html"
    )

class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    thread_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    blocked: bool = False


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    rejection = check_input(body.message)
    if rejection:
        return ChatResponse(
            answer=rejection,
            sources=[],
            blocked=True,
        )

       
    conversation_id = json.dumps([
        body.user_id, body.thread_id
    ])
    config = {
        "configurable": {
            "thread_id": conversation_id
        }
    }

    with chat_lock:
        result = app.state.graph.invoke(
            {
                "messages": [
                    HumanMessage(content=body.message)
                ]
            },
            config=config,
        )

        answer = redact_output(
        text_of(result["messages"][-1])
    )
    sources = sorted(set(
        re.findall(r"\[([^\[\]]+\.md)\]", answer)
    ))

    return ChatResponse(
        answer=answer,
        sources=sources,
    )