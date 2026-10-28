# v14 test build: dynamic crosshair size

The user confirmed v13's 50-metre reticle reach works. They requested a smaller crosshair at longer distances and a slight shrink when aimed at enemies, returning when aimed away.

v14 preserves the v13 range and applies a multiplier to the existing pointer scale curve during motion-controller gameplay:

`clamp(1200 / (distance_cm + 1000), 0.35, 1)`

The original scale curve has matching time/value keys at 0, 500, and 100000 cm, compensating for distance. The new multiplier tapers its apparent size: 100% at 2 m or closer, 80% at 5 m, 60% at 10 m, 40% at 20 m, and a 35% floor farther away. World-space size still grows with distance; the crosshair looks smaller in the headset.

A fresh BreakHitResult from the pointer's final trace determines whether the actor is a GAL, MiniKuronaPawn, or MiniRisuPawn (including subclasses). Those enemy types receive an additional 0.8 multiplier. Walls, menu widgets, and no-hit results do not. This is aiming feedback, not a confirmation that a shot did damage. Other target classes may need adding after testing.

The result uses FInterpTo from the prior uniform AimReticle world scale at speed 12, using the pointer's tick DeltaSeconds. Size eases toward the new value and recovers when aiming away. Near/far transitions also ease. There is no cumulative multiplication of last frame's size.

The update applies only when the owning pawn uses dual motion controllers, enables camera/reticle control, and does not force-hide the aim reticle. Other contexts use the original curve directly. Menus, trigger input, ray direction, target range, and original trace code are retained.

## Build and validation

After building v13, run:

```powershell
python work/build_dynamic_reticle.py
python work/verify_dynamic_reticle.py
./work/package_muzzle_pointer.ps1 -DynamicReticle -CookedDirectory 'PATH/TO/COOKED/DevilSweeper' -UnrealPak 'PATH/TO/UnrealPak.exe'
```

Only ExecuteUbergraph_PointerComponent's function payload changes from v13. A trampoline preserves every original VM branch/event entry address; appended code returns to the original scale consumer. Existing package indices are preserved while names/imports are appended. Bytecode size, branch destinations, and context skip lengths are validated.

The emitted-bytecode evaluator passes 240 combinations of distance, target class, and gameplay/menu flags, plus easing/recovery at 45, 72, 90, and 120 Hz. UnrealPak validates all 17 entries. These checks do not prove Unreal runtime import resolution or visual behavior in the headset.

Installed for headset testing October 28, 2026; v13 was backed up before installation. The user subsequently confirmed v14 works and requested publication. The v14 release packages these exact tested binaries. Future regressions should be checked with distant and near enemies, transitions to walls/empty space, readability in both eyes, and title/pause menus.
