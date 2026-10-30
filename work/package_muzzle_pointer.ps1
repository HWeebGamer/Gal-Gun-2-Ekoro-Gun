param([switch]$MenuVisibility,[switch]$MenuInteraction,[switch]$MenuRayFix,[switch]$NativeMenuConfirm,[switch]$RestoreMenuInitialization,[switch]$ScopedHover,[switch]$InteractionDiagnostic,[switch]$MenuRayAlignment,[switch]$ReticleDistance,[switch]$DynamicReticle,[switch]$HeartMuzzle,[switch]$SubtleHearts,[switch]$BriefHearts,[switch]$LaserSight,[switch]$RightALaser,[switch]$LaserBridge,[switch]$AlwaysLaser,[switch]$AlignedLaser,[switch]$VisibleLaser,[switch]$LaserDot,[switch]$BoundedDot,[switch]$StoryChoices,[Parameter(Mandatory=$true)][string]$CookedDirectory,[Parameter(Mandatory=$true)][string]$UnrealPak)
if($BoundedDot) { $LaserDot = $true }
if($LaserDot) { $VisibleLaser = $true }
if($VisibleLaser) { $AlignedLaser = $true }
if($AlignedLaser) { $AlwaysLaser = $true }
if($AlwaysLaser) { $LaserSight = $true; $LaserBridge = $false; $RightALaser = $false }
if($LaserBridge) { $LaserSight = $true; $RightALaser = $false }
if($RightALaser) { $LaserSight = $true }
if($LaserSight) { $BriefHearts = $true }
if($BriefHearts) { $SubtleHearts = $true }
if($SubtleHearts) { $HeartMuzzle = $true }
if($HeartMuzzle) { $DynamicReticle = $true }
if($DynamicReticle) { $ReticleDistance = $true }
if($ReticleDistance) { $MenuRayAlignment = $true }
if($MenuRayAlignment) { $InteractionDiagnostic = $true }
$ErrorActionPreference = 'Stop'
$workspace = Split-Path $PSScriptRoot
$cooked = $CookedDirectory
New-Item -ItemType Directory -Force (Join-Path $workspace 'outputs') | Out-Null
$output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v4_P.pak'
$payloadFolder = 'work\muzzle-pointer'
if($MenuVisibility) {
    $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v5_P.pak'
    $payloadFolder = 'work\muzzle-pointer-v5'
}
if($MenuInteraction) {
    $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v6_P.pak'
    $payloadFolder = 'work\muzzle-pointer-v6'
}
$response = Join-Path $workspace 'work\muzzle-pointer-response.txt'
if($MenuRayFix) {
    $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v7_P.pak'
    $payloadFolder = 'work\muzzle-pointer-v7'
}
$files = @(Get-ChildItem -LiteralPath $cooked -File | Where-Object {$_.BaseName -in @('SK_DevilSweeper_Grip','Ekoro_BaseColor','Ekoro_Prototype_Surface')})
if($NativeMenuConfirm) {
    $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v8_P.pak'
    $payloadFolder = 'work\muzzle-pointer-v8'
}
if ($files.Count -ne 7) { throw 'Expected seven unchanged mesh/material files' }
if($RestoreMenuInitialization) {
    $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v9_P.pak'
    $payloadFolder = 'work\muzzle-pointer-v8'
}
$lines = @($files | ForEach-Object { '"'+$_.FullName+'" "../../../GalGun2/Content/VRGG/Player/DevilSweeper/'+$_.Name+'"' })
if($ScopedHover) {
    $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v10_P.pak'
    $payloadFolder = 'work\muzzle-pointer-v10'
}
foreach($extension in @('uasset','uexp')) {
    if($InteractionDiagnostic) {
        $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v11_P.pak'
        $payloadFolder = 'work\muzzle-pointer-v11'
    }
    if($HeartMuzzle) { $payloadFolder = 'work\muzzle-pointer-v15' }
    if($StoryChoices) { $payloadFolder = 'work\muzzle-pointer-v26' }
    $file = Join-Path $workspace "$payloadFolder\VRGG\Player\VRGG_Pawn.$extension"
    $lines += '"'+$file+'" "../../../GalGun2/Content/VRGG/Player/VRGG_Pawn.'+$extension+'"'
}
$lines | Set-Content -LiteralPath $response -Encoding ASCII
if(($MenuInteraction -or $MenuRayFix -or $NativeMenuConfirm) -and -not $RestoreMenuInitialization) {
    foreach($extension in @('uasset','uexp')) {
        $file = Join-Path $workspace "work\muzzle-pointer-v6\VRGG\Widgets\VRGG_Widget.$extension"
        ('"'+$file+'" "../../../GalGun2/Content/VRGG/Widgets/VRGG_Widget.'+$extension+'"') | Add-Content -LiteralPath $response -Encoding ASCII
    }
}
if($ScopedHover -or $InteractionDiagnostic) {
    foreach($asset in @('Widgets/WidgetControl/VRGG_SelectControl_Widget','Widgets/Base/Title/VRGG_TitleMenu_Widget')) {
        foreach($extension in @('uasset','uexp')) {
            $file = Join-Path $workspace "work/muzzle-pointer-v10/VRGG/$asset.$extension"
            ('"'+$file+'" "../../../GalGun2/Content/VRGG/'+$asset+'.'+$extension+'"') | Add-Content -LiteralPath $response -Encoding ASCII
        }
    }
}
if($MenuRayAlignment) {
    $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v12_P.pak'
    foreach($extension in @('uasset','uexp')) {
        $file = Join-Path $workspace "work/muzzle-pointer-v12/VRGG/Widgets/VRGG_Widget.$extension"
        ('"'+$file+'" "../../../GalGun2/Content/VRGG/Widgets/VRGG_Widget.'+$extension+'"') | Add-Content -LiteralPath $response -Encoding ASCII
    }
}
if($ReticleDistance) {
    $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v13_P.pak'
    $pointerVersion = 'v13'
    if($DynamicReticle) {
        $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v14_P.pak'
        $pointerVersion = 'v14'
    }
    if($LaserSight) { $pointerVersion = 'v18' }
    if($LaserBridge) { $pointerVersion = 'v20' }
    if($AlwaysLaser) { $pointerVersion = 'v21' }
    if($AlignedLaser) { $pointerVersion = 'v22' }
    if($VisibleLaser) { $pointerVersion = 'v23' }
    if($LaserDot) { $pointerVersion = 'v24' }
    if($BoundedDot) { $pointerVersion = 'v25' }
    foreach($extension in @('uasset','uexp')) {
        $file = Join-Path $workspace "work/muzzle-pointer-$pointerVersion/VRGG/Actors/PointerComponent.$extension"
        ('"'+$file+'" "../../../GalGun2/Content/VRGG/Actors/PointerComponent.'+$extension+'"') | Add-Content -LiteralPath $response -Encoding ASCII
    }
}
if($HeartMuzzle) {
    $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v15_P.pak'
    $heartVersion = 'v15'
    if($SubtleHearts) {
        $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v16_P.pak'
        $heartVersion = 'v16'
    }
    if($BriefHearts) {
        $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v17_P.pak'
        $heartVersion = 'v17'
    }
    foreach($extension in @('uasset','uexp')) {
        $asset = 'Effect/Particles/Shooting/P_EkoroHearts'
        $file = Join-Path $workspace "work/muzzle-pointer-$heartVersion/VRGG/$asset.$extension"
        ('"'+$file+'" "../../../GalGun2/Content/VRGG/'+$asset+'.'+$extension+'"') | Add-Content -LiteralPath $response -Encoding ASCII
    }
}
if($LaserSight) {
    $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v18_P.pak'
    foreach($extension in @('uasset','uexp')) {
        $asset = 'Effect/Particles/Shooting/P_EkoroLaser'
        $laserVersion = if($LaserDot) {'v24'} elseif($VisibleLaser) {'v23'} else {'v18'}
        $file = Join-Path $workspace "work/muzzle-pointer-$laserVersion/VRGG/$asset.$extension"
        ('"'+$file+'" "../../../GalGun2/Content/VRGG/'+$asset+'.'+$extension+'"') | Add-Content -LiteralPath $response -Encoding ASCII
    }
}
if($RightALaser -or $LaserBridge) {
    $inputVersion = if($LaserBridge) {'v20'} else {'v19'}
    $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v19_P.pak'
    foreach($extension in @('uasset','uexp')) {
        $asset = 'Player/Utils/PlayerInputFunctionLibrary'
        $file = Join-Path $workspace "work/muzzle-pointer-$inputVersion/VRGG/$asset.$extension"
        ('"'+$file+'" "../../../GalGun2/Content/VRGG/'+$asset+'.'+$extension+'"') | Add-Content -LiteralPath $response -Encoding ASCII
    }
}
if($LaserBridge) { $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v20_P.pak' }
if($AlwaysLaser) { $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v21_P.pak' }
if($AlignedLaser) { $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v22_P.pak' }
if($VisibleLaser) { $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v23_P.pak' }
if($LaserDot) {
    $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v24_P.pak'
    foreach($extension in @('uasset','uexp')) {
        $asset = 'Effect/Particles/Shooting/P_EkoroLaserDot'
        $file = Join-Path $workspace "work/muzzle-pointer-v24/VRGG/$asset.$extension"
        ('"'+$file+'" "../../../GalGun2/Content/VRGG/'+$asset+'.'+$extension+'"') | Add-Content -LiteralPath $response -Encoding ASCII
    }
}
if($BoundedDot) { $output = Join-Path $workspace 'outputs\EkoroMuzzlePointer_v25_P.pak' }
if($StoryChoices) {
    $output = Join-Path $workspace $(if($LaserSight) {'outputs\EkoroMuzzlePointer_v26_P.pak'} else {'outputs\EkoroMuzzlePointer_v26_NoLaser_P.pak'})
    foreach($extension in @('uasset','uexp')) {
        $asset = 'Widgets/Demo/VRGG_TalkSelectActor'
        $file = Join-Path $workspace "work/muzzle-pointer-v26/VRGG/$asset.$extension"
        ('"'+$file+'" "../../../GalGun2/Content/VRGG/'+$asset+'.'+$extension+'"') | Add-Content -LiteralPath $response -Encoding ASCII
    }
}
& $unrealPak $output "-create=$response" '-compress'
if ($LASTEXITCODE -ne 0) { throw 'Package creation failed' }
& $unrealPak $output '-test'
if ($LASTEXITCODE -ne 0) { throw 'Package validation failed' }
& $unrealPak $output '-list'
if ($LASTEXITCODE -ne 0) { throw 'Package listing failed' }
