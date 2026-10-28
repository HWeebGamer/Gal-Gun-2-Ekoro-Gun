# Gal*Gun 2 VR — Ekoro Gun

Ekoro's gun imported into Gal*Gun 2 VR, with a right-hand grip, a barrel-aligned gameplay crosshair, and gun-pointer menu navigation with trigger selection.

## Download and install

Download **GalGun2_VR_Ekoro_Gun_v14.zip** from the [v14 release](https://github.com/HWeebGamer/Gal-Gun-2-Ekoro-Gun/releases/tag/v14). Use the mod ZIP, not GitHub's automatically generated source-code ZIP.

1. Close the game.
2. Open the installation directory through Steam: Properties → Installed Files → Browse.
3. Open `GalGun2/Content/Paks` and create `~mods` if needed.
4. Extract both `EkoroPrototype_P.pak` and `EkoroPrototype_P.sig` directly into `~mods`.
5. Launch the game in VR normally.

Back up any previous mod pair outside `Paks` before replacing it. Remove older versions of this mod, including differently named copies. Leave the original game archives untouched. Other weapon, pawn, or menu mods may conflict.

To uninstall, close the game and remove only those two mod files from `~mods`.

## Status

The author confirmed v14 works on their Meta Quest 2 PC VR setup. The tested game is the Windows Steam version, build 3345483. Other builds and headsets have not been verified. Two-handed grip is not implemented.

V14 extends the crosshair's displayed reach from 5 to 50 metres, matching the existing targeting range. It gradually looks smaller at longer distances, shrinks another 20% over supported enemies, and smoothly recovers when aimed away. Menu sizing and controls are preserved.

This release retains the tested menu diagnostic crosshair colors: green for an interactable widget, cyan for a hit-testable widget, orange for a component without a hit-testable path, red for no widget component hit, and magenta for an invalid interaction component.

## Development

Patch and packaging scripts are in `work/`. See [development instructions](docs/DEVELOPMENT.md) for required local inputs, build order, validation, and limitations. Game assets and engine tools are not included in the source tree. Installation of the release does not require development tools.

Unofficial fan mod; not affiliated with the game's developers or publisher. Game assets belong to their respective rights holders.
