# v17 test build: brief muzzle hearts

The user approved v16's size and appearance but requested near-immediate disappearance and less travel beyond the muzzle. Lifetime is reduced from 0.38 seconds to 0.08 seconds. The existing normalized alpha fade completes over that shorter lifetime. At unchanged velocity, travel before disappearance is approximately 21% of v16's travel (excluding the initial spawn offset).

Size, alpha strength, color, three-heart count, velocity/spread, muzzle placement, and all gun/crosshair/menu behavior remain unchanged. Only ParticleModuleLifetime_0's export payload changes: distribution minimum, maximum, and lookup value are all 0.08 seconds.

After building v16, run `python work/build_brief_hearts.py`, then use `work/package_muzzle_pointer.ps1 -BriefHearts` with the same CookedDirectory and UnrealPak parameters as earlier versions. The builder validates source lifetime values and reopens the output to verify scope. All 19 package entries pass archive validation.

Installed for headset testing with v16 backed up. Verify that hearts remain briefly visible at the barrel without drifting into the aiming area. No public release yet.
