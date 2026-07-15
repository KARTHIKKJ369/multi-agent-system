from ..generic_agent import ConfiguredAgent


class KubernetesAgent(ConfiguredAgent):
    prompt = "You are a Kubernetes specialist. Produce safe, correct orchestration guidance for the assigned task."

    def __init__(self):
        super().__init__("kubernetes_agent")
