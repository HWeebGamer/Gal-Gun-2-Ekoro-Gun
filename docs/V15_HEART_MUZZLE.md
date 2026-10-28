# v15 test build: pink heart muzzle burst

Adds a small pink heart burst at PointerComponent's barrel transform on accepted VR gameplay shots. The original controller input calls ShotEvent when the trigger crosses its press threshold; the gameplay input gate calls Shot. The added code guards dual controllers, camera/reticle enablement, force-hide state, nonzero reticle status, and pointer validity. Menu presses do not intentionally spawn effects.

The new `P_EkoroHearts` particle is a separate clone of the game's `P_EcstasyShot`, using only its CPU mesh-heart emitter and existing pink emissive material. The GPU sparkle emitter is not included in the active emitter list. Original impact effects remain unchanged.

The burst has three hearts with a 0.38-second lifetime and the original alpha fade. StartSize is 0.6; the component spawns at uniform scale 0.06. The existing sphere-location module supplies outward velocity from an 8-unit radius, with VelocityScale 200 and Negative_X disabled, so motion is in the muzzle's positive-X hemisphere. Original camera-offset and size-multiply-over-life modules are removed from the active heart emitter. Dynamic bounds replace the original fixed impact bounds.

SpawnEmitterAtLocation uses the muzzle's world position and rotation, uniform scale, and auto-destroy. The component is not attached after spawning, so the particle burst does not follow subsequent hand motion. Particle motion is local to that fixed component.

## Build

Supply the original `P_EcstasyShot.uasset/.uexp` under `UmodelSaved/Game/VRGG/Effect/Particles/Shooting/`. Build v14 prerequisites, then:

```powershell
python work/build_heart_muzzle.py
python work/verify_heart_muzzle.py
./work/package_muzzle_pointer.ps1 -HeartMuzzle -CookedDirectory 'PATH/TO/COOKED/DevilSweeper' -UnrealPak 'PATH/TO/UnrealPak.exe'
```

Only the Pawn Shot function payload changes from v14's pawn. A tail trampoline preserves the original shot branch addresses and resumes the original logic. Existing exports and imports retain their indices. All v14 pointer/menu/gun assets are reused unchanged. The new particle relies on mesh/material dependencies already present in the game.

Validation: bytecode branch/context lengths; 32 combinations of shot guards; muzzle location/rotation and auto-destroy arguments; unchanged non-Shot pawn exports; 19-entry PAK integrity check. These checks do not verify runtime particle rendering, exact visible size, or binocular alignment.

Installed for testing with a verified v14 backup. Check single presses, held/repeated presses, empty-space shots, muzzle origin/direction, visibility in both eyes, and no effects during title/pause menu selection. Effect size and spread may need tuning after the first headset test. No public release yet.
