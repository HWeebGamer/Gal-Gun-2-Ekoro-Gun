# v13 test build: reticle distance

The user reported that the mission crosshair followed their aim but stopped at a fixed distance while shots could still hit farther targets.

Inspection found PointerComponent's VR `MaxDistance` default is 500 cm, while `MaxTraceDistance` is 5000 cm. Its tick clamps the displayed hit distance to MaxDistance before positioning the reticle. The motion-controller path already bypasses the pawn's angular cursor clamp.

This change raises only `Default__PointerComponent_C.MaxDistance` from 500 to 5000 cm (5 to 50 metres), matching the existing gameplay trace. The targeting distance, collisions, hit displacement, distance-dependent scaling curve, menu interaction ray, trigger handling, and all v12 assets remain unchanged. With no hit, the reticle can now sit at the farther limit. The non-VR BeginPlay override is unchanged.

## Build

First build v12 as described in DEVELOPMENT.md. Supply the original `VRGG/Actors/PointerComponent.uasset` and `.uexp` under `UmodelSaved/Game/`, then run:

```powershell
python work/build_reticle_distance.py
./work/package_muzzle_pointer.ps1 -ReticleDistance -CookedDirectory 'PATH/TO/COOKED/DevilSweeper' -UnrealPak 'PATH/TO/UnrealPak.exe'
```

The patcher checks the original display/trace defaults and modifies exactly one four-byte property value. The original package header and every other payload byte are preserved. UnrealPak validated all 17 package entries.

Installed for local testing October 28, 2026. PAK SHA256: `726D090D26B81721F4547FB73478A717BD1FA160E6AE23A9D4494CA8765DEF63`.

The user confirmed the longer reach works well on October 28, 2026. They then requested distance-dependent shrinking and enemy-target size feedback, implemented in the v14 test build. v13 is not a published release; v12 remains the downloadable version.
