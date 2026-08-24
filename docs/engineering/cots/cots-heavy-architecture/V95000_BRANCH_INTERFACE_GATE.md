# V95000 final-branch interface gate

## Finding

The cartridge/inflator pair remains a published commercial rearm configuration, but the **STINGRAY HP branch does not**.

Nordson publishes Hydro 1F as a life-vest inflator. Its service sheet identifies two manifold O-rings and a cartridge gasket. The official `830011001` manifold instructions install a 1F inflator onto a manifold with a valve core, O-rings on both sides and a cap torqued 24–30 in-lb. No captured drawing publishes a pressure-rated threaded/tube outlet from `V95000` suitable for an HP check valve or collection bus.

Therefore:

- `V95000 + 86202Z` rearm pairing: **PUBLISHED CONFIGURATION SUPPORTED** in its published life-vest/manifold context;
- `V95000 + 86202Z + HP check + HP bus`: **APPLICATION APPROVAL REQUIRED / NO PUBLISHED INTERFACE**;
- the earlier topology cannot be frozen for CAD.

## Seal and leak-interface count

For nine published source modules, the documented service-seal minimum is 27: nine cartridge gaskets plus eighteen manifold O-rings. A hypothetical two-connection check per branch raises the source/check connection lower bound to 45 before common-bus, regulator, restriction, relief and buoy interfaces. Because the manifold-to-HP adapter is undefined, the final leak-point count is not releasable.

## Required resolution

Nordson/Leland must either:

1. provide a commercial, pressure-rated manifold/outlet/holder configuration approved for `V95000 + 86202Z` feeding an HP check/bus, with MAWP, temperature derating, flow/reaction limits and service instructions; or
2. approve direct installation on a selected buoy/manifold system with documented low-pressure relief and fault-flow capacity; or
3. nominate a different commercial water-automatic pressure-source device with a rated outlet.

No custom pressure plenum, receiver or improvised adapter is authorized.
