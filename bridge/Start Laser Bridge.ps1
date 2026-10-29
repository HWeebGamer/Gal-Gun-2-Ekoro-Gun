$ErrorActionPreference = 'Stop'
$gameRoot = Split-Path $PSScriptRoot
$game = Get-Process -Name GalGun2-Win64-Shipping -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -eq (Join-Path $gameRoot 'GalGun2\Binaries\Win64\GalGun2-Win64-Shipping.exe') } |
    Select-Object -First 1
if(-not $game) { throw 'Start GalGun2 first, then run Start Laser Bridge.cmd.' }
$exe = Join-Path $PSScriptRoot 'EkoroLaserBridge.exe'
$existing = Get-Process -Name EkoroLaserBridge -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq $exe}
if(-not $existing) {
    $bridge = Start-Process -FilePath $exe -ArgumentList ('"'+$gameRoot+'"') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $PSScriptRoot 'bridge.log') -RedirectStandardError (Join-Path $PSScriptRoot 'bridge-error.log')
    Start-Sleep -Milliseconds 500
    if($bridge.HasExited) { throw "Bridge exited. See $PSScriptRoot\bridge.log" }
}
Add-Type -AssemblyName Microsoft.VisualBasic
[Microsoft.VisualBasic.Interaction]::AppActivate($game.Id)
Write-Host 'Right A laser bridge is running. Keep the game window focused. It stops when the game closes.'
