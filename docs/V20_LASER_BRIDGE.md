# v20 test: physical right A through a SteamVR companion

The v19 toggle did not receive physical A through the user's SteamVR/ALVR runtime. Read-only mission inspection confirmed the laser fields loaded, all gameplay gates enabled, and no enabled state or spawned beam after A presses. See LASER_INPUT_DIAGNOSIS.md for the runtime mapping evidence.

The companion bridge reads OpenVR's right-hand A bit directly. Its read-only probe detected the user's presses and releases. It sends one 100 ms F8 pulse per rising edge only while the exact installed game process owns the foreground window. It suppresses holds, focus-regain activation, and reconnect-held activation, releases its injected key on focus loss or shutdown, prevents duplicate instances, and exits when that game process ends. It does not modify process memory, global bindings, or startup settings. The helper loads the game's own OpenVR DLL by absolute path.

The pak now polls F8 during gameplay. The mapping library reserves F8 instead of MotionController_Right_FaceButton1, restoring the latter's original SteamVR touchpad-direction behavior. All existing gun, crosshair, menu and heart assets remain. The laser renderer is unchanged; rendering cannot be judged until input actually activates it.

## Build

- Build bridge/EkoroLaserBridge.cpp with MSVC x64 and the installed UE4.18 OpenVRv1_0_10 headers; use /std:c++17 /EHsc /MT and user32.lib. Run the resulting executable with --self-test.
- Run work/build_laser_control.py and work/verify_laser_control.py with --bridge.
- Run work/build_right_a_reservation.py and work/verify_right_a_reservation.py with --bridge.
- Package with work/package_muzzle_pointer.ps1 -LaserBridge, passing the v18 cooked mesh snapshot and UnrealPak path.

Verification passed: helper edge/focus self-test, 64 generated laser-control cases, 22 generated mapping paths, unchanged other input-library exports/imports, and UnrealPak's 23-entry integrity check. Physical A was detected in a read-only probe against the actual running game session. Full keyboard-to-game and beam rendering verification remains a headset check.

Installed as muzzle-pointer-v20-laser-bridge-test, pak SHA256 7A6B66A209633178AE8F679770716CB643AB747946B9BBF995D9D29399B5F0CA. Prior pak/sig and manifest backed up under G:\GalGun2-ModWork\backups\prototype-v19. Original game archives unchanged. Companion installed in the game root's EkoroLaserBridge folder; see its README for startup and rollback. Not published.
