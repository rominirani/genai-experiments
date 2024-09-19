from typing import Dict
import pytest
from deepeval import assert_test
from deepeval.metrics.ragas import (
    RAGASContextualPrecisionMetric,
    RAGASFaithfulnessMetric,
    RAGASContextualRecallMetric,
    RAGASAnswerRelevancyMetric,
)
from deepeval.metrics import BiasMetric
from deepeval.test_case import LLMTestCase
from deepeval.models.base_model import DeepEvalBaseLLM

from vertexai.preview import rag
from vertexai.preview.generative_models import GenerativeModel, Tool

from langchain_google_vertexai import (
    ChatVertexAI,
    HarmBlockThreshold,
    HarmCategory
)

from ragas.llms import LangchainLLMWrapper

CORPUS_NAME = "projects/963355964121/locations/us-central1/ragCorpora/4611686018427387904"

class GoogleVertexAI(DeepEvalBaseLLM):
    """Class to implement Vertex AI for DeepEval"""
    def __init__(self, model):
        self.model = model

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        return chat_model.invoke(prompt).content

    async def a_generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        res = await chat_model.ainvoke(prompt)
        return res.content

    def get_model_name(self):
        return "Vertex AI Model"

# Initilialize safety filters for vertex model
# This is important to ensure no evaluation responses are blocked
safety_settings = {
    HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
}

#TODO : Add values for project and location below
custom_model_gemini = ChatVertexAI(
    model_name="gemini-1.0-pro-002"
    , safety_settings=safety_settings
    , project= "romin-gcp-experiments"
    , location= "us-central1" #example : us-central1
)

# initiatialize the  wrapper class
vertexai_gemini = GoogleVertexAI(model=custom_model_gemini)

#######################################
# Initialize metrics with thresholds ##
#######################################
bias = BiasMetric(model=vertexai_gemini, threshold=
0.5
)
contextual_precision = RAGASContextualPrecisionMetric(model=vertexai_gemini,threshold=
0.5
)
contextual_recall = RAGASContextualRecallMetric(model=vertexai_gemini,threshold=
0.5
)
answer_relevancy = RAGASAnswerRelevancyMetric(model=vertexai_gemini,threshold=
0.5
)
faithfulness = RAGASFaithfulnessMetric(model=vertexai_gemini,threshold=
0.5
)

#######################################
# Specify evaluation metrics to use ###
#######################################
evaluation_metrics = [
  bias,
  answer_relevancy,
  #faithfulness,
  #contextual_precision,
  #contextual_recall,
]

#######################################
# Specify inputs to test RAG app on ###
#######################################
input_output_pairs = [
  {
    "input": "which are some places to eat?",
    "expected_output": "Trattoria CasaLinga, Trattoria da Mario,Teatro del Sale", 
  },
  {
    "input": "Which are top attractions in Florence?",
    "expected_output": "Tour the Uffizi Gallery, Ponte Vecchio, Galleria dell Academia", 
  }
]

#######################################
# Loop through input output pairs #####
#######################################
@pytest.mark.parametrize(
    "input_output_pair",
    input_output_pairs,
)

def test_llamaindex(input_output_pair: Dict):
    input_used = input_output_pair.get("input", None)
    expected_output = input_output_pair.get("expected_output", None)

    # Hypothentical RAG application for demonstration only. 
    # Replace this with your own RAG implementation.
    # The idea is you'll be generating LLM outputs and
    # getting the retrieval context at evaluation time for each input
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
    response = rag_model.generate_content(input_used)
    actual_output = response.text

    retrieval_context = ["Only restaurants should be listed"]

    test_case = LLMTestCase(
        input=input_used,
        actual_output=actual_output,
        retrieval_context=retrieval_context,
        expected_output=expected_output
    )
    
    # assert test case
    assert_test(test_case, evaluation_metrics)
