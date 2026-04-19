# Release Notes v0.1

Internet-X v0.1 is the first repository state that can reasonably be handed to another engineer as a coherent research package.

The exact audited research-demo baseline from that release is preserved at git tag `v0.1-research-demo`.

## Post-Audit Remediation

The current repository state adds the minimal control-plane maturity that was previously blocking `MVP-N1 READY`:

- separate authenticated control-plane service process
- signed registration for `Name`, `NodeID`, and `Locator`
- signed locator updates with lease expiry and monotonic locator versions
- service-backed demo, benchmark, and test flows

## Included In This Release

- identity-first protocol spec
- runnable reference implementation
- authenticated locator rebinding
- test suite and demo scripts
- prior-art and novelty analysis
- paper draft and IETF-style draft
- evidence pack and formal bounded model

## Claim Boundary For This Release

This release supports the claim that Internet-X is a credible identity-first overlay design point with explicit flow establishment, authenticated locator update, and a minimally real authenticated control plane under stated assumptions. It does not support claims of production deployment readiness, full novelty, or real post-quantum security.

## Recommended Evaluation Path

```bash
make test
make demo
python3 scripts/benchmark.py
python3 formal/bounded_model.py
```
