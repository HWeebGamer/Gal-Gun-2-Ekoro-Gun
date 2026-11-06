# Gal*Gun 2 VR — Ekoro Gun

Ekoro's gun imported into Gal*Gun 2 VR, with a right-hand grip, a barrel-aligned gameplay crosshair, and gun-pointer menu navigation with trigger selection.

## Download and install

Download **one** edition from the [v33 release](https://github.com/HWeebGamer/Gal-Gun-2-Ekoro-Gun/releases/tag/v33):

| Edition | Laser | Circular white sight |
| --- | --- | --- |
| **Laser+Sight** | Yes | Yes |
| **NoAttachments** | No | No |
| **LaserNoSight** | Yes | No |
| **OnlySight** | No | Yes |

**All four include light anti-wobble stabilization**, the story-choice cursor/selection fix, dynamic crosshair, menu pointer, and brief heart muzzle effects. Each ZIP is a complete mod; attachments are not separate add-on PAKs. Use one mod ZIP, not GitHub's source-code ZIP.

1. Close the game.
2. Open the installation directory through Steam: Properties → Installed Files → Browse.
3. Open `GalGun2/Content/Paks` and create `~mods` if needed.
4. Extract both `EkoroPrototype_P.pak` and `EkoroPrototype_P.sig` directly into `~mods`.
5. Launch the game in VR normally.

Back up any previous mod pair outside `Paks` before replacing it. All four editions use the same installed filenames: install only one pair at a time. To switch editions, close the game and replace that pair. Remove older versions of this mod, including differently named copies. Leave the original game archives untouched. Other weapon, pawn, or menu mods may conflict.

To uninstall, close the game and remove only those two mod files from `~mods`.

## Status

The author confirmed the v33 Laser+Sight build on Meta Quest 2 PC VR. The other three editions have matching stabilization and story-choice code and passed archive checks, but have not had separate v33 headset tests. The tested game is the Windows Steam version, build 3345483. Other builds/headsets remain unverified. Two-handed grip is not implemented.

Stabilization gently smooths tiny rotational movements with an 18 ms time constant; larger turns bypass the filter. Position follows the controller directly. Menus, story cursor overrides, tracking loss and frame hitches reset the filter. This is motion smoothing, not target lock or aim assist toward enemies.

The circular white sight has a clear opening through which you use the existing world-space crosshair; it does not have a separately projected optic dot. Laser editions include an automatic pink beam, small center marker and under-barrel housing. No toggle or companion bridge is needed.

The crosshair's displayed reach is 50 metres, matching the existing targeting range. It gradually looks smaller at longer distances, shrinks another 20% over supported enemies, and smoothly recovers when aimed away. Story choices now show the VR cursor and update the confirmed choice when hovering different options, including right-side choices.

This release retains the tested menu diagnostic crosshair colors: green for an interactable widget, cyan for a hit-testable widget, orange for a component without a hit-testable path, red for no widget component hit, and magenta for an invalid interaction component.

## Development

Patch and packaging scripts are in `work/`. See [development instructions](docs/DEVELOPMENT.md) for required local inputs, build order, validation, and limitations. Game assets and engine tools are not included in the source tree. Installation of the release does not require development tools.

Unofficial fan mod; not affiliated with the game's developers or publisher. Game assets belong to their respective rights holders.
