"""Bounded protocol-state checker for Internet-X invariants."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable


EVENTS = ["INIT", "INIT_ACK", "KEM_OK", "KEM_BAD", "AUTH_OK", "DATA", "LOCATOR_UPDATE", "RESET"]


@dataclass(frozen=True)
class ModelState:
    phase: str = "START"
    flow_established: bool = False
    locator_bound: bool = False
    downgrade_detected: bool = False
    data_accepted: bool = False



def step(state: ModelState, event: str) -> ModelState:
    if event == "RESET":
        return ModelState()
    if state.phase == "START" and event == "INIT":
        return ModelState(phase="INIT_SENT")
    if state.phase == "INIT_SENT" and event == "INIT_ACK":
        return ModelState(phase="INIT_ACKED")
    if state.phase == "INIT_ACKED" and event == "KEM_BAD":
        return ModelState(phase="ERROR", downgrade_detected=True)
    if state.phase == "INIT_ACKED" and event == "KEM_OK":
        return ModelState(phase="KEM_VERIFIED")
    if state.phase == "KEM_VERIFIED" and event == "AUTH_OK":
        return ModelState(phase="ESTABLISHED", flow_established=True, locator_bound=True)
    if state.phase == "ESTABLISHED" and event == "DATA":
        return ModelState(
            phase="ESTABLISHED",
            flow_established=True,
            locator_bound=True,
            data_accepted=True,
        )
    if state.phase == "ESTABLISHED" and event == "LOCATOR_UPDATE":
        return ModelState(
            phase="ESTABLISHED",
            flow_established=True,
            locator_bound=True,
            data_accepted=state.data_accepted,
        )
    return state


def admissible_trace(trace: Iterable[str]) -> bool:
    state = ModelState()
    for event in trace:
        next_state = step(state, event)
        if next_state == state and event != "RESET":
            return False
        state = next_state
    return True



def invariant_no_data_before_auth(trace: Iterable[str]) -> bool:
    state = ModelState()
    for event in trace:
        if event == "DATA" and not state.flow_established:
            return False
        state = step(state, event)
    return True



def invariant_bad_kem_detects_downgrade(trace: Iterable[str]) -> bool:
    state = ModelState()
    for event in trace:
        expect_detection = event == "KEM_BAD" and state.phase == "INIT_ACKED"
        state = step(state, event)
        if expect_detection and not state.downgrade_detected:
            return False
    return True



def invariant_locator_update_requires_established(trace: Iterable[str]) -> bool:
    state = ModelState()
    for event in trace:
        if event == "LOCATOR_UPDATE" and not state.flow_established:
            return False
        state = step(state, event)
    return True



def run_model_check(max_depth: int = 6) -> dict[str, int]:
    checked = 0
    for depth in range(1, max_depth + 1):
        for trace in product(EVENTS, repeat=depth):
            if not admissible_trace(trace):
                continue
            checked += 1
            assert invariant_no_data_before_auth(trace), trace
            assert invariant_bad_kem_detects_downgrade(trace), trace
            assert invariant_locator_update_requires_established(trace), trace
    return {"checked_traces": checked, "max_depth": max_depth}


if __name__ == "__main__":
    print(run_model_check())
