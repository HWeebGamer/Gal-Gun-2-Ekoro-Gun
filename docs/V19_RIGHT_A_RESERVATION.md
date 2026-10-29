# v19: reserve right A for the laser

The user reported a face button opening a game menu and requested that physical right A be reserved for the laser. DefaultInput.ini alone did not reveal the game's bindings: PlayerInputFunctionLibrary builds action/axis mappings from options and global data, and PlayerController.InitInput2 clears and installs those mappings.

CreateActionKeyMapping and CreateAxisKeyMapping now skip Array_Add when the final l_Key equals MotionController_Right_FaceButton1. The check occurs after optional hand inversion, so it reserves physical right A. Other keys retain their original mapping construction. The existing v18 raw WasInputKeyJustPressed query still toggles the laser during gameplay; menu presses do not toggle it. Right B, left face buttons, triggers, keyboard, and gamepad face-button mappings are not filtered.

The patch adds a tail branch to each function while preserving existing VM addresses. It reuses the existing FKey and EqualEqual_KeyKey imports; UE4.18 local engine source confirms the equality function is static native and supports EX_CallMath. All other exports remain byte-identical. This does not change SteamVR external bindings or prove which face button originally opened the user's menu.

## Build and verification

Run `python work/build_right_a_reservation.py`, then `python work/verify_right_a_reservation.py`. The builder expects the original extracted library in the parent workspace's UmodelSaved/Game/VRGG/Player/Utils directory. Package using `work/package_muzzle_pointer.ps1 -RightALaser`, with the v18 attachment mesh snapshot as CookedDirectory and UE4.18 UnrealPak as UnrealPak.

The saved-bytecode evaluator checks 20 paths across action and axis mappings, including right A suppression and preservation of B, left buttons, triggers, gamepad A, Enter, Escape, and None. It verifies unchanged imports and all other exports. UnrealPak validates all 23 entries. These are offline checks, not a headset test.

Installed locally with a checksum-verified v18 backup at G:\GalGun2-ModWork\backups\prototype-v18. Original game archives remain unchanged. Not published.

Headset check: launch fresh, enter a mission, press right A twice to confirm laser on/off without opening a menu. Verify other menu controls and trigger selection still work. If the conflict persists, inspect the active controller runtime's key aliases rather than broadening the filter indiscriminately.
