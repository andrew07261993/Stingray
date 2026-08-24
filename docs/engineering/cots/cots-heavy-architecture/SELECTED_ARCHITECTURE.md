# Selected architecture — Architecture C retained with pressure revision required

## Selection status

The historical trade winner remains **Architecture C: distributed cartridge mechanical bus**, with the recorded 405/500 score and projected 18/23 = 78.26% functional COTS. That trade result is preserved. The specific **three-cartridge pressure embodiment is not accepted for general CAD implementation**.

Formal disposition: **ARCHITECTURE C PRESSURE CONCEPT REQUIRES REVISION**.

## What remains selected

- Distributed, independently checked, field-replaceable sealed gas-source modules.
- Zero custom pressure vessels.
- Passive water authorization, no electrical dependency and no pyrotechnic initiation.
- COTS pressure components with explicit catalog ratings and receiving traceability.
- Modular field reset without routine depot rebuilding after damage-free deployment.
- Separate structural recovery chain and positive mechanical arm stops/locks.

## Required revised pressure topology

`supported approved cartridge/inflator branches → HP checks → HP bus → pressure regulator → fixed flow restrictor → buoy-adjacent high-flow differential relief → buoy`

The HP design basis is provisionally 2,500 psig with ≥3,000 psig component ratings at temperature. The exact value is replaced by higher manufacturer application data if supplied.

## Gas inventory disposition

For 60 L at depth with a provisional 10 kPa buoy differential:

- 210 g supports about 5.18 m warm design, 2.82 m nominal design and 0.07 m cold design.
- Qualification limits are about 3.72 m warm, 1.56 m nominal and unsupported at 0 °C surface.
- Three cartridges therefore fail as a general solution.
- Reserve packaging/interfaces for **at least four 70 g-class sources** in the next trade/layout iteration, but do not call four sufficient until mission values close. Ten-metre qualification needs about 300/352/440 g at warm/nominal/cold conditions.

## Field reset

The service architecture is conditionally feasible: complete cartridge/puncture modules, water consumables, checks, regulator/restrictor/relief modules, damper and buoy are line-replaceable or inspectable. Normal deployment should not require depot work. This verdict is held until the exact inflator service kit, torque/engagement controls, leak criterion, fold card and two representative reset cycles are approved.

## Development procurement

- HIKO `87640_OLV_ONE`: quantity 2, softgoods development only.
- ACE `HBD-15-25-AA-P`: quantity 2, underwater mechanism development.
- Complete 70 g water branch: **blocked, quantity 0**, until manufacturer application approval and buoy pressure/relief closure.

## Fail-closed gates before CAD commission

1. Owner mission and buoy pressure values close.
2. Exact 89070 water inflator/puncture configuration is manufacturer-supported or published-data technically supported.
3. Revised cartridge count and layout meet mass/envelope requirements.
4. Regulator, restrictor and relief pass cold transient/fault-flow sizing.
5. Development procurement and test results are reviewed; field reset is demonstrated.
6. Owner separately authorizes Architecture C CAD implementation.

Until then: **NOT RELEASED — DO NOT PROCURE FOR PRODUCTION — DO NOT IMPLEMENT CAD**.
