# STINGRAY I5-S DF8 Stakeholder System Review — Source Notes

## Scope and status

This deck is a stakeholder communication artifact, not a release certificate. Architecture, part identities, measured endpoint metrics, and vendor links are grounded in the preserved R2 handoff package. The latest owner-directed Codex run was stopped at a safe boundary after validating motion through 55°; 56°–80° remains unvalidated in that latest rerun. Earlier handoff artifacts include a prior 81-sample motion dataset that ended in terminal audit/release-gate failure; it is not presented as current release PASS evidence.

The current remote GitHub `main` branch contains only the initial README; the deck is intended for a documentation branch so it does not overwrite local Codex engineering work.

## Slide-by-slide source map

1. Current deployed AP242 master; latest manual-inspection status.
2. `CURRENT_STATE.json`; current authoring inventory; controlling commission; latest manual-inspection checkpoint.
3. Controlling commission; `AFTER_IMAGE_01_PRODUCT_BOUNDARY.png`.
4. Controlling commission; current authoring inventory.
5. Controlling commission §§15–16; authoring inventory.
6. Current STOWED AP242 master; `CURRENT_STATE.json`; stowed authoring inventory.
7. Current DEPLOYED AP242 master; `CURRENT_STATE.json`; deployed-cohesion evidence.
8. Current nose/forward-shell/ballast definitions; water-port evidence.
9. Current authoring inventory; attachment/connectivity evidence; route-clearance and route/sear views.
10. Controlling arm requirements; arm definitions; arm-root evidence.
11. Crosshead/link/guide definitions; measured crosshead travel; crosshead-retention evidence.
12. Controlling commission §9.1; GS-19 BUY definition; actuator/spring evidence.
13. Controlling commission §§3.3 and 9.2; HBD-15 BUY definition; actuator/spring evidence.
14. Controlling commission §3.2; controlled custom backup-spring definition; actuator/spring evidence.
15. Stow-dog/sear definitions; intentional-fit register; route/sear evidence.
16. Hard-stop/lock requirements; fixed-stop/stop-pad/lock definitions; arm-root evidence.
17. V80040 / trigger-housing / water-inlet definitions; water-port evidence.
18. Leland 81121 / Swagelok SS-CHS2-1 / puncture/manifold definitions; route evidence.
19. WP04 ejector/buoy definitions; deployed buoy evidence.
20. Attachment/connectivity inventory; terminal-chain evidence.
21. `connectivity_summary.json`; attachment inventory; terminal-chain and product-boundary evidence.
22. Current BUY definitions 1–9.
23. Current BUY definitions 10–17.
24. Current authoring inventory.
25. Controlling commission §§3–4; `CURRENT_STATE.json` dimensions/mass.
26. `WP02_ENGINEERING_CALCULATION_REPORT.md`; `WP02_KINEMATIC_REGISTER.csv`; `WP02_SPRING_TRADE_AND_CORRECTION.csv`; `WP02_DYNAMIC_CASE_RESULTS.csv`.
27. Final-cycle validation evidence under `work/final_analysis/validation/`; per-solid final-source audits; `CURRENT_STATE.json`; latest manual-inspection status.
28. `CURRENT_STATE.json` endpoint metrics; latest manual-inspection checkpoint.
29. `CURRENT_STATE.json`; latest manual-inspection checkpoint; latest Codex repository reconciliation.
30. Final packaging requirements; latest manual-inspection checkpoint.
31. Synthesis of slides 2–30; no new engineering claims.

## Vendor coverage

- **SSCF-M3-6-A4** — Accu — qty 4 — M3 X 6 full-thread socket cap screw — https://www.accu.co.uk/metric-cap-head-screws/3973-SSCF-M3-6-A4
- **SSCF-M3-10-A4** — Accu — qty 14 — M3 X 10 full-thread socket cap screw — https://www.accu.co.uk/us/socket-cap-head-screws/3975-SSCF-M3-10-A4
- **SSK-M3-6-A4-P80** — Accu — qty 10 — M3 X 6 socket countersunk screw, Precote 80 — https://www.accu.co.uk/countersunk-socket-head-screws/795226-SSK-M3-6-A4-P80
- **SSCA-M3-8-A4-BL** — Accu — qty 26 — M3 X 8 captive socket cap screw — https://www.accu.co.uk/cap-head-captive-screws/779966-SSCA-M3-8-A4-BL
- **SSCL-M4-8-A4** — Accu — qty 1 — M4 X 8 low-head socket cap screw — https://www.accu.co.uk/low-head-cap-screws/8885-SSCL-M4-8-A4
- **HDP-3-8-A1** — Accu — qty 6 — 3 mm X 8 mm dowel pin — https://www.accu.co.uk/dowel-pins/72653-HDP-3-8-A1
- **HTP-3-30-A1** — Accu — qty 1 — 3 mm X 30 mm taper pin — https://www.accu.co.uk/taper-pins/389498-HTP-3-30-A1
- **HEC-10-A4** — Accu — qty 1 — 10 mm external circlip — https://www.accu.co.uk/external-circlips/629101-HEC-10-A4
- **LELAND-81121** — Leland Gas Technologies — qty 4 — 12 g CO₂ cartridge — https://www.lelandgas.com/product-page/81121-cartridge-small-x-xml-x-xxg-gas
- **SS-CHS2-1** — Swagelok — qty 3 — 316 SS poppet check valve — https://products.swagelok.com/en/c/fixed-pressure/p/SS-CHS2-1
- **V80040** — Nordson MEDICAL / Halkey-Roberts — qty 1 — water-sensitive bobbin — https://fluid-components.nordsonmedical.com/Resources/Orders/
- **ROTOR-CLIP-DC-4SS** — Rotor Clip — qty 6 — crescent retaining ring for 4 mm shaft — https://www.rotorclip.com/product/dc-4/
- **GS-19-50-V4A-B8-B8** — ACE Controls — qty 1 — gas-spring assembly — https://www.acecontrols.com/us/calculations/gas-spring-configurator.html
- **GS-19-50-V4A-B8-B8-ROD-CHILD** — ACE Controls — qty 1 — moving rod articulation child — https://www.acecontrols.com/us/calculations/gas-spring-configurator.html
- **HBD-15-25-AA-P** — ACE Controls — qty 1 — hydraulic damper assembly — https://www.acecontrols.com/us/products/motion-control/hydraulic-dampers/hbd-15-to-hbd-40/hbd-15/hbd-15-25.html
- **HBD-15-25-AA-P-ROD-CHILD** — ACE Controls — qty 1 — moving rod articulation child — https://www.acecontrols.com/us/products/motion-control/hydraulic-dampers/hbd-15-to-hbd-40/hbd-15/hbd-15-25.html
- **GN-615.3-M3-KN-PFB** — JW Winco / Ganter — qty 4 — M3 stainless ball plunger — https://www.jwwinco.com/en-us/products/3.1-Indexing-locking-blocking-with-pins-and-ball-shaped-elements/Spring-plungers/GN-615.3-Steel-Stainless-Steel-Ball-Plungers-with-thread-locking-with-ball-with-internal-hexagon

## Known source gaps / caveats

- Latest local Codex technical views generated after the handoff are not accessible from this ChatGPT runtime; the deck uses the preserved R2 corrective technical views plus fresh renders from the preserved endpoint STEP masters.
- The current local state-parity/provenance disposition should be rechecked before formal release; the preserved handoff recorded unresolved parity rows before later Codex work.
- Physical/environmental qualification, calibrated damper force-speed performance, and final manufacturing qualification are not established by the CAD evidence and are not presented as completed tests.
