from ..generic_agent import ConfiguredAgent


class Visualizer(ConfiguredAgent):
    prompt = "You are a visualization specialist. Recommend or produce a clear visualization suited to the supplied data."

    def __init__(self):
        super().__init__("visualizer")
