# Windows side of one Microduck training job. Run by the "MicroduckTrain" scheduled task, as lelan, with nobody
# needing to be logged in. A Windows task (not an SSH session) has to start Linux: WSL stops Linux a few
# seconds after the last connection to it closes, and a training run would die with it.
# The job is in C:\Users\lelan\microduck-runs\job.env (written by the laptop's `pc-train start`):
#   NAME, ITERATIONS, ENVS, RESUME_RUN, RESUME_CKPT (read by pc-run.sh), SHUTDOWN=1|0, POWER_LIMIT=<watts>

$dir = 'C:\Users\lelan\microduck-runs'
$job = (Get-Content "$dir\job.env" -Raw) -replace "`r", '' | ConvertFrom-StringData
$note = "$dir\$($job.NAME).windows.log"
"started $(Get-Date -Format s)" | Out-File $note

# Optional: a lower graphics-card power limit means less heat and fan noise, and slightly slower training.
if ($job.POWER_LIMIT) { & nvidia-smi.exe -pl $job.POWER_LIMIT 2>&1 | Out-File -Append $note }

& C:\Windows\System32\wsl.exe -d Ubuntu-24.04 -- bash -lc '~/pc-run.sh'
"training ended (exit $LASTEXITCODE) $(Get-Date -Format s)" | Out-File -Append $note

if ($job.POWER_LIMIT) { & nvidia-smi.exe -pl 170 2>&1 | Out-File -Append $note }

# Shut down from Windows itself. (Asking Windows to shut down from inside Linux didn't work on 2026-11-03.)
# Five minutes' grace lets the laptop fetch the result first; the results stay on C: either way.
if ($job.SHUTDOWN -eq '1') {
    "shutting down in 5 minutes $(Get-Date -Format s)" | Out-File -Append $note
    shutdown.exe /s /t 300 /c "Microduck training finished: shutting down in 5 minutes. To cancel: shutdown /a"
}
