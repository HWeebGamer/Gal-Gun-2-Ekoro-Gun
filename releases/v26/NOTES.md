# v26 — Story Choice Fix · Laser and No-Laser Editions

Story choices now show a VR cursor, and hovering a right-side choice updates the selected option instead of leaving the previous/left choice selected. **Both downloads contain this fix.**

Choose one edition:

- **GalGun2_VR_Ekoro_Gun_v26_Laser_Always_On.zip**: under-barrel laser attachment, automatic lighter pink beam at 50% particle opacity, and a bounded pink center marker.
- **GalGun2_VR_Ekoro_Gun_v26_No_Laser.zip**: the same gun, menus and story-choice fixes, without the beam, center marker or laser attachment.

Both include the extended-reach dynamic crosshair and brief pink heart muzzle effects. Neither requires a button binding or companion bridge.

## Install or update

Close the game and back up your previous mod files outside Paks. Extract the chosen ZIP's **EkoroPrototype_P.pak** and **EkoroPrototype_P.sig** into **GalGun2/Content/Paks/~mods**, replacing the old pair. Install **only one edition**; do not rename them to load both. Keep the original game archives untouched. Switching editions uses the same replacement process. If you tried the experimental bridge build, it is no longer needed; close the game before removing its EkoroLaserBridge folder.

## Verification

The author confirmed the story-choice fix in the laser edition on Quest 2 PC VR. Both release archives were extracted and checked against the exact patched story-choice actor and pawn; the no-laser edition has not had a separate v26 headset test. Automated checks cover 240 hover/selection cases and cursor visibility restoration. UnrealPak validated 25 laser-edition entries and 21 no-laser entries.

Windows Steam build 3345483 was used. Other game builds/headsets and combinations with other pawn/menu/weapon mods remain unverified. Two-handed grip is not included.
