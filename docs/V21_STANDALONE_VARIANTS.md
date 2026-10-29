# Standalone laser editions

The user replaced the controller-toggle plan with two mutually exclusive pak editions. Neither requires the bridge or changes controller bindings.

- Laser Always On: v21, under-barrel attachment and faint converging beam automatically active while gameplay aiming is enabled. Beam remains hidden in menus/disabled aiming contexts.
- No Laser: the previously confirmed v17 payload, without the beam or its attachment; retains the gun, crosshair/menu improvements and brief heart effects.

The v20 bridge detected and forwarded physical A, but activation crashed. The saved minidump's faulting instruction was `movaps xmm2,[rdx+10h]` with unaligned RDX ending in 0xcb4. The laser passed a nested MakeTransform expression directly to the native const-reference K2_SetWorldTransform argument. v21 materializes the result in the existing CallFunc_MakeTransform_ReturnValue local before passing that local. This addresses the observed alignment failure; headset confirmation is still required. The offline evaluator alone cannot prove native execution.

Build with work/build_laser_control.py --always-on; verify with work/verify_laser_control.py --always-on. Package with work/package_muzzle_pointer.ps1 -AlwaysLaser using the v18 attachment mesh snapshot. work/package_laser_variants.py creates both edition folders and ZIPs, identical installed filenames, SHA256 records and installation instructions. Always On has 21 checked archive entries; No Laser has 19. Validation includes 64 control cases, convergence, and assertions that the always-on bytecode has no input polling and passes the stored transform to the beam component.

Always On installed locally; prior v20 pak/sig and companion files backed up under G:\GalGun2-ModWork\backups\prototype-v20. The installed EkoroLaserBridge folder was removed after per-file backup checksum verification. No startup entries or global bindings were created. Original game archives remain unchanged. Install only one edition's EkoroPrototype_P.pak/.sig pair at a time. Not published.
