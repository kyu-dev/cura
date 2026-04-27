"""Web-based RAG retriever tool for Cura."""

import threading

from langchain.tools import tool
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore, VectorStoreRetriever
from langchain_mistralai import MistralAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

_URLS = [
    'https://www.lesrecettesdevirginie.com/2026/02/pates-aux-cinque-p.html',
    'https://www.elle.fr/Elle-a-Table/Recettes-de-cuisine/Salade-Cesar-4122645'
]

_RETRIEVER: VectorStoreRetriever | None = None
_RETRIEVER_LOCK = threading.Lock()


def _load_documents() -> list[Document]:
    """Load and flatten documents from all configured URLs."""
    docs = [WebBaseLoader(url).load() for url in _URLS]
    return [doc for sublist in docs for doc in sublist]


def _build_retriever() -> VectorStoreRetriever:
    """Split documents, embed them, and return a retriever."""
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=100, chunk_overlap=50
    )
    chunks = splitter.split_documents(_load_documents())
    vectorstore = InMemoryVectorStore.from_documents(
        documents=chunks, embedding=MistralAIEmbeddings()
    )
    return vectorstore.as_retriever()


def get_retriever() -> VectorStoreRetriever:
    """Return the retriever, building it once on first call."""
    global _RETRIEVER  # pylint: disable=global-statement
    if _RETRIEVER is None:
        with _RETRIEVER_LOCK:
            if _RETRIEVER is None:
                _RETRIEVER = _build_retriever()
    return _RETRIEVER


@tool
def retrieve_blog_posts(query: str) -> str:
    """Search and return recipes and cooking information from the configured recipe websites."""
    docs = get_retriever().invoke(query)
    return "\n\n".join(doc.page_content for doc in docs)
