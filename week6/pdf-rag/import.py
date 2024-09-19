from vertexai.preview import rag
from vertexai.preview.generative_models import GenerativeModel, Tool
import vertexai

# Create a RAG Corpus and Import Files

# TODO(developer): Update below lines
PROJECT_ID = "YOUR_PROJECT_ID"
DISPLAY_NAME = "YOUR_CORPUS_DISPLAY_NAME"
paths = ["gs://rag-pdf-store/files-to-import"] //Google Cloud Storage Folder or Drive Folders only

# Initialize Vertex AI API once per session
vertexai.init(project=PROJECT_ID, location="us-central1")

# Create RagCorpus
# Configure embedding model, for example "text-embedding-004".

embedding_model_config = rag.EmbeddingModelConfig(
    publisher_model="publishers/google/models/text-embedding-004"
)

rag_corpus = rag.create_corpus(
    display_name=DISPLAY_NAME,
    embedding_model_config=embedding_model_config,
)

print(rag_corpus.name)

# Import Files to the RagCorpus
response = rag.import_files(
    rag_corpus.name,
    paths,
    chunk_size=512,  # Optional
    chunk_overlap=100,  # Optional
    max_embedding_requests_per_min=900,  # Optional
)

print(response)
