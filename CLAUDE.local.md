# Leland's notes — Microduck (crossfeed seat: DUCK)

> **This file is committed** on the `leland` branch of Leland's **public** fork
> `LelandLong/microduck`, so it travels to Claude Cloud sessions. Anyone can read it: never put
> credentials, tokens or private contact details here. Pollen's `CLAUDE.md` / `AGENTS.md` are
> upstream: read and follow them, but never edit them for anything of Leland's (it would conflict
> with every upstream merge). `.claude/` (crossfeed hooks + skill) stays local-only via
> `.git/info/exclude`.

## What this is
- `~/microduck` is a fork of **`pollen-robotics/microduck`** (Apache-2.0), the software for
  Pollen Robotics' Microduck biped. Cloned 2026-10-30, forked to `LelandLong/microduck` the same day.
- Leland has **pre-purchased a Microduck; delivery is 4–6 months out.** Until it arrives, this seat
  exists to help him **explore, learn and try things in the simulator** (`scripts/duck-sim`,
  `docs/robot/simulation.md`) so he is ready on day one.
- The training side (MuJoCo + PPO, the policies the duck runs) is a separate repo,
  `pollen-robotics/microduck_rl`. It is **not cloned yet**; clone it beside this one if he wants it.

## Git layout (set up 2026-10-30)
- `origin` = `LelandLong/microduck` (his public fork). `upstream` = `pollen-robotics/microduck`.
- **`leland`** = his working branch and the fork's default branch: upstream code + `CLAUDE.local.md`
  + `leland/` (notes, session logs, video list). **`main`** stays a clean mirror of upstream, so a
  fix for Pollen can branch from it later.
- Sync with Pollen: `git fetch upstream && git checkout main && git merge --ff-only upstream/main &&
  git push origin main && git checkout leland && git merge main && git push origin leland`.
- This Mac's git is 2.15 (2017): pushes with media failed ("remote end hung up") until
  `git config http.postBuffer 157286400` (set repo-local 2026-11-03). No `git switch`; use `checkout`.
- Commits in this repo use his GitHub no-reply email (repo-local `user.email`), so his personal
  address never appears in the public history.

## Keeping everything in the repo (Leland's standing request, 2026-10-30)
- Leland wants **everything we discuss** in this repo so it is reachable from Claude Cloud.
- Durable facts and decisions go in this file. Longer material goes in `leland/`: one session log per
  day in `leland/sessions/YYYY-MM-DD.md`, reference material in `leland/` (see `leland/README.md`).
- At the end of each substantive turn: update the notes, **commit on `leland` and push to `origin`**
  (standing authorisation from Leland). Public repo: scrub anything private before committing.
- **Every `.md` in `leland/` (+ this file) has a sibling `.html`** (Leland, 2026-11-03: raw markdown is
  "eye strain and brain melt down"). Renderer: `leland/tools/md-render-sibling.mjs`, ported from
  keller-portal. A local PostToolUse hook runs `--auto` after Edit/Write; edits made via Bash don't
  trigger it, so **run `node leland/tools/md-render-sibling.mjs --auto` before every commit** (in a
  cloud session, `npm install` in `leland/tools` first). Commit the `.html` files too.
- Videos/images for notes go in `leland/media/`. Recipe for the learning-stages video: export each
  `runs/<run>/checkpoints/model_N_steps.zip` (+ vecnormalize) with `export-walk` from a scratch run
  dir, film each with the walk env (`train.env_class("microduck","walk")`, domain_rand off, fixed
  `twist_cmd`), tile with PIL, write mp4 with imageio. Verify motion by distance, not by eval score.

## ▶ Where we are right now (updated 2026-11-03 ~17:30, read this first)
- **Today's done:** Mac Studio connected (`ssh studio`), fully installed, simulator verified, training race
  (Studio 2.2x laptop). Gaming PC connected (`ssh pc`, key only, passwords off). See `leland/MACHINES.md`.
