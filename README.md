# Gal*Gun 2 VR — Ekoro Gun

Ekoro's gun imported into Gal*Gun 2 VR, with a right-hand grip, a barrel-aligned gameplay crosshair, and gun-pointer menu navigation with trigger selection.

## Download and install

Download **one** edition from the [v26 release](https://github.com/HWeebGamer/Gal-Gun-2-Ekoro-Gun/releases/tag/v26):

- **GalGun2_VR_Ekoro_Gun_v26_Laser_Always_On.zip** — under-barrel attachment, lighter pink beam at 50% particle opacity, and a small pink aiming dot. Automatically active during gameplay; no toggle or companion program.
- **GalGun2_VR_Ekoro_Gun_v26_No_Laser.zip** — no laser beam, laser dot, or under-barrel attachment.

**Both editions include the story-choice cursor and correct hovered-choice selection fix**, along with the Ekoro gun, dynamic crosshair, menu pointer, and brief heart muzzle effects. Use one of these mod ZIPs, not GitHub's automatically generated source-code ZIP.

1. Close the game.
2. Open the installation directory through Steam: Properties → Installed Files → Browse.
3. Open `GalGun2/Content/Paks` and create `~mods` if needed.
4. Extract both `EkoroPrototype_P.pak` and `EkoroPrototype_P.sig` directly into `~mods`.
5. Launch the game in VR normally.

Back up any previous mod pair outside `Paks` before replacing it. Both editions use the same installed filenames: install only one pair at a time. To switch editions, close the game and replace that pair. Remove older versions of this mod, including differently named copies. Leave the original game archives untouched. Other weapon, pawn, or menu mods may conflict.

To uninstall, close the game and remove only those two mod files from `~mods`.

## Status

The author confirmed the v26 story-choice fix on their Meta Quest 2 PC VR setup, using the laser edition. Both packaged editions were verified to contain the exact same patched story-choice actor and pawn. The no-laser edition has not had a separate v26 headset test. The tested game is the Windows Steam version, build 3345483. Other builds and headsets have not been verified. Two-handed grip is not implemented.

The crosshair's displayed reach is 50 metres, matching the existing targeting range. It gradually looks smaller at longer distances, shrinks another 20% over supported enemies, and smoothly recovers when aimed away. Story choices now show the VR cursor and update the confirmed choice when hovering different options, including right-side choices.

This release retains the tested menu diagnostic crosshair colors: green for an interactable widget, cyan for a hit-testable widget, orange for a component without a hit-testable path, red for no widget component hit, and magenta for an invalid interaction component.

## Development

Patch and packaging scripts are in `work/`. See [development instructions](docs/DEVELOPMENT.md) for required local inputs, build order, validation, and limitations. Game assets and engine tools are not included in the source tree. Installation of the release does not require development tools.

Unofficial fan mod; not affiliated with the game's developers or publisher. Game assets belong to their respective rights holders.
