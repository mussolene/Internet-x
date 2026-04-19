# Gap Analysis

## Starting Gaps

The original repository had five major gap classes.

### 1. Publication Gap

- The paper draft was placeholder text.
- The IETF draft was empty.
- No novelty matrix or prior-art survey existed.

### 2. Specification Gap

- The architecture was described, but not as a complete, internally cross-linked specification set.
- Mobility and locator update were conceptually central but insufficiently defined.
- Error handling, downgrade logic, and cryptographic agility were not specified in enough detail.

### 3. Prototype Gap

- The old prototype was a clear teaching artifact but did not provide a real security baseline.
- No authenticated locator update existed.
- No multi-node test coverage existed.

### 4. Evidence Gap

- There was no formal or semi-formal model.
- No local benchmark harness existed.
- No evidence pack tied claims to runnable commands.

### 5. Honesty Gap

- The repository risked being read as broader or more novel than the evidence justified.
- “Post-quantum-ready” was under-specified relative to implementation reality.

## Resolution Strategy

The repository was upgraded by separating concerns explicitly:

- `prototype/` remains legacy educational context.
- `refimpl/` is the current runnable baseline.
- `spec/` describes the current design and points out where PQ remains simulated.
- `docs/` holds positioning, prior art, evaluation, and limitations.
- `paper/` and `ietf/` are written against the actual code and specs.
- `formal/` captures bounded invariants rather than overstating proof strength.

## Gaps That Remain

These are deliberate, not accidental.

- No global naming or locator service is implemented.
- No real ML-KEM or ML-DSA is integrated.
- No full routing or path-selection substrate exists.
- No kernel transport integration exists.
- No Internet-scale or WAN evaluation exists.

## Why Those Remaining Gaps Are Acceptable

The repository goal is a credible research package, not a production stack. Under that scope, the unresolved items are documented limitations rather than hidden defects. The repository now distinguishes clearly between:

- real reference implementation behavior,
- architectural intent,
- and future research directions.
