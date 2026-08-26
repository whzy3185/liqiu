# Industrial GB Sample-Weighting Gate

## Prerequisite

Prompt 9 was authorized only if Prompt 8 showed at least a local positive
structural-feature signal.

Prompt 8 instead found:

- overall matched Macro-F1 delta: `-0.0065`;
- dataset mean deltas: APS `-0.0004`, SECOM `+0.0000`, Steel `-0.0190`;
- no dataset averaged a meaningful positive gain;
- no matched cell reached +3pp;
- decision: `KILL`.

## Decision

**NOT RUN / KILL BY PREREQUISITE**

W1--W4 were not searched. Continuing after this gate would tune a second GB
module to rescue a negative first mechanism and would invalidate the intended
application-scout discipline.

