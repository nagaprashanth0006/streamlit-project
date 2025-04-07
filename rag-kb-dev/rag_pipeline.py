from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.llms import Ollama
from llama_index.embeddings import SentenceTransformerEmbedding


def build_query_engine():
    documents = SimpleDirectoryReader("docs/").load_data()
    llm = Ollama(model="llama3")
    service_context = ServiceContext.from_defaults(
        llm=llm, embed_model=SentenceTransformerEmbedding(model_name="all-MiniLM-L6-v2")
    )
    index = VectorStoreIndex.from_documents(documents, service_context=service_context)
    return index.as_query_engine()
