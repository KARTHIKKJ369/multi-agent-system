from multi_agent_system.utils.observability import Observability


def test_span_is_safe_when_observability_is_disabled():
    telemetry = Observability()
    with telemetry.span("unit.test", item="value"):
        pass
