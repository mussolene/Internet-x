# Evidence Pack

## Thesis

Internet-X is a strong design point when the requirements are:

- stable identity above changing locators
- explicit control-plane visibility
- overlay deployment over today's Internet
- authenticated locator rebinding
- crypto agility and clear fallback semantics

## Evidence Summary

### Code Evidence

- `refimpl/` provides a working implementation with real classical authenticated and encrypted flows.
- `tests/` exercises success and failure paths, including retransmission and locator update.
- `scripts/run_demo.py` produces a complete packet exchange without manual setup.

### Specification Evidence

- `spec/` defines the architecture packet by packet and state by state.
- `paper/` and `ietf/` align with the implementation instead of speaking in a separate conceptual dialect.

### Research Evidence

- `docs/prior-art-survey.md` and `docs/novelty-matrix.md` show that the repository's novelty claim is intentionally narrowed.
- `docs/positioning.md` states exactly which claims are defensible.

### Formal/Semi-Formal Evidence

- `formal/bounded_model.py` checks bounded invariants for data-before-auth, downgrade detection, and locator-update preconditions.

## Where Internet-X Wins

- explicit identity-first semantics
- a clean mapping from architecture to packets
- authenticated locator update in a compact reference package
- transparency of hybrid/fallback decision points

## Where Internet-X Loses

- higher overhead than streamlined production transports
- weaker privacy due to visible metadata and stable identity
- no real PQ implementation yet
- no large-scale operational evidence
- no mature routing or mapping service layer

## Why “Near-Optimal” Is Conditional

Internet-X can only be called near-optimal under the repository's stated constraints. If the optimization target changes, the conclusion changes. That is why the repository avoids universal language and frames the result as a strong design point rather than a final answer to Internet architecture.