- **Done 17:45: PC has WSL 3.0.3 + Ubuntu 24.04 + `~/microduck_rl`; GPU training test ran, 3.66 s/iteration**
  (750 it ≈ 46 min, 4,000 ≈ 4 h). Details in `leland/MACHINES.md`. **Next:** Wake-on-LAN (needs BIOS +
  adapter settings, MAC `50:eb:f6:ca:72:a1`) + auto-shutdown after runs; **First real run started 17:46: 750 it, `--agent.run-name first-750`,
  script `~/run-first-750.sh` (status `~/first-750.status`, log `~/first-750.log`), shuts the PC down 10 min after.**
  Resume later with `--agent.resume True --agent.load-run <run dir> --agent.load-checkpoint model_749.pt`
  (mjlab `rl/config.py`). Quoting tip: pipe scripts in with `ssh pc 'wsl -d Ubuntu-24.04 -- bash -s' <<'EOF'`;
  inline `|` and `"` get mangled by Windows' cmd.
  GPU power cap optional. No ZeroTier, no remote-control apps on the PC.
- **18:31 first-750 finished (43m28s) and WALKS: 0.78/1.16/2.46 m at vx 0.15/0.3/0.5 in 8 s (alpha_walking 0.01/1.06/1.70)**
  in the microduck-lab harness. Copied to `~/microduck-runs/pc/` + `leland/policies/pc-first-750.onnx`. Auto-shutdown
  FAILED (shutdown.exe from a nohup'd WSL process); PC shut down by hand 18:39. `ssh pc` → 192.168.1.194 (mDNS flaky).
  **Never send `shutdown /a` to check status**: it cancels a pending shutdown.
- **Metal project (`leland/METAL.md`):** warp-metal works on both Macs (`~/Pollen/microduck_rl-metal`, DavidDobas `metal`
  branch + local `mujoco==3.11.0` pin). Studio M4 Max 4.0 s/it (90% of 3060), M1 Pro 13.7 s/it; Studio 750-run (48 min)
  WALKS 0.53/1.32/2.12 m. **First open-source contribution posted: innate-inc/warp-metal#10.** Starred warp-metal +
  DavidDobas/microduck_rl. Next: watch for David's reply; offer branch update PR; fixed-seed like-for-like run.
- **PC complete 2026-11-03 21:50:** `leland/tools/pc-train` wakes (WoL works after BIOS ErP off + Power On By PCI-E on +
  Fast Startup off), trains via Windows task `MicroduckTrain` (S4U; WSL dies without a client otherwise), packs to
  `C:\Users\lelan\microduck-runs`, auto-shutdown from Windows 5 min after. Tested end to end. Details `leland/MACHINES.md`.
- **Overnight 2026-11-03 → 04 (Leland approved the phased plan):** PC `walk-4000` = resume first-750 → 3999 (`pc-train start walk-4000 3250
  --resume first-750 model_749.pt --power 130`; mjlab counts resume iterations as EXTRA, and `load-run` must match the whole
  folder name, so pc-run.sh prefixes `.*`), ETA ~01:40, auto-off. Studio `standup-750` (Mjlab-StandUp-Flat-MicroDuck, Metal,
  background; osascript Terminal failed -10810 = screen locked). Tomorrow: report cards (walk test, video, duck-sim).
- **2026-11-04 morning report cards done (TRAINING.md §13):** `walk-4000` walks STRAIGHT (first-750 curved ~70°),
  runs in full `duck-sim`/robotd (swap via a temporary `policies/` dir beside the repo, which duck-sim prefers).
  **Metal branch bug found:** mjlab 1.6 + unnamed geoms → only feet touch the floor in ground-contact tasks, so the
  Studio StandUp brain is INVALID (walking unaffected). Comment POSTED on warp-metal#10 2026-11-04.
  StandUp retraining on the PC (`pc-train start standup-750 750 --task Mjlab-StandUp-Flat-MicroDuck --power 130`, 10:21). Scripts `leland/tools/report-card/` (StandUp tests run on the Studio, device "cpu").
- Leland left the house 2026-11-03 evening; laptop + PC left on (laptop kept awake with `caffeinate` for 12 h).
- **A Claude Cloud session can't reach the Studio or the PC** (they're on the home network; the cloud isn't).
  For hands-on work from the iPhone, use **Remote Control** of the laptop session instead. A cloud session is
  fine for reading and editing these notes, and for planning and learning.

## Session start
1. This file, then the upstream `CLAUDE.md`, then the newest `leland/sessions/` log.
2. **On the laptop only:** run the crossfeed skill (seat **DUCK**, personal group); credentials
   `~/crossfeed/access/crossfeed-DUCK.env`, named inline. **In a Claude Cloud session** there is no
   `~/crossfeed`, no hooks and no skill: skip crossfeed entirely.
3. Now and then, sync with Pollen (command above): upstream moves daily.
4. (History: XFD-069, the setup handover, was read and marked 2026-10-30; its durable parts are below.)

## Working with Leland (house rules from his other projects)
- Plain English, no jargon. Short bullets first, detail after, and **every substantive reply ends
  with a summary**.
- He's an experienced Swift/iOS developer and knows Apple tooling well. Rust, robotics and
  reinforcement learning are new to him here, so teach those properly without talking down.
- Verify, don't recall: time comes from `date`, and nothing is called working until it has been run.
- **Never install system-wide software (Homebrew packages, Rust toolchains, Python environments)
  without telling him first** what it is and roughly how big it is.

## Handover from XFD-069 (copied 2026-10-30)

### The Mac (measured by XFD 2026-10-30, re-check before relying on it)
- Apple Silicon (arm64), macOS 26.6.2, 32 GB RAM, Homebrew 7.0.11, Python 3.11.3.
- **Missing:** Rust (`rustup`/`cargo`), `uv`, Docker, GStreamer, git-lfs.
- **Disk: quote Finder's "available" figure, never plain free space** (Leland, 2026-11-03: he relies on
  Finder, and the lower number irritated him). Finder's figure = `volumeAvailableCapacityForImportantUsage`
  (69.41 GB on 2026-11-03, matched his Finder exactly). The ~33 GB gap is purgeable space macOS clears on
  demand: mostly `~/Library/Caches` (24 GB) and local copies of iCloud/OneDrive/Dropbox files (~9 GB).
  Measure it with a Swift `URL.resourceValues` check, not `df`.

