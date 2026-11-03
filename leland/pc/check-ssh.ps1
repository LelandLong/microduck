# Read-only check: why can't the laptop reach this PC's SSH server? Changes nothing.
# Run in an ADMINISTRATOR PowerShell on the gaming PC, then photograph the output for Claude.

Write-Host "== SSH server"
Get-Service sshd | Format-Table -AutoSize Name, Status, StartType
Write-Host "== Listening on port 22?"
netstat -an | Select-String ":22 " | Select-String "LISTENING"
Write-Host "== Firewall rules for SSH"
Get-NetFirewallRule -DisplayName *ssh* -ErrorAction SilentlyContinue |
  ForEach-Object { $a = $_ | Get-NetFirewallAddressFilter; [pscustomobject]@{ Name = $_.Name; Enabled = $_.Enabled; Profile = $_.Profile; Action = $_.Action; From = ($a.RemoteAddress -join ",") } } |
  Format-Table -AutoSize
Write-Host "== Network profile (Public or Private)"
Get-NetConnectionProfile | Format-Table -AutoSize InterfaceAlias, Name, NetworkCategory
Write-Host "== Firewall on per profile"
Get-NetFirewallProfile | Format-Table -AutoSize Name, Enabled, DefaultInboundAction
Write-Host "== Security apps Windows knows about"
Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct -ErrorAction SilentlyContinue | Format-Table -AutoSize displayName
Get-CimInstance -Namespace root/SecurityCenter2 -ClassName FirewallProduct -ErrorAction SilentlyContinue | Format-Table -AutoSize displayName
