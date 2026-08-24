# Targeted COTS CAD Implementation Gate

## Formal disposition

**TARGETED COTS REQUIRES PHYSICAL TEST BEFORE CAD**

Clean baseline status: **CLEAN CAD BASELINE TECHNICALLY COMPLETE — OWNER CREO ACCEPTANCE PENDING**.

No production CAD, AP242 master, source geometry, route, motion, state-parity, render or presentation artifact was modified during Phase 4.

## Item gates

- **A — ACCEPT FOR CAD IMPLEMENTATION:** Rotor Clip `DC-4SS` only. Implement only as a bounded post-acceptance revision to the two existing mating grooves, then revalidate local retention/tool clearance.
- **B — ACCEPT PENDING OWNER / VENDOR APPLICATION APPROVAL:** Smalley `VSM-8-S16`. Obtain exact `-S16`, certificate and submerged/service response; owner accepts the pivot-pin groove revision.
- **C — ACCEPT FOR PHYSICAL TEST BEFORE CAD:** Swagelok `316L-50DF4-150`; HIKO `87640_OLV_ONE`.
- **D — DEFER — INSUFFICIENT EVIDENCE:** none.
- **E — REJECT — RETURN FUNCTION TO CUSTOM BASELINE:** Gutekunst `VD-244`; igus `GFM-081013-08`; igus `GTM-0815-005`.

Counts: A `1`; B `1`; C `2`; D/E `3`.

## Required owner decisions

1. Accept or reject clean CAD baseline commit `8c594781e27b0597a71957082fb64f152cacfcd9` after Creo review.
2. Accept or reject bounded groove revisions for the Smalley and Rotor Clip rings after vendor responses.
3. Approve or reject a field-reset concept based on certified pressure-module exchange; operator field refill remains unverified.
4. After test evidence, accept or reject the Swagelok and HIKO selections for any CAD implementation.

## Release boundary

Projected functional COTS is **24/114 = 21.05%** only if A/B/C items ultimately qualify. Four new custom adapter lines reduce the accepted 14-definition conversion to a net custom line reduction of 10. Delivered-item CoCs verified: 0. CAD substitutions implemented: 0. Product status: **NOT RELEASED**.

## Exact next action

Obtain owner authorization to send the four prepared Priority-1 RFQs; request certificate/application/CAD evidence without purchasing. In parallel, owner reviews the clean CAD baseline. Do not start CAD until owner acceptance and the C-item physical-test gates are closed.
