# ADR 0003 — Selection filter rejects bodies not created by this addon

## Status
Accepted

## Context
The unified dialog accepts either sketch curves (create) or existing cable bodies (edit). A user could accidentally select a generic pipe or sweep body — one the addon did not create and has no stored parameters on.

## Decision
The selection filter uses Fusion's selection filter API to accept only sketch curves and Addon-Tagged Bodies (bodies carrying this addon's custom attributes). Generic bodies cannot be selected as edit targets.

## Consequences
- Prevents silent data loss (overwriting a structural body the user didn't intend to touch).
- Prevents confusing partial-edit states where some fields are populated and others are not.
- Users cannot "adopt" existing pipe bodies into addon management. If they want a cable managed by the addon, they must recreate it via the addon. This is the correct trade-off — cable routing bodies should be created intentionally.
