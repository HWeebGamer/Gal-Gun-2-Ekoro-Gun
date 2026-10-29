# v16 test build: smaller, lower-alpha hearts

The user found v15's hearts distractingly large and requested smaller, partially transparent hearts. This adjustment reduces each linear size dimension to 25% of v15 (`StartSize` 0.6 → 0.15) and scales the existing `AlphaOverLife` curve from 1 → 0 down to 0.4 → 0. Timing is preserved. Actual perceived transparency still depends on the existing heart material and requires a headset test.

Three-heart burst count, 0.38-second lifetime, pink color, travel/spread, muzzle transform, input guards, and v14 dynamic crosshair remain unchanged. Reducing the mesh size rather than the entire component scale preserves particle motion.

Build after the v15 prerequisites:

```powershell
python work/build_subtle_hearts.py
./work/package_muzzle_pointer.ps1 -SubtleHearts -CookedDirectory 'PATH/TO/COOKED/DevilSweeper' -UnrealPak 'PATH/TO/UnrealPak.exe'
```

Validation reopens the generated particle package, verifies size (0.15 on all axes) and alpha endpoints (0.4, 0), and confirms that only ParticleModuleSize_0 and ParticleModuleColorOverLife_0 export payloads change. All 19 PAK entries pass integrity validation. v15 is backed up before local installation. Headset validation and public release are pending.
