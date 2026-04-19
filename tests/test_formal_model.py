from formal.bounded_model import run_model_check


def test_bounded_model_invariants() -> None:
    result = run_model_check(max_depth=4)
    assert result["checked_traces"] > 0
