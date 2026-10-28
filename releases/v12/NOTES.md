# v12 — working VR gun and menu pointer

- Ekoro gun model replaces the right-hand weapon.
- Gameplay crosshair follows the barrel.
- Menu pointer follows the barrel and supports hover/navigation and trigger selection.
- Fixes the menu's fixed-world-direction interaction ray overriding gun aim.
- Retains diagnostic menu crosshair colors from the tested build.

Confirmed working by the user on Meta Quest 2 PC VR, October 28, 2026. Tested game: Windows Steam build 3345483. Two-handed grip is not included.

Download `GalGun2_VR_Ekoro_Gun_v12.zip`, close the game, and extract both the `.pak` and `.sig` directly into `GalGun2/Content/Paks/~mods`. Create `~mods` if needed. Back up any older mod pair outside Paks first. Do not replace the original game archives.

The ZIP includes installation/removal instructions and SHA-256 checksums. Its binaries match the user-tested v12 installation. `manifest.json` records both binary hashes and sizes.
