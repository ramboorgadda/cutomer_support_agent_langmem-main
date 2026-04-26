from __future__ import annotations
from typing import Any
import hashlib
import os
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitter import RecursiveCharacterTextSplitter
from customer_support_agent.core.settings import Settings


class KnowledgeBaseService:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = chromadb.PersistentClient(path=self._settings.chroma_rag_path)
        self._embedding_function = self._build_embedding_function()
        self._collection_name = "support_kb_gemini" if settings.google_api_key else "support_kb"
        self._splitter = RecursiveCharacterTextSplitter(chunk_size=settings.rag_chunk_size, 
                                                    chunk_overlap=settings.rag_chunk_overlap)
        self._collection = self._client.get_or_create_collection(name=self._collection_name, 
                                                                embedding_function=self._embedding_function)


    def _build_embedding_function(self) -> Any:
        if self._settings.google_api_key:
            os.environ.setdefault("GOOGLE_API_KEY", self._settings.google_api_key)
            try:
                return  embedding_functions.GoogleGeminiEmbeddingFunction(model_name=self._settings.effective_google_embedding_model)
            except Exception as e:
                print(f"Failed to initialize Google Gemini embedding function: {e}")
                return None
        return embedding_functions.GoogleGeminiEmbeddingFunction()
    
    def ingest_directory(self,directory: Path,clear_existing: bool = False) -> dict[str, int]:
        if clear_existing:
            self._client.delete_collection(name=self._collection_name)
            self._collection = self._client.get_or_create_collection(name=self._collection_name, 
                                                                    embedding_function=self._embedding_function)
        source_files = sorted(Path(directory).glob("**/*.*"))
        
        docs : list[str] = []
        ids: list[str] = []
        metadats: list[dict[str, Any]] = []
        
        for file_path in source_files:
            if file_path.is_file():
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                metadata = {"source": str(file_path)}
                chunks = self._splitter.split_text(content)
                docs.extend(chunks)
                ids.extend([hashlib.sha256((chunk + str(metadata)).encode()).hexdigest() for chunk in chunks])
                metadats.extend([metadata] * len(chunks))
        if docs:
            self._collection.upsert(documents=docs, metadatas=metadats, ids=ids)
        return {
            "files_indexed": len(source_files),
            "chunks_indexed": len(docs),
            "collection_count": self._collection.count()
        }
    def add_knowledge(self, content: str, metadata: dict[str, Any]) -> None:
        chunks = self._splitter.split_text(content)
        ids = [hashlib.sha256((chunk + str(metadata)).encode()).hexdigest() for chunk in chunks]
        self.collection.add(
            documents=chunks,
            metadatas=[metadata] * len(chunks),
            ids=ids
        )
