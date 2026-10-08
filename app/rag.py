from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_documents() -> list[Document]:
    documents = []

    files = [
        (
            DATA_DIR / "logs" / "production.log",
            "production.log",
            "logs",
        ),
        (
            DATA_DIR / "documents" / "system_docs.md",
            "system_docs.md",
            "documentation",
        ),
        (
            DATA_DIR / "incidents" / "past_incidents.json",
            "past_incidents.json",
            "past_incident",
        ),
    ]

    for file_path, source, doc_type in files:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": source,
                    "type": doc_type,
                },
            )
        )

    return documents


def split_documents(
    documents: list[Document],
) -> list[Document]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )

    return splitter.split_documents(documents)


def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
    )


def create_vectorstore() -> Chroma:
    documents = load_documents()
    chunks = split_documents(documents)

    embeddings = get_embeddings()

    vectorstore = Chroma(
        collection_name="incident_knowledge",
        embedding_function=embeddings,
        persist_directory=str(VECTORSTORE_DIR),
    )

    vectorstore.add_documents(chunks)

    return vectorstore


def get_vectorstore() -> Chroma:
    embeddings = get_embeddings()

    return Chroma(
        collection_name="incident_knowledge",
        embedding_function=embeddings,
        persist_directory=str(VECTORSTORE_DIR),
    )


def search_knowledge_base(
    query: str,
    k: int = 4,
) -> list[Document]:

    vectorstore = get_vectorstore()

    return vectorstore.similarity_search(
        query,
        k=k,
    )


def build_context(
    documents: list[Document],
) -> str:

    context_parts = []

    for index, document in enumerate(documents, start=1):
        context_parts.append(
            f"""
--- Evidence {index} ---
Source: {document.metadata.get("source")}
Type: {document.metadata.get("type")}

{document.page_content}
"""
        )

    return "\n".join(context_parts)


def retrieve_context(
    query: str,
    k: int = 4,
) -> str:

    documents = search_knowledge_base(
        query=query,
        k=k,
    )

    return build_context(documents)