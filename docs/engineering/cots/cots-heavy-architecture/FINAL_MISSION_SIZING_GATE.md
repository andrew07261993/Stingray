# Final owner-mission CO2 sizing gate

## Controlled owner basis

- Maximum activation depth: **5.0 m**.
- Minimum water/cartridge/source temperature: **0 °C**.
- Inflation time: **10 s maximum** to useful inflation.
- Required usable volume: **60 L actual displaced volume at operating depth**; nominal label/geometric capacity is not a substitute.
- Environment: fresh and salt water, repeated immersion/reset/repack, 0 °C minimum and marine corrosion exposure.

## Useful-inflation test threshold

The measurable 10 s threshold is **at least 54 L actual displaced volume at 5 m (90% of the 60 L requirement), with the buoy deployed into its stable intended geometry and volume still increasing or holding without structural leakage**. Measure displacement directly or infer it from calibrated in-water buoyant force corrected for water density. A rated/geometric volume, surface volume or visual “full” indication is not acceptable.

The gas inventory is still sized to **60 L actual volume**, not 54 L. Full 60 L steady-state usable displacement before source exhaustion is a separate pass criterion.

## Controlling calculation

The existing Peng–Robinson 60 L model at 5 m and 0 °C gives:

- theoretical minimum: **190.06 g**;
- design requirement: **304.10 g**;
- qualification requirement: **334.51 g**.

The design and qualification multipliers retain the existing cold-discharge, residual gas, flow/loss, leakage and reserve treatment; this commission did not redefine them.

## Integer result

| Branches | Inventory | Design margin | Qualification margin | Result |
|---:|---:|---:|---:|---|
| 5 | 190 g | −114.10 g | −144.51 g | FAIL / FAIL |
| 6 | 228 g | −76.10 g | −106.51 g | FAIL / FAIL |
| 7 | 266 g | −38.10 g | −68.51 g | FAIL / FAIL |
| 8 | 304 g | −0.10 g | −30.51 g | FAIL / FAIL |
| **9** | **342 g** | **+37.90 g (+12.46%)** | **+7.49 g (+2.24%)** | **PASS / PASS** |

**Thermodynamic minimum count: nine `86202Z` cartridges.** Eight fails even the design case. Nine has no complete-branch-out tolerance: eight remaining cartridges fail qualification and miss design by 0.10 g. No one-branch-out requirement was supplied, so a tenth branch is not selected merely for redundancy.

## 5 / 6 / 7 branch comparison

Repeated branch occurrences do not change the historical 18/23 = 78.26% projected unique functional-line COTS percentage if every interface remains COTS. Mass, package volume, leak interfaces, reset actions and qualification burden rise approximately linearly with branch count, while the probability that every branch activates/discharges falls as more branches are required. All of 5/6/7 fail the controlling cold/depth case, so none is selectable regardless of its lower burden.

`FINAL_MISSION_SIZING_GATE.csv` includes the numerical margins, cartridge-envelope proxy, procurement/shipping mass proxy, seal lower bounds and reset consumables.

## Mass and packaging evidence limit

- Cylinder outer-envelope proxy: about 83.3 mL each; nine = **749.7 mL**, before clearance, holders, manifolds or routing.
- A current market record lists the complete `V95000-86202Z` rearm kit at approximately 0.204 kg; the official Hydro 1F shipping pack averages 0.0726 kg per inflator. These give a conservative procurement/shipping proxy of **2.489 kg for nine rearm kits plus nine inflators**.
- That proxy is not installed mass. Exact cartridge gross mass, holder/manifold mass, checks, tubing, bus, regulator, restriction and relief are absent. A total installed package mass cannot be released until exact commercial interfaces exist.

## Flow-time gate

Static inventory does not establish the 10 s requirement. Nine-branch activation synchronization, cold puncture, delivered mass and buoy displacement must be demonstrated at 5 m/0 °C or in an approved equivalent facility procedure. The LSC Type-3 article proves trigger behavior only and does not qualify nine 38 g branches.

## Sizing disposition versus architecture disposition

The **342 g inventory is frozen as the minimum thermodynamic inventory** for the owner case. It does not authorize nine Hydro 1F devices into the previously drawn HP bus; that interface is not published and the pressure architecture requires revision.
