# Contributing

## Development Principles

- preserve the identity-first architecture
- do not overclaim relative to evidence
- keep packet formats and state-machine docs aligned with code
- distinguish clearly between real security and simulated transition hooks

## Before Opening A Change

Run:

```bash
make test
make demo
python3 formal/bounded_model.py
make paper-check
```

## Change Discipline

- update `spec/` if packet fields or state transitions change
- update `docs/positioning.md` if claim surface changes
- update `docs/evidence-pack.md` if evaluation changes materially
- keep `prototype/` as legacy context unless there is a specific reason to revise it
