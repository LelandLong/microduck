#!/bin/bash
# Linux side of one training job on the gaming PC (inside WSL). Started by pc-train.ps1, which the
# MicroduckTrain Windows task runs. The job is described in C:\Users\lelan\microduck-runs\job.env:
#   NAME=first-4000  ITERATIONS=4000  ENVS=4096  [RESUME_RUN=<run dir regex>  RESUME_CKPT=model_749.pt]
# Writes NAME.log, NAME.status and (at the end) NAME.tgz into that same folder, so the laptop can read them
# from Windows without starting Linux.
set -u
out=/mnt/c/Users/lelan/microduck-runs
source <(tr -d '\r' < "$out/job.env")
ENVS=${ENVS:-4096}
status="$out/$NAME.status"
log="$out/$NAME.log"

cd ~/microduck_rl
export PATH="$HOME/.local/bin:$PATH" WANDB_MODE=disabled
echo "running since $(date '+%F %T')" > "$status"

args=(Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs "$ENVS" --agent.max-iterations "$ITERATIONS" --agent.run-name "$NAME")
if [ -n "${RESUME_RUN:-}" ]; then
    # mjlab matches the whole run folder name (e.g. 2026-11-03_17-46-58_first-750), so a short name needs ".*" in front.
    args+=(--agent.resume True --agent.load-run ".*$RESUME_RUN" --agent.load-checkpoint "${RESUME_CKPT:-model_.*.pt}")
fi
uv run train "${args[@]}" > "$log" 2>&1
rc=$?

run=$(ls -td logs/rsl_rl/*/*_"$NAME" 2>/dev/null | head -1)
if [ -n "$run" ]; then
    tar -czf "$out/$NAME.tgz" -C "$(dirname "$run")" "$(basename "$run")"
fi
echo "finished rc=$rc at $(date '+%F %T') run=$(basename "${run:-none}")" > "$status"
exit $rc
