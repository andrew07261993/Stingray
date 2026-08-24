# Functional decomposition

This decomposition is architecture-first and does not preserve legacy part boundaries. “COTS” below means an independently orderable functional line; standard fasteners, raw stock, consumables, and inherited child geometry are excluded from the coverage denominator.

| Function | Required behavior | Best attainable class | Selected Architecture C allocation | Gate |
|---|---|---|---|---|
| Penetrator / entry structure | Engage mission fabric without loss of load path | UNAVOIDABLE CUSTOM | Custom source-derived penetrator | Fabric/load definition |
| Body structure | Carry launch, deployment and recovery loads in envelope | UNAVOIDABLE CUSTOM | Custom primary body/carrier | New structural design |
| Water sensing / authorization | Authorize only after immersion | COMPLETE COTS MODULE | Halkey-Roberts Alpha/V80040 module | False-fire and underwater test |
| Transport inhibit | Positive safe condition during handling | COTS + SMALL CUSTOM ADAPTER | GN 817 plunger plus custom inhibit interface | Abuse/two-action test |
| Trigger / release | Convert water event to pressure and latch release | CONFIGURABLE COTS MODULE | Alpha inflator plus pneumatic release cylinder | Force/time confirmation |
| Gas storage | Store adequate gas safely | COMPLETE COTS MODULE | 3 × Leland 89070 70 g cartridges | Depth/cold sizing |
| Pilot control | Isolate and signal release branch | COTS COMPONENT FAMILY | Swagelok check/tee elements | CO2 compatibility |
| Full-flow control | Open main inflation paths | COMPLETE COTS MODULE | Three independent Alpha piercer/inflators | 70 g compatibility/flow |
| Inflation | Convey gas to buoy without carrying recovery load | COTS COMPONENT FAMILY | Swagelok tube/fittings plus qualified hose | Timed cold test |
| Buoy extraction | Positively eject packed buoy | COTS + SMALL CUSTOM ADAPTER | Gutekunst VD-244 plus custom follower | Packed-buoy force test |
| Buoy storage | Protect and release packed buoy | UNAVOIDABLE CUSTOM | Custom pack enclosure/door | Pack/release development |
| Arm actuation | Coordinate three arms through required travel | CONFIGURABLE COTS MODULE | ACE GS-19 gas spring plus common crosshead | Exact force setting/test |
| Damping | Bound deployment rate | CONFIGURABLE COTS MODULE | ACE HBD-15-25-AA-P | Seawater/force-speed test |
| Backup deployment energy | Deploy after primary energy loss | COTS COMPONENT FAMILY | Lee Spring LHL 625D 12 candidate | Force/solid-height mismatch resolution |
| Arm guidance | Constrain intended DOF and remain captive | COTS + SMALL CUSTOM ADAPTER | COTS bushings/rings in custom carrier | Detailed joint design |
| Stops | Carry end-of-travel load | COTS + SMALL CUSTOM ADAPTER | Replaceable COTS stop pads on custom seats | 0.8 kN/arm proof floor |
| Locks | Positive deployment after drive-force loss | COTS + SMALL CUSTOM ADAPTER | GN 817 stainless plungers plus custom lock geometry | Shock/contamination test |
| Recovery tether / load transfer | Continuous structural chain independent of bladder/lines | COTS COMPONENT FAMILY | Samson AmSteel-Blue and catalog terminations | Wet splice/dynamic proof |
| Service closure | Seal, drain and permit access | COTS + SMALL CUSTOM ADAPTER | Parker seal plus GN 706.3 collar on custom door | IP/leak/corrosion test |
| Reset interfaces | Safe depressurization and controlled reverse reset | COTS + SMALL CUSTOM ADAPTER | COTS vent/indicator plus custom tool interfaces | Timed service demo |

## Selected functional-line denominator

Architecture C has 23 eligible independently orderable functional unique lines. Eighteen are complete/configurable COTS modules or component-family lines; five remain custom: penetrator, primary body/carrier, common crosshead/arm set, buoy pack enclosure, and interface adapter set. Standard fasteners and inherited actuator child geometry are excluded. Coverage is therefore `18 / 23 = 78.26%`.

This is the truthful current ceiling. Reclassifying the five custom lines, splitting catalog assemblies, or counting fasteners/raw stock would inflate the ratio without reducing architecture risk.
