# 11-20 night chain: kitchen night bake -> resume the paused hall bake -> shut the PC down (his word, 11-20).
$ErrorActionPreference = 'Continue'
$log = "$PSScriptRoot\bake_chain.log"
function Say($m) { "$(Get-Date -Format 'HH:mm:ss')  $m" | Tee-Object -FilePath $log -Append }

Say 'kitchen bake starting'
& 'C:\Program Files\Git\bin\bash.exe' "$PSScriptRoot/room-kitchen/bake_kitchen.sh" 2>&1 | ForEach-Object { Say "kitchen: $_" }
Say 'kitchen bake finished'

Add-Type -Namespace W -Name N -MemberDefinition '[DllImport("ntdll.dll")] public static extern int NtResumeProcess(System.IntPtr h);'
$hall = Get-Process -Id 11560 -ErrorAction SilentlyContinue
if ($hall) {
  Say ('resuming hall bake (PID 11560): ' + [W.N]::NtResumeProcess($hall.Handle))
  $hall.WaitForExit()
  Say 'hall blender exited'
} else { Say 'hall blender (11560) not found - skipped' }

Start-Sleep -Seconds 60   # let bake_hall.sh write its tail lines
Say 'shutting down in 5 min (cancel: shutdown /a)'
shutdown /s /t 300 /c "Urban Nest bakes done - shutting down in 5 minutes. Run 'shutdown /a' to cancel."
