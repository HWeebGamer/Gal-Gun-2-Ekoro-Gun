# v22: store the beam direction before rotation

The user confirmed v21 renders without the prior activation crash, but provided a screenshot of a detached, misaligned beam.

UE4.18's KismetMathLibrary.MakeRotFromZ takes `const FVector&`. FFrame::StepCompiledInRef returns MostRecentPropertyAddress when set by expression evaluation, rather than necessarily returning the temporary result. Passing the nested Subtract_VectorVector expression directly can therefore use a referenced input instead of the calculated direction. This is the same class of VM argument issue that required storing the transform in v21.

v22 stores HitLocation minus laser-source position in the existing CallFunc_Subtract_VectorVector_ReturnValue local, then passes that local to MakeRotFromZ. The local's original last read occurs before the hook; no subsequent original code reads it. The transform still uses the existing stored-transform fix. No mesh, attachment offset, brightness, particle settings, input mappings, or no-laser payload changes.

Build and verify with build_laser_control.py --aligned and verify_laser_control.py --aligned. Package with package_muzzle_pointer.ps1 -AlignedLaser and package_laser_variants.py --version 22. Validation checks both reference arguments are locals, absence of input polling, 64 control cases, near/far/behind endpoints, and translated world positions. UnrealPak validated all 21 entries. These checks do not replace headset alignment verification.

Installed with verified v21 backup at G:\GalGun2-ModWork\backups\prototype-v21. Both standalone ZIPs are under outputs/variants-v22. No Laser remains byte-identical to the previously confirmed v17 payload. Not published.
