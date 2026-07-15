from ..generic_agent import ConfiguredAgent


class DocumentationWriter(ConfiguredAgent):
    prompt = "You are a technical documentation specialist. Produce accurate, well-structured documentation for the assigned task."

    def __init__(self):
        super().__init__("documentation_writer")
