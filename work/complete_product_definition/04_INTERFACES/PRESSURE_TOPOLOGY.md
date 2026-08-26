# Pressure Topology

Status: **MAXIMUM-COMPLETE DIGITAL DEVELOPMENT PACKAGE - NOT RELEASED FOR FABRICATION, PROCUREMENT, QUALIFICATION, OR FIELD USE**

```text
Leland 81121 non-refillable 12 g CO2 cartridge
        |
        | 3/8-24 puncture interface; matching Hydro suffix not completed
        v
Halkey-Roberts Hydro 1F V95000 family automatic/manual inflator
        |-- V80040 water-sensitive bobbin / manual pull activation
        |-- V90113 manifold O-rings identified by supplier
        v
Custom 60 L buoy inflation patch/manifold
        v
Buoy internal volume / no separately modeled vent or exhaust
```

The current architecture has no separate fill interface, regulator, gauge, sensor, tee, hose, rigid
tube, or pneumatic actuator.  It therefore has zero CAD route objects.  This removes the historical
broken-line geometry family from the current model, but it does not prove the compact supplier-internal
flow path or the custom patch interface.

The topology is non-release because the cartridge/volume sizing fails, the exact Hydro suffix and
installed vendor geometry are absent, and the application pressure/flow/leak evidence is unavailable.
