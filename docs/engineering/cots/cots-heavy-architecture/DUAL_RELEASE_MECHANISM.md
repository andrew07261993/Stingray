# Passive dual-release mechanism

## Selection

**ONE WATER AUTHORIZATION -> ONE SPRING-LOADED EQUALIZER -> TWO POSITIVE MECHANICAL RELEASE OUTPUTS**

One Nordson MEDICAL / Halkey-Roberts `V80040` field-replaceable water-sensitive bobbin releases the retained STINGRAY non-pressure latch. A captured spring drives a balanced crossbar/equalizer. Two short, independently preloaded Bowden outputs or a direct dual yoke advance the two `89200` cylinders into fixed `65026-18Y12` heads. The high-pressure boundary remains entirely inside the two commercial heads and their rated outlets.

Nordson publishes that `V80040` disintegrates under immersion, is replaceable and has a marked expiration date, but also states that it is intended for Halkey-Roberts products only. Therefore `V80040` identity and behavior are commercial evidence; its use in the retained STINGRAY latch is **APPLICATION QUALIFICATION REQUIRED**, not manufacturer-approved. This is a non-pressure physical qualification/release gate. The next CAD commission may preserve the already bounded trigger envelope, but may not claim Nordson application approval.

The exact choice between Bowden outputs and a direct yoke is a bounded-CAD packaging decision after the Leland interface document supplies required travel and torque. This does not reopen the pressure architecture.

## Why one trigger is selected

| Criterion | One trigger / dual output | Two independent water triggers |
|---|---|---|
| Water authorization | One event | Two activation events may differ |
| Required source firing | Mechanically forces two outputs | One source can be omitted or delayed |
| Timing | Common equalizer; difference bounded by linkage | Bobbin wetting variability is additive |
| Reset consumables | One | Two |
| Ready-state inspection | One armed indicator plus two output witnesses | Two separate armed states |
| Common-cause failure | Trigger is single-point | Lower trigger commonality, but mission still fails if either source misses |

Because one 200 g source cannot meet 334.51 g, independent triggers do not provide useful mission redundancy: failure of either is a mission failure. The equalizer instead makes single-cylinder omission directly inspectable. It shall include two over-center/full-stroke witnesses or one crossbar position that cannot indicate fired unless both outputs reach the drawing-controlled stroke.

## Controls

- Passive, no electrical dependency and non-pyrotechnic.
- Water remains the only deployment authorization after the transport-safe pin is removed.
- Stored spring energy acts only on the non-pressure drive; it does not form a pressure boundary.
- Both modules are restrained against puncture reaction and hose thrust.
- The mechanism is fail-safe against partial armed thread engagement and cannot allow a charged cylinder to unscrew under discharge reaction.
- Simultaneous release is targeted; allowable timing difference is **PROVISIONAL — PHYSICAL TEST REQUIRED** until 10 s useful-inflation testing allocates a numerical limit.
- The linkage is not pressure-tested; the two commercial gas paths are tested under qualified pressure-system procedures.

## Field reset

1. Make safe, isolate the article and verify both branches have no residual pressure using the approved service indication/procedure.
2. Remove both discharged `89200` modules; no field cylinder refill is allowed.
3. Inspect both `65026` pins, seals, relief holes, brackets and rated outlet connections; reject damage, corrosion, obstruction or seal uncertainty.
4. Install two certified charged `89200` replacements and verify minimum gross weight/identity/lot status.
5. Replace the water-sensitive consumable; reset the latch, spring and equalizer with the transport-safe pin installed.
6. Verify both output witnesses and the drawing-controlled safe thread engagement without approaching puncture travel.
7. Inspect/reconnect low-pressure lines; deflate, dry, inspect and repack the buoy.
8. Perform the approved leak/functional checks and complete the ready-state checklist.

Verdict: **FIELD RESETTABLE BY CERTIFIED CHARGED MODULE EXCHANGE — NO FIELD CYLINDER RECHARGE, NO PRESSURE-VESSEL FABRICATION.**

Source: [Nordson MEDICAL V80040 instructions](https://fluid-components.nordsonmedical.com/files/fluid-components-nordsonmedical-com/Technical%20Information/HRC/Hyrdo-1F-Manual-Automatic-Inflator-V80040-Bobbin-Instructions-For-Use.pdf).
