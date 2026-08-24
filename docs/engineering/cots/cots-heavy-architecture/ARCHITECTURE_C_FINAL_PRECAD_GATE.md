# Architecture C final pre-CAD gate

## Decision

**C. ONE SPECIFIC MANUFACTURER INTERFACE VALUE REQUIRED BEFORE CAD**

The selected developmental path is two Leland `89200` cylinders, two Leland `65026-18Y12` mountable puncture heads, two independent commercial HP outlet/control paths, one `V80040` water-sensitive consumable with a dual non-pressure STINGRAY release, low-pressure convergence, Leafield GIV/B10 protection and the STINGRAY 60 L softgood. The custom `V80040` latch application is physical-qualification-required and is not represented as Nordson-approved.

## Closed gates

- gas inventory: 400 g versus 334.51 g qualification requirement — **PASS**;
- source body diameter: 50.038 mm versus 50.80 mm allocation — **PASS, TOLERANCE-CRITICAL**;
- source count: two — **PASS**;
- source gross mass: 0.600 kg total published — **PASS**;
- complete system mass estimate: 3.400 kg; projected ready-to-throw 14.911 kg; reserve 3.229 kg — **PASS BY PRE-CAD ESTIMATE**;
- pressure boundary: commercial Leland head through 1/8 NPT; no raw-HP manifold — **CREDIBLE TOPOLOGY**;
- water authorization: separated from HP boundary, passive and non-electrical — **CREDIBLE TOPOLOGY**;
- field reset: certified charged module exchange — **PASS IN CONCEPT**;
- custom pressure vessels: 0;
- custom HP adapters: 0.

## Single developmental-CAD hold

Obtain the **Leland drawing-controlled `89200` + `65026-18Y12` armed interface definition**, stating installed safe/armed and fired overall lengths, thread engagement, axial/rotary advance, puncture torque/force, retention/reaction, bracket/outlet keep-out and removal direction.

This one document controls both mechanical release sizing and the longitudinal packaging gate. Published cylinder-plus-head arithmetic is 560.07 mm against the existing 545 mm forward pressure corridor, but it double-counts unknown neck/head overlap and omits unknown armed travel. Fit cannot truthfully be claimed without the interface document.

`CAD_AUTHORIZED = false`

`FALLBACK_SEARCH_TRIGGERED = false`

`REASON = COMMERCIAL RATED PUNCTURE INTERFACE EXISTS; ONLY ITS ARMED INSTALLATION DEFINITION IS MISSING`

## Downstream gates that do not hold developmental CAD

- procurement: orderable suffixes, quote, lead time, CoC/lot options and exact hose/control MPNs;
- pressure test: exact `89200` allowable/proof/burst/temperature data, `65026` derating/application limit and complete component ratings;
- release: received identity/CoC, 0 C/5 m/10 s performance, relief accumulation, softgood pressure/leak/cycle, salt/corrosion/reset and structural qualification.

Delivered-item CoCs accepted: **0**.

## Exact next action

Obtain the one Leland armed-interface drawing above; then commission only the bounded developmental CAD packaging of two axial modules. Do not start CAD before that document.
