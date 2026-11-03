# Lets my laptop log in to this PC over SSH: home network only, my laptop's key only, no passwords.
# Run once in an ADMINISTRATOR PowerShell on the gaming PC (RERUN_GAMER). Safe to run again.
# Written 2026-11-03 for Leland's Microduck setup; see leland/MACHINES.md.

$ErrorActionPreference = "Stop"

Write-Host "1/4  Installing the OpenSSH server (Windows' own, can take a few minutes)..."
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-Null
Set-Service -Name sshd -StartupType Automatic
Start-Service sshd

Write-Host "2/4  Firewall: only devices on the home network may connect..."
# The rule only applies on Private networks, and Windows had the home Ethernet marked Public.
Set-NetConnectionProfile -InterfaceAlias Ethernet -NetworkCategory Private
Set-NetFirewallRule -Name OpenSSH-Server-In-TCP -RemoteAddress LocalSubnet

Write-Host "3/4  Trusting my laptop's key (public half, from github.com/LelandLong.keys)..."
$key = (Invoke-RestMethod https://github.com/LelandLong.keys).Trim()
if (-not $key.StartsWith("ssh-")) { throw "Didn't get a key from GitHub: $key" }
# Administrators' keys live here (Windows ignores ~/.ssh for admins), readable only by admins and SYSTEM.
$adm = "$env:ProgramData\ssh\administrators_authorized_keys"
Set-Content -Path $adm -Value $key -Encoding ascii
icacls.exe $adm /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F" | Out-Null
# And here, in case this account isn't an administrator.
New-Item -ItemType Directory -Force "$env:USERPROFILE\.ssh" | Out-Null
Set-Content -Path "$env:USERPROFILE\.ssh\authorized_keys" -Value $key -Encoding ascii

Write-Host "4/4  Keys only: switching password logins off..."
$cfg = "$env:ProgramData\ssh\sshd_config"
# Both password routes: "password" and "keyboard-interactive" (which on Windows also asks for the password).
$c = (Get-Content $cfg) -replace '^#?\s*PasswordAuthentication\s.*', 'PasswordAuthentication no' -replace '^#?\s*KbdInteractiveAuthentication\s.*', ''
Set-Content $cfg (@('KbdInteractiveAuthentication no') + $c)
Restart-Service sshd

Write-Host ""
Write-Host "Done. SSH server: $((Get-Service sshd).Status). This PC: $env:COMPUTERNAME, user $env:USERNAME."
Write-Host "Tell Claude it's done."
