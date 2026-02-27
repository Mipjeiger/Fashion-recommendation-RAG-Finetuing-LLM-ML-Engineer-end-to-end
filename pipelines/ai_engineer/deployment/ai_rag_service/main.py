from fastapi import FastAPI
from langserve import add_routes

from .rag_chain import rag_chain

app = FastAPI(title="E-Commerce RAG Service")

add_routes(
    app,
    rag_chain,
    path="/rag"
)