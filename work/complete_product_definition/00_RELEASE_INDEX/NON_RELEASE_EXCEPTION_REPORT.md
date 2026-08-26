# Non-Release Exception Report

## Controlling disposition

**MAXIMUM-COMPLETE DIGITAL DEVELOPMENT PACKAGE - NOT RELEASED FOR FABRICATION, PROCUREMENT, QUALIFICATION, OR FIELD USE**

The frozen candidate is a coherent developmental digital assembly, not a production release.  The
following exceptions are evidence limitations or verified failures; none is reclassified as acceptable.

## Critical verified failure

The selected Leland 81121 cartridge contains 12 g CO2.  At 20 C and one atmosphere, the optimistic
ideal-gas upper bound is **6.559 L**, only
**10.9%** of the modeled 60 L buoy.  The ideal lower-bound mass for 60 L is
**109.772 g**, before losses, cooling, buoy back pressure, leakage, or
required gauge pressure.  The current inflation architecture therefore **FAILS**.

## Irreducible external evidence limitations

1. The exact installed Hydro 1F suffix, vendor-exact geometry, rated interface, flow curve, application
   approval, and custom patch/manifold definition are absent.
2. The primary source ZIP and two owner-decision filenames remained placeholders; no such attachments
   were supplied.
3. All eleven required reference screenshots were absent, preventing image-specific before/after closure.
4. Mission loads, proof factors, duty spectrum, impact/drop cases, and approved material allowables are
   absent; structural/fastener/fatigue margins are not calculable.
5. No wet inflation, breakaway, leak, proof/burst, stability, environmental, durability, dynamic, or
   assembly/service qualification evidence exists.
6. No released manufactured-part drawings, GD&T, tolerances, inspection plans, torque/locking data, or
   approved work instructions exist.
7. Identical seeded builds reproduce inventories and mass byte-for-byte but OCCT varies AP242
   presentation-style entity ordering, so the STEP masters are not byte-reproducible.

## Unaffected work completed

- Fresh endpoint, five-angle, and full one-degree exact-Boolean validation on frozen AP242 hashes.
- State parity, nominal envelope, occurrence identity, attachment/connection, mass/CG/inertia, BOM,
  materials/finishes, COTS provenance, procurement, design-basis, interface, risk/FMEA, applicability,
  physical-verification, manufacturing-readiness, and screenshot exception records.
- Per-part neutral/native exports and CAD-derived render catalogs (generated separately).
- Executive PPTX/PDF and internal review are complete.  The initial fresh-context review returned one
  critical, one major, and three minor package findings; the first closure review closed those and found
  two new major plus one minor reproducibility defect.  Subsequent clean extraction trials found and
  corrected STEP-schema scoping, Windows path, and required render-baseline defects.  Final short-root
  extraction, 680-file integrity, PAIR build, 12 renders, endpoint, five-angle, and 81-position full
  sweep all passed.  The second manifest-bound review independently closed all prior closure and
  extraction findings, then found one minor filename-reference typo in the unreleased drawing register.
  The register and delivered generator were corrected.  The final independent 684-file immutable
  set/size/hash recheck passed with zero mismatches and closed all package-review findings.

## Required path to release

Correct and qualify the inflation architecture; control exact supplier configurations and rated
interfaces; define mission/load/environment requirements; release drawings and work instructions;
complete all required calculations and physical tests; correct export reproducibility or approve a
controlled semantic acceptance method; rerun full validation/review; then evaluate production release.

This package authorizes no purchase, fabrication, field use, qualification acceptance, or merge to main.
