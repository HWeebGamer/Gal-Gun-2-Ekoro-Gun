# v19 laser input diagnosis

Read-only inspection during a mission found the added PointerComponent fields loaded and correctly linked. EkoroLaserEnabled remained false and EkoroLaserBeam remained null, including after the user held right A. IsUsingDualMotionControllers and IsCameraControlAndReticleEnabled were true; ForceHideAimReticle was false. Beam rendering has therefore not yet been tested by this attempt.

The active runtime uses SteamVR with the ALVR driver. SteamVR's vrserver log explicitly records loading drivers/oculus/resources/input/legacy_bindings_touch.json for steam.app.851890. That binding maps physical right A to right_a_press and B to right_applicationmenu_press.

The installed UE4.18 SteamVRController.cpp handles System, ApplicationMenu, TouchPadPress/Touch, TriggerPress, Grip and emulated touchpad directions. It does not read k_EButton_A. ApplicationMenu maps to MotionController_Right_Shoulder; MotionController_Right_FaceButton1 is an emulated touchpad-up click, not physical A on this input path. The previous native-Oculus-based assumption was incorrect for this runtime. The game's customized native code has not been fully disassembled, so the engine-source mapping remains evidence for the cause rather than a complete binary audit.

Next implementation depends on the user's preference: reserve right B's supported menu input and retain pak-only distribution, or keep physical A with an additional input bridge. Any next build should also remove v19's unconditional FaceButton1 filter on SteamVR, because it targets a touchpad direction there. Do not substitute another key while claiming it is physical A.

Keep v19 installed until the replacement is built and validated; back it up before installation. No rendering changes are justified yet by these observations. Beam lifetime, transform, alpha and actual two-eye visibility still need testing after a working input activates the component.
