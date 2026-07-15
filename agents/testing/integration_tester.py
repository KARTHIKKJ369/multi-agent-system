from ..generic_agent import ConfiguredAgent


class IntegrationTester(ConfiguredAgent):
    prompt = "You are an integration-testing specialist. Analyze interfaces and produce reliable integration tests."

    def __init__(self):
        super().__init__("integration_tester")
