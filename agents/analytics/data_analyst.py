from ..generic_agent import ConfiguredAgent


class DataAnalyst(ConfiguredAgent):
    prompt = "You are a data-analysis specialist. Analyze supplied data, state assumptions, and report defensible findings."

    def __init__(self):
        super().__init__("data_analyst")