### Local simulator notes (from `docs/robot/simulation.md`; read it yourself)
- `scripts/duck-sim` runs the real daemons against a MuJoCo body. Commands: `duck-sim`, `status`,
  `drive`, `ctl <robotctl args>`, `monitor`, `log`, `down`.
- Needs this repo built with cargo plus a `microduck_rl` checkout with its venv (default
  `~/Pollen/microduck_rl`, override `DUCK_SIM_RL`). Camera needs `brew install gstreamer
  libnice-gstreamer` and microduck_rl's `develop` branch.
- `duck-sim boot N` (multi-duck) needs `systemd-nspawn`/`mmdebstrap`: probably Linux-only (unverified).
- microduck_rl says training needs CUDA, but its venv should install on the Mac for `duck-body` (CPU
  MuJoCo): checked 2026-11-03 against its `uv.lock`, every package has a macOS arm64 build except
  Linux-only NVIDIA/CUDA packages (skipped on Mac) and BAM (installed from git). Not yet run.

### Options offered to Leland, easiest first (none picked as of 2026-10-30)
1. Browser simulator, zero install: https://huggingface.co/spaces/pollen-robotics/microduck-simulator
2. Policy Playground (https://huggingface.co/spaces/pollen-robotics/microduck-policy-playground) and
   Arena leaderboard (https://huggingface.co/spaces/pollen-robotics/microduck-arena).
3. Full local simulator (`scripts/duck-sim`): Rust + microduck_rl + disk.
4. Train his own tricks: official needs CUDA; alternatives are `--hf-jobs` (paid) or community
   https://github.com/jonathanhawkins/microduck-lab (claims Mac training, unverified).
5. Build an app: SwiftUI iPhone app over Bluetooth (`btd`/`duckctl`) or WebRTC (`docs/faq.md`, `spaces/`).
6. Build a replica now: e.g. https://github.com/fanhao375/microduck-replica,
   https://github.com/LuwuDynamics/xgoduck_hardware.
- TypeSafe/Jev (raise when it fits): fits "what should the duck do next" decisions; NOT walking/balance.

**Open decisions:** browser vs. local sim first; whether to clone microduck_rl; which of 1–6.

### Reading map
`README.md`, `docs/README.md`, `docs/faq.md`, `docs/robot/simulation.md`, `docs/robot/cheatsheet.md`,
`docs/design/architecture.md`, `docs/project/roadmap.md`, and https://github.com/joeynyc/awesome-microduck
(says first units before Christmas 2026; official policies at `pollen-robotics/microduck-policies`).

### Seat gotcha
- (Laptop only) set the crossfeed resting status with `~/crossfeed/set-status.sh` **before** writing the final reply.

### HF Jobs cost for `microduck_rl --hf-jobs` (researched 2026-10-30)
- microduck_rl `scripts/hf/README.md`: default `--flavor l4x1`, also `a10g-large` / `a100-large`;
  default `--timeout 12h`. Also uploads source + checkpoints to private HF repos, a uv-cache bucket,
  and forwards wandb (optional, `--no-wandb`). `--dry-run` prints the job without submitting.
- HF price list (docs/hub/jobs-pricing): L4 $0.80/h, A10G-large $1.50/h, A100 $2.50/h; billed per
  minute; needs a **positive prepaid credit balance**. Default 12 h timeout caps one L4 run at $9.60.
- Not yet known: how fast an L4 trains the duck vs. the README's "1–2 h for a usable gait".

### Leland's gaming PC (from his System Information screenshots, 2026-10-30)
- ASUS ROG Strix G15CF desktop, Windows 11 Home, i7-12700F (12 cores/20 threads), 16 GB RAM,
  **NVIDIA RTX 3060, 12 GB** (confirmed in Task Manager 2026-11-03),
  driver 32.0.15.9636 = NVIDIA 596.36.
- **PC plan Leland likes (2026-11-03):** Claude wakes it from the laptop (Wake-on-LAN; check BIOS +
  network-adapter setting, it's wired) and every training run **shuts it down at the end**. Worries: being
  used as a bot while unattended, fan noise, heat in his office. Reassurance plan: no router port forwards,
  SSH key-only from the home subnet via Windows Firewall, no ZeroTier on it, no remote-control apps,
  Defender + updates on, optional AT&T per-device internet block, optional GPU power cap (~170 → 120 W).
- From his screenshots 2026-11-03: name **RERUN_GAMER**, Windows user `lelan`, build 26200, UEFI + Secure
  Boot, BIOS G15CF.301 (2022), **"Virtualization-based security: Running" = CPU virtualization already on**
  (WSL2 needs it), three screens (5760x1080). **VRAM 12.0 GB** (Task Manager; msinfo's "1 MB" is a
  4 GB-field bug), driver 596.49. **C: NVMe SSD, 124 of 453 GB free; D: "DATA" SATA hard drive, 887 of 931
  GB free.** WSL2 disk needs 20–50 GB; where it goes is Leland's choice (see `leland/MACHINES.md`).
- He mainly games on it. Wants the **Mac as home base** and the PC as an optimized training step,
  not a daily workstation.
- mjlab (microduck_rl's engine) officially: training **Linux only**, WSL listed for evaluation only;
  needs Turing+ GPU and driver ≥ 580 (3060 + 596 both qualify). WSL2 training: officially unlisted, but
  Kevin Wood trains Microduck in WSL2 on Windows in his video (see below), so expected to work.

### YouTube learning list given to Leland (2026-10-30; titles/channels checked, videos not watched)
- Best channels found: **Pollen Robotics** (official), **Remi Fabre** (Microduck RL/expressive clips),
  **Kevin Wood | Robotics & AI** (Microduck mjlab training on Windows/Linux: ZDvCdIFXANw),
  **DigiKey + Shawn Hymel** 6-part "Reinforcement Learning for Robotics" (MuJoCo + PPO + sim-to-real),
  sentdex G1 walking (FGnAeUXRZ4E).
- Avoid: Lifey Guy, OTOFOOTAGE, Code-Dixa and similar churn channels.
- Leland's plan as of 2026-10-30: not installing on the PC yet, "soon".

### Kevin Wood's Microduck training video (ZDvCdIFXANw), from the transcript Leland pasted 2026-10-30
- **Native Windows fails** (`uv run train` → "selected GPUs index out of range"). **WSL2 + Ubuntu works**:
  he trained on Windows via WSL. This answers our "WSL2 unverified" question (for his GPU, not yet ours).
- Steps: `wsl --install` (PowerShell) → in WSL `git clone` microduck_rl → `uv run train Mjlab-Velocity-Flat-MicroDuck ...`.
- First run asks about Weights & Biases; option **3** = don't visualise (no account needed).
- Default run is **50,000 iterations** (written `50_000` in code; override with `--agent.max_iterations`).
  ~**3.8 s/iteration** on his (unnamed) GPU → full run ≈ 53 h. Nobody needs the full run:
  **walking already at 750 iterations (~48 min)**, clearly better at 4,000 (~4 h).
- Checkpoints saved every 250 iterations in `logs/rsl_rl/<task>/<date>/model_N.pt`; watch one mid-training:
  `uv run play <task> --checkpoint-file logs/rsl_rl/.../model_750.pt`.
- Sim-to-real lesson: the motors are modelled by **BAM** (Better Actuator Models, system identification of the
  Dynamixel servos); friction is the usual difference between a good and a bad policy.

### Disk budget for a full Mac setup (measured/estimated 2026-11-03)
- Available (Finder's figure): **69.4 GB**. Already present: Homebrew (2.2 GB cellar), Node.
- Core local simulator ≈ **8–10 GB**: Rust toolchain ~1.5 GB (est.); this repo's build (595 crates,
  debug `target/`) ~4–6 GB (est., grows; `cargo clean` reclaims); uv + Python 3.12 ~0.1 GB;
  microduck_rl repo + venv ~1.5–2 GB (**measured: 0.34 GB of Mac downloads**, ~3–4x unpacked).
- Optional: camera = GStreamer + libnice-gstreamer, **58 new Homebrew packages** (incl. GTK 3/4, a
  second Python) ~1.5–2.5 GB (est.); microduck-lab ~3 GB (its README).
- Everything ≈ **13–16 GB**, leaving ~53 GB. Not needed on the Mac: Docker, CUDA, git-lfs, multi-duck `boot`.

### Installed on the Mac (2026-11-03) — **the local simulator works**
- Rust 1.99.1 via rustup (`~/.rustup` 1.3 GB, `~/.cargo` 0.3 GB; shell needs `. "$HOME/.cargo/env"`),
  `uv` 0.13.7 via Homebrew, `~/Pollen/microduck_rl` + `.venv` (1.2 GB), uv cache 1.2 GB,
  this repo's `target/` 2.0 GB (daemons built in 51 s). **≈ 6 GB total**, less than the 8–10 GB estimate.
- `scripts/duck-sim` ran first time: MuJoCo window, duck stood up, loop 50.0/50 Hz, 0 missed ticks.
  Policies fetched automatically. Full write-up for Leland: `leland/INSTALL.md`.
- **`drive` with no args does NOT walk** (I wrongly reported it did: I only checked it was still
  standing). Default vx 0.15 is below the current walking policy's effective threshold (~0.25):
  measured 0.15 → 6 mm in 4 s, 0.20 → 8 mm, 0.30 → 45 cm, 0.50 → 82 cm. Use `drive 0.4 0`.
  Likely a stale script default worth reporting to Pollen.
- **Lesson: verify motion by measuring it.** The body's TCP port (7801) answers
  `{"op":"hello","protocol":1,"joints":15}` then `{"op":"read"}` with `trunk` [x,y,z]; compare before/after.
- **Round 2, same day: camera + microduck-lab installed and verified.** GStreamer 1.28.8 +
  libnice-gstreamer via brew (cellar 2.2 → 3.0 GB); `DUCK_SIM_CAMERAS=a scripts/duck-sim` → console
  http://127.0.0.1:8080, capture 32 fps, frame grabbed via `duck-a-frame.sock` (UYVY, rotate 90).
  microduck-lab at `~/microduck-lab` (1.9 GB, own pinned Pollen clones inside); first `train-walk`
  3M steps = 9 min, eval 0/20 falls, lin-vel error 0.23 m/s, **but it only STANDS**: 0.00 m at vx 0.15/0.3/0.5
  (Pollen's alpha_walking through the same harness: 1.06 m / 1.70 m). Explained in `leland/TRAINING.md`.
  Finder available after all: 63.2 GB.

### Mac Studio upstairs: connecting the laptop to it (started 2026-11-03)
- Goal: Leland's newer **Mac Studio** (wired to AT&T) usable headless from the laptop: Claude runs
  commands on it over SSH; Leland sees its screen with Screen Sharing. Then benchmark it for training.
- Laptop measured: **M1 Pro (8 performance + 2 efficiency cores), 32 GB**, on AT&T Wi-Fi,
  192.168.1.x. Two home networks (AT&T fiber, Spectrum cable): **both machines must be on AT&T**.
- Scan 2026-11-03: the Studio did **not** appear on the home network (no SSH, no Screen Sharing; the
  only Windows box answering is `TF-260416140219` at .201, probably the gaming PC). The Macs that do
  show up (names starting SAN/CHS) come over **ZeroTier** (`feth1592`, 192.168.193.x), almost
  certainly the Keller work network. **Not Leland's: never connect to them.**
- **Found 2026-11-03 16:00:** Bonjour name "CHS Leland Mac Studio (2025)", hostname
  `CHS-Leland-Mac-Studio-2025.local` (home 192.168.1.243/.167/.248, also on Keller ZeroTier). It is
  **Keller-owned**, with Remote Management on: Screen Sharing (5900) and ARD (3283) open, **SSH (22) closed**.
- **Connected 2026-11-03 16:05: `ssh studio` works** (user `lelandlong`, key `~/.ssh/id_ed25519`,
  `IdentitiesOnly yes`: the laptop agent holds 23 keys and the Studio drops you after 6 tries; old
  config backed up to `~/.ssh/config.bak-2026-11-03`). Host key ED25519 `SHA256:jO1/OvVI…fnU0`.
- **Studio measured:** Mac Studio Mac16,9, **M4 Max, 14 cores (10 performance + 4 efficiency), 32-core GPU,
  36 GB**, macOS 26.6.1, **135.7 GB available (Finder's figure)** of 494. Never sleeps (sleep 0, wake on
  network on). Has Xcode + git 2.50; **no Homebrew, uv, Rust or Node**. Leland: admin, in Keller IT, may
  install anything. At first login it was busy (load ~20–32): Spotlight indexing + preparing a macOS
  27.2 update; **don't benchmark while that's running**.
- **Studio fully installed 2026-11-03 (same as the laptop, Leland: "when I switch to studio I don't want
  to be limited")**: Homebrew (Leland ran the installer with his password via `ssh -t studio`; Claude can't
  sudo), uv 0.13.7, Node 26, gh, GStreamer 1.28.8 + libnice-gstreamer, Rust 1.99.1 (stable, 1.3 GB),
  `~/microduck` (fork, `leland` branch, `upstream` remote; daemons built in **32 s** vs laptop 51 s),
  `~/Pollen/microduck_rl` (develop `bae39f59`, .venv 1.1 GB), `~/microduck-lab` (`8dad921`, 1.8 GB,
  setup "Ready"), uv cache 1.6 GB, Homebrew cellar 1.4 GB. **Simulator verified: stands, loop 49.9/50 Hz,
  `drive 0.4 0` walked 1.31 m** (measured via port 7801).
- **Showing things on the Studio's screens:** `ssh studio 'osascript -e "tell application \"Terminal\" to
  do script \"…\""'` opens a Terminal window in Leland's logged-in desktop (he granted the Automation
  permission 2026-11-03). Run duck-sim, training and long jobs that way so he can watch upstairs.
  `duck-sim status` straight after launch can say "did not stand up": it's still starting, re-check.
- **Training race 2026-11-03 16:26** (same `train-walk --envs 32 --steps 3_000_000`, run at the same time,
  both machines quiet): **Studio 2 min 35 s (154.7 s, ~19,400 steps/s), laptop 5 min 36 s (335.9 s,
  ~8,950 steps/s): Studio 2.2x faster.** 16.7 h of duck practice in 2.6 min = ~390x real time. The laptop's
  earlier 9 min was slowed by the camera install running alongside. Runs: `runs/race-studio`, `runs/race-laptop`.
- Not yet on the Studio: VS Code + Claude Code, crossfeed (asked, unanswered).
- Steps Leland must do at the Studio once: Sharing → **Remote Login** on (and **Screen Sharing** on);
  note the "Local hostname"; Energy → prevent sleep when display off + wake for network access.
  Then from the laptop: `ssh-copy-id <user>@<hostname>.local` (he types the Studio password once)
  and an `ssh` alias `studio` in `~/.ssh/config`.
- Training on it: still **no CUDA on any Mac**, so official microduck_rl stays on the PC/HF Jobs.
  microduck-lab is CPU-bound, so a Studio with more cores should go faster: measure it with the same
  3M-step `first-gait` run (laptop: ~9 min, with an install running alongside).
