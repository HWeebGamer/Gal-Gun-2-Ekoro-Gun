# v25: bound marker size independently of crosshair mesh scale

The user reported a room-sized pink sheet from the v24 marker while finding the beam acceptable. v24 multiplied the crosshair component's world scale by a fraction and applied it to a different mesh; the crosshair's unverified source dimensions made that sizing assumption unsuitable.

v25 instead derives dot diameter from HitDistance and clamps it to 0.4–1.5 cm. The scale applied to the 100 cm cylinder is clamp(distance_cm * .000012, .004, .015). Thickness, position just behind the center, color, opacity, and component lifecycle are unchanged. The beam's 3 mm diameter, lighter pink and 50% alpha remain unchanged. The no-laser payload is unchanged.

Build and verify control with --bounded-dot; package with -BoundedDot and package_laser_variants.py --version 25. The evaluator retains 192 lifecycle/input cases and adds 24 combinations spanning 1 cm to 1 km distance and hypothetical crosshair scales .001 to 10000. Dot size stays within the prescribed bounds and does not depend on that scale. All 23 archive entries pass UnrealPak validation. Headset appearance remains to be confirmed.
