from ..generic_agent import ConfiguredAgent


class UnitTester(ConfiguredAgent):
    prompt = "You are a unit-testing specialist. Analyze the task and produce focused, executable unit tests."

    def __init__(self):
        super().__init__("unit_tester")
