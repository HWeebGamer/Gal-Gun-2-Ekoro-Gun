# Development baseline: v12

The release ZIP is the exact user-tested build. Source scripts preserve the cooked Blueprint patch workflow for subsequent commits. This is not a standalone Unreal project or a complete clean-room rebuild of the game assets.

## Local inputs

- Python 3.10 or compatible Python 3; Blueprint patchers use the standard library.
- Unreal Engine 4.18.3 UnrealPak for packaging. The game uses a customized UE4.18.1 build.
- Original extracted `.uasset` and `.uexp` pairs under `UmodelSaved/Game/` for:
  - `VRGG/Player/VRGG_Pawn`
  - `VRGG/Widgets/VRGG_Widget`
  - `VRGG/Widgets/WidgetControl/VRGG_SelectControl_Widget`
  - `VRGG/Widgets/Base/Title/VRGG_TitleMenu_Widget`
- Seven previously cooked mesh/material files for `SK_DevilSweeper_Grip`, `Ekoro_BaseColor`, and `Ekoro_Prototype_Surface`, supplied to the packager through `-CookedDirectory`.

Extract original packages from your own installation, without installed mod overrides. Preserve them unchanged. The original archives, extraction keys, engine binaries, local memory snapshots, and backup folders are not tracked here.

The optional Blender script `build_ekoro_prototype.py` records mesh conversion from local Double Peace Ekoro GLTF and Gal*Gun 2 skeleton references. Its staging path is currently machine-specific and must be adjusted before use. It does not create/cook the UE material project. The working cook used instanced stereo, multiview, and forward shading enabled; retain the existing cooked assets when changing only menu behavior.

## Blueprint build order

Run from the repository root after supplying the local inputs:

```powershell
New-Item -ItemType Directory -Force outputs
python work/build_muzzle_pointer.py --native-menu-confirm
python work/build_scoped_menu_hover.py
python work/build_pointer_diagnostic.py
python work/verify_pointer_diagnostic.py
python work/build_menu_ray_alignment.py
./work/package_muzzle_pointer.ps1 -MenuRayAlignment -CookedDirectory 'PATH/TO/COOKED/DevilSweeper' -UnrealPak 'PATH/TO/UnrealPak.exe'
```

The stages intentionally retain their historical v8/v10/v11/v12 names. v12 packages the v11 pawn, v10 scoped hover handlers, v12 base-widget update, and the unchanged cooked gun assets. Do not combine historical packaging switches with `-MenuRayAlignment`.

The packager creates, tests, and lists the PAK. It does not install it. Close the game, back up the installed mod pair outside Paks, then install the new files manually. The existing `.sig` companion is a legacy loader workaround; it is not a newly generated cryptographic signature for the mod.

For reproducing the *existing* v12 ZIP, place matching `EkoroMuzzlePointer_v12_P.pak` and `.sig` in `outputs/`, then run `python work/package_shareable_v12.py`. The release manifest validates exact hashes. That script deliberately refuses to overwrite an existing ZIP. Future versions need their own manifest/version and release notes.

## Why v12 fixes menu aiming

Read-only runtime inspection found WidgetInteraction active with hit testing enabled, but reporting no hovered widget. Its direction differed from the barrel pointer. The original `VRGG_Widget.Mouse Update` stereo branch forced a fixed world direction using `FindLookAtRotation((0,0,0),(0,-1,0))` every update.

v12 instead reads `PointerComponent.K2_GetComponentRotation` and passes it to the existing WidgetInteraction SetWorldRotation call. It preserves the function's 434-byte runtime script size, jump targets, global cursor gate, and trigger handling. Other exports in that widget package are copied unchanged from the original.

The patcher checks bytecode control flow and context skip lengths. The diagnostic verifier evaluates 64 state combinations. Archive validation checks all 15 entries. These checks do not substitute for a headset test: verify startup trigger input, menu hover/selection, pause/options interaction, gameplay aiming, and both eyes' rendering before publishing another version.

## Release workflow

Make source changes in this checkout, validate locally, commit the scripts and notes, then attach a versioned install ZIP to a GitHub release pointing at that commit. Keep generated assets out of Git history. The initial v12 release was confirmed working by the user on October 28, 2026.
