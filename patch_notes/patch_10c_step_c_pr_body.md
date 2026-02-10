## Patch 10-C Step C — Staff/Manager Guard Enhancements

- Title: Patch 10-C Step C: Staff/Manager Guard Enhancements

- Summary
  - Complete Step C for the Staff/Manager Guard workstream: tighten access controls around staff workflows, prepare test coverage, and lay groundwork for Patch 10-D health/warnings clean-up.

- What changed
  - Scaffolding for Step C tasks and test coverage related to staff guards.
  - Placeholder tests (to be implemented in Step C) around admin gating for staff flows.
  - An explicit in_progress mark for Patch 10-C Step C in the patch log to reflect ongoing work.

- Rationale
  - Strengthen security by ensuring only authorized admins can perform sensitive staff-flow operations; reduce risk of privilege escalation and leakage of admin controls.

- Testing
  - Plan to add tests validating admin gating across staff flows (Manager, Kitchen, Packer, Courier).
  - Will extend existing is_admin_callback/tests and dependencies to cover Step C scenarios.

- Migration/Compatibility
  - No database migrations in this step; no schema changes planned.

- Documentation
  - Update CHANGELOG and PR notes to reflect Step C progress.

- Risks
  - Low risk: changes are primarily access-control guards and test scaffolding; potential for false negatives in tests if mocks are incomplete.

- Rollback plan
  - If issues arise, revert this PR or squash reverts to previous guard behavior; ensure admin guards revert to prior state.

- How to verify
  - Run existing test suite: pytest -q
  - Run new Step C test scaffolds once implemented to confirm coverage and no regressions.

- Next steps
  - Implement Step C changes in code (guard integration for staff flows).
  - Add concrete tests for staff flows in 10-C Step C.
  - Prepare Patch 10-D plan (health warnings fix) and update PR body accordingly.
