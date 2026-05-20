# ADR 0001 — Edit cables via delete-and-recreate, not parametric Custom Feature

## Status
Accepted

## Context
Cables need to be editable after creation (e.g. change cross-section or colour). Fusion's API offers two approaches: the Custom Feature API (parametric, timeline-integrated) or storing parameters as custom attributes on a plain body and replacing it on edit.

## Decision
Use delete-and-recreate. On edit, the addon reads stored custom attributes from the selected body, pre-populates the dialog, and on confirm: deletes the old body and sweeps a new one with the updated parameters.

## Consequences
- The Fusion timeline shows a plain Pipe feature, not a named custom feature. Users cannot double-click the timeline entry to re-edit.
- The toolbar button is the single re-entry point for editing — select an Addon-Tagged Body, open the dialog, adjust, confirm.
- Avoids the Custom Feature API, which is complex, fragile across Fusion versions, and poorly documented.
- The UX feels like an edit; the implementation is a replace. This is invisible to the user.
