# v23: visibility and inactive-component recovery

The user reported a barely visible beam before mission selection and no visible beam during the mission. The cause of disappearance was not confirmed with live inspection.

The always-on edition increases diameter from 0.1 cm to 0.3 cm and particle alpha from 0.10 to 0.30. It retains the pink color, alignment fixes, gameplay gating and normal depth testing. When the stored particle component exists but IsActive is false, it calls Activate(true) before updating its transform. This handles deactivated/completed components without spawning another component every frame; it is not proof that deactivation caused the reported disappearance.

Build build_laser_control.py, build_laser_particle.py and verify_laser_control.py with --visible. Package with package_muzzle_pointer.ps1 -VisibleLaser and package_laser_variants.py --version 23. The evaluator runs the original 64 state combinations plus 64 with inactive beam state, checking recovery only when gameplay should show the beam. Alignment/local-reference checks and translated endpoint checks remain. All 21 archive entries validated.

Installed locally with checksum-verified v22 backup under G:\GalGun2-ModWork\backups\prototype-v22. The no-laser variant remains byte-identical to v17. No helper or controller-binding changes. Not published. Requires a headset test spanning mission entry to assess visibility and whether disappearance persists.
