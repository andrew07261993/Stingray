# Controlled Post-Generation Status Transition Procedure

Status: **REQUIRED FOR REVIEWED HANDOFF REPRODUCTION**

`complete_product_definition_reports.py` is deliberately a **pre-review template generator**. It
creates conservative `TEMPLATE - PENDING` states and must never be used by itself to claim that the
executive artifacts, reviews, extraction, or delivery have passed.

## Ordered evidence states

1. Generate reports and per-part artifacts, stage the byte-verified source/CAD/validation trees, then
   generate and render-check the PPTX and PDF.
2. Run `validate_complete_product_definition.py`. Only a zero-exit audit may transition the internal
   package-review rows to PASS for the non-release package.
3. Run `freeze_independent_review_packet.py`; provide that manifest-bound packet to a fresh-context
   reviewer. Record the review result and findings without changing the frozen candidate.
4. Correct every package CRITICAL/MAJOR/MINOR finding, rerun affected checks, regenerate the dependency
   inventory via `stage_complete_product_definition.py`, re-audit, re-freeze, and return it for closure.
5. Run `finalize_complete_product_definition.py` to create a preliminary ZIP. Extract it to a new clean
   directory and run `verify_extracted_complete_product_definition.py` before any rebuild output is made.
6. From the extracted `11_BUILD_AND_REPRODUCIBILITY/rebuild_source` root, rebuild the PAIR and rerun
   endpoint, five-angle, and full-motion gates with fresh output names. Compare the rebuilt inventories,
   mass properties, occurrence counts, and semantic gate results to the frozen evidence. Do not claim
   AP242 byte identity.
7. Add the extraction/rebuild audit only after it passes; update traceability/review ledgers to the actual
   evidence state; re-run the internal audit and independent status closure; then regenerate final hashes
   and the deterministic ZIP. A final clean integrity extraction must match every manifest entry exactly.

All status edits are evidence transitions, not product-release waivers. Product release remains FAIL
while the non-release exception report lists open external, manufacturing, and physical gates.
