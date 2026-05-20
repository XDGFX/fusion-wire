# ADR 0002 — ISO 6722 as the OD reference standard

## Status
Accepted

## Context
The user specifies cable size in mm² (cross-section). The Pipe feature requires an OD in mm. There is no universal mm²→OD mapping — it varies by construction standard and manufacturer. Options considered: hard-coded lookup table from a named standard, user-editable table, or user-entered OD directly.

## Decision
Use a hard-coded lookup table based on ISO 6722 (automotive single-core cable). Covers 0.5 mm² to 110 mm².

## Consequences
- OD values are predictable and consistent across all users without any configuration.
- Values may not match a specific user's actual cable stock exactly. This is acceptable for routing and visualisation — dimensional accuracy to the nearest fraction of a mm is not required.
- The table is isolated in a single module, making it straightforward to replace with a user-editable table in a future version.
