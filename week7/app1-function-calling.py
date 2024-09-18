from vertexai.preview import reasoning_engines
from vertexai.generative_models import Tool, grounding
from model_config import safety_settings, model_kwargs, initVertexAI
from model_tools import  get_weather_forecast, get_location_data

initVertexAI()
MODEL_NAME = "gemini-1.5-flash-001"

agent = reasoning_engines.LangchainAgent(
    model=MODEL_NAME,
    tools=[get_weather_forecast, get_location_data],
)

response1 = agent.query(input="what is the current weather in Mumbai?")
print(response1)

#print(get_location_data(location_name="Mumbai, India"))
