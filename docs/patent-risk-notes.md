# Patent Risk Notes

## Important Limitation

This document is a technical risk note, not legal advice. The search was deliberately limited and should not be treated as a freedom-to-operate opinion.

## Search Scope

A limited search was run across public patent search results for combinations of:

- host identity protocol
- locator/identifier separation
- mobility with stable identity
- overlay locator mapping

## Families Noted As Potentially Relevant

- [US8516243B2 - Host identity protocol method and apparatus](https://patents.google.com/patent/US8516243B2/en)
- [WO2012019525A1 - HIP-based communication method, system and device](https://patents.google.com/patent/WO2012019525A1/en)
- [US20100002660A1 - Multi-homing based mobile internet](https://patents.google.com/patent/US20100002660)
- several LISP- and locator/ID-separation-related families surfaced in adjacent results

## Technical Risk Interpretation

The risk is not that Internet-X reproduces one exact product claim. The risk is that broad patents in the following areas may overlap with deployment-minded embodiments:

- stable identity plus mobility management
- locator update procedures for ongoing flows
- mapping systems that bind persistent identifiers to changing locators
- tunnel or overlay control logic for roaming endpoints

## Why The Risk Is Not Repository-Blocking

This repository is:

- research-oriented,
- openly documented,
- explicit about prior art,
- and narrow in its release claims.

Those properties reduce but do not eliminate risk. Any move from research artifact to commercial deployment should trigger a real patent review.

## Practical Recommendation

If Internet-X progresses beyond research packaging, obtain counsel before:

- shipping a hosted locator service,
- integrating the protocol into a commercial endpoint product,
- or standardizing specific operational procedures that materially track existing claim language.
