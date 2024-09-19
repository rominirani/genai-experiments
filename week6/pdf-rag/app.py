from vertexai.preview import rag
from vertexai.preview.generative_models import GenerativeModel, Tool

# Create a RAG Corpus, Import Files, and Generate a response
CORPUS_NAME = "projects/YOUR-PROJECT-ID/locations/us-central1/ragCorpora/YOUR-CORPUS-ID"
# EXAMPLE --> CORPUS_NAME = "projects/963355964121/locations/us-central1/ragCorpora/4611686018427387904"
# or use the code from below to get a list of your corpus'

CorporaList = rag.list_corpora()
if CorporaList:
    for corpora in CorporaList:
        print(corpora.name)
else:
    print("No Corpora found")

response = rag.retrieval_query(
    rag_resources=[
        rag.RagResource(
            rag_corpus=CORPUS_NAME
        )
    ],
    text="Which are some places to eat?",
    similarity_top_k=10,  # Optional
    vector_distance_threshold=0.5,  # Optional
)

print(response)

# Grounded response with Gemini

rag_retrieval_tool = Tool.from_retrieval(
    retrieval=rag.Retrieval(
        source=rag.VertexRagStore(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=CORPUS_NAME,  # Currently only 1 corpus is allowed.
                )
            ],
            similarity_top_k=3,  # Optional
            vector_distance_threshold=0.5,  # Optional
        ),
    )
)
# Create a gemini-pro model instance
rag_model = GenerativeModel(
    model_name="gemini-1.5-flash-001", tools=[rag_retrieval_tool]
)

# Generate response
response = rag_model.generate_content("The Corpus contains a document which is a guide to Florence. Please look into the document and tell me about some of the listed places to eat?")
print(response.text)
