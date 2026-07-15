from ..generic_agent import ConfiguredAgent


class DockerAgent(ConfiguredAgent):
    prompt = "You are a Docker specialist. Produce safe, correct containerization guidance for the assigned task."

    def __init__(self):
        super().__init__("docker_agent")
