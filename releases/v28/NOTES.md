# v28 — Light Stabilization and Four Attachment Editions

Small hand tremors are gently smoothed while larger turns respond immediately. All four editions include the same anti-wobble adjustment, story-choice cursor/selection fixes, dynamic crosshair, menu pointer and brief heart effects.

Choose one complete mod:

| Download | Attachments |
| --- | --- |
| GalGun2_VR_Ekoro_Gun_v28_Laser+Sight.zip | Pink laser and white sight |
| GalGun2_VR_Ekoro_Gun_v28_NoAttachments.zip | Neither attachment |
| GalGun2_VR_Ekoro_Gun_v28_LaserNoSight.zip | Pink laser only |
| GalGun2_VR_Ekoro_Gun_v28_OnlySight.zip | White sight only |

The sight uses the existing crosshair through its clear opening; there is no separate projected optic dot. Laser editions include the under-barrel housing, automatic beam and pink center marker. No button setup or companion program is required.

## Install or update

Close the game. Back up the previous mod pair outside Paks. Extract **EkoroPrototype_P.pak** and **EkoroPrototype_P.sig** from your chosen ZIP directly into **GalGun2/Content/Paks/~mods**, replacing the old pair. Install only one edition. Do not rename the files to load multiple editions together. Switching editions uses the same replacement process. Leave original game archives untouched.

## Verification and limits

The author confirmed the Laser+Sight v28 build feels good on Quest 2 PC VR. Its release PAK is byte-for-byte identical to that tested build. The other editions use the same stabilization pawn and story-choice fixes but have not had separate headset tests. All four PAKs passed UnrealPak validation and extraction/hash comparisons; ZIP contents and checksums are verified before publication.

The filter uses an 18 ms rotational time constant, bypasses changes exceeding 0.7 degrees on any normalized rotation axis, and leaves position directly tracked. Menu/story override, tracking loss and frame hitches reset its history. Simulated emitted-bytecode checks cover tremor attenuation, fast turns, yaw wraparound and recovery. VR controller late update remains enabled.

Windows Steam build 3345483 was used. Other builds/headsets and combinations with other pawn/menu/weapon mods remain unverified. No hand model or two-handed grip is included.
