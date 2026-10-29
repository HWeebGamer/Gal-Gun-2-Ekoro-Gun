# Right-A bridge for SteamVR / Quest

This companion is needed for the v20 test pak. UE4.18's legacy SteamVR input does not forward Quest A as MotionController_Right_FaceButton1. The bridge reads the right controller's OpenVR A bit and sends one 100 ms F8 pulse per press. The mod reserves F8 for the laser; pressing keyboard F8 also toggles it during gameplay.

Place this folder, named `EkoroLaserBridge`, directly inside the GalGun 2 installation folder. It must contain EkoroLaserBridge.exe and both Start Laser Bridge launchers. The pak and its companion sig still go in GalGun2/Content/Paks/~mods as usual.

1. Start the game through SteamVR.
2. Run `EkoroLaserBridge/Start Laser Bridge.cmd` once per game session.
3. Enter a mission and press right A to toggle the beam. Keep the desktop game window focused; click its window if needed.

The launcher attempts to focus the game. The bridge never forwards keys while another desktop app is focused. It requires A to be released after launch/reconnection, avoids repeating while held, prevents duplicate instances, and exits when the game closes. No administrator privileges, injection, game-memory writes, SteamVR binding changes, or Windows startup entries are needed. Logs are in this folder. Closing the game stops it; deleting this folder uninstalls the companion. Restore the prior pak/sig pair to roll back the mod.

The bridge dynamically loads the game's existing Engine/Binaries/ThirdParty/OpenVR/OpenVRv1_0_10/Win64/openvr_api.dll. No extra runtime DLL is distributed. Build the C++ source with MSVC x64, /std:c++17 /EHsc /MT, UE4.18's OpenVRv1_0_10 headers, and user32.lib. `--self-test` checks input edge/focus behavior. `GAME_ROOT --probe` reads A for 45 seconds without sending keyboard input.

Physical A detection was verified against the user's running SteamVR/ALVR session. Beam rendering and the complete input-to-pak path still require the v20 headset test.
