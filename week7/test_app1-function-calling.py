from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import ToolCorrectnessMetric

from langchain_google_vertexai import (
    ChatVertexAI,
    HarmBlockThreshold,
    HarmCategory
)
from deepeval.models.base_model import DeepEvalBaseLLM

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

def test_llm():
    answer_relevancy_metric = ToolCorrectnessMetric(threshold=0.5)
    test_case = LLMTestCase(
        input="What is the weather in Mumbai?",
        actual_output="The current temperature in Mumbai is 26.8 degrees Celsius.",
        tools_called=["WeatherForecast","LocationDetails"],
        expected_tools=["WeatherForecast", "LocationDetails"]
    )
    assert_test(test_case, [answer_relevancy_metric])