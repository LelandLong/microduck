# What's installed on my Mac for the Microduck

Installed 2026-11-03 on my MacBook Pro (Apple Silicon, macOS 26.6.2), in two rounds: the core
simulator (~6 GB), then the camera and microduck-lab (~3 GB more). **About 9 GB in total.** Finder's
available space: 69.4 GB before, **63.2 GB after**.

The **Mac Studio** upstairs has the same setup (2026-11-03): see [`MACHINES.md`](MACHINES.md).

## At a glance

| What | Version | Where | Size | Installed with |
|---|---|---|---|---|
| Rust toolchain (compiler `rustc`, build tool `cargo`, manager `rustup`) | Rust 1.99.1, rustup 1.29.3 | `~/.rustup`, `~/.cargo` | 1.3 GB + 0.3 GB | official installer from rustup.rs |
| `uv` (Python package and version manager) | 0.13.7 | `/opt/homebrew/Cellar/uv` | 34 MB | `brew install uv` |
| Python for the training repo | 3.12.16 | `~/.local/share/uv/python` | 70 MB | `uv`, automatically |
| **microduck_rl**, Pollen's training repo | branch `develop`, commit `bae39f59` | `~/Pollen/microduck_rl` | 1.2 GB (1.1 GB is its `.venv`) | `git clone` + `uv sync` |
| uv's download cache | | `~/.cache/uv` | 1.2 GB | `uv`, automatically |
| The duck's software, built for the Mac | 0.18.3 | `~/microduck/target` | 2.0 GB | `cargo build` (51 s) |
| The simulator's state, logs and the official policies | | `~/.cache/duck-sim` | ~20 MB | `scripts/duck-sim`, on first run |
| **GStreamer** + **libnice-gstreamer** (video for the simulated camera) | 1.28.8, 0.1.24 | `/opt/homebrew` (+ ~60 dependencies) | ~0.8 GB | `brew install gstreamer libnice-gstreamer` |
| **microduck-lab** (community: training on the Mac, no NVIDIA GPU) | commit `8dad921` | `~/microduck-lab` | 1.9 GB | `git clone` + its `./scripts/setup.sh` |

Nothing went into system folders. Everything except the Homebrew packages (`uv`, GStreamer) is inside
my home folder.

## What each piece is for

- **Rust**: the language the duck's software (`robotd`, `robotctl` and the rest) is written in.
  `cargo` compiles it. `rustup` keeps Rust up to date (`rustup update`).
- **uv**: installs Python and the Python libraries a project needs, kept inside that project (its
  `.venv` folder), so nothing clashes with my other Python installs.
- **microduck_rl**: Pollen's training repo. The simulator uses it for:
  - `duck-body`, the physics model of the duck (MuJoCo) that the real software drives
  - the scenes (floors, rooms)
  - the ONNX Runtime library that runs the duck's neural-network policies on the Mac

  It's also where training happens, but that needs an NVIDIA GPU, so not on this Mac.
- **`~/microduck/target`**: the compiled duck software. Safe to delete with `cargo clean`; the next
  `scripts/duck-sim` rebuilds it.
- **`~/.cache/duck-sim`**: the running duck's logs, sockets, config, and the 10 official policies
  (`alpha_walking.onnx`, `alpha_stand.onnx`, `roulade.onnx`, …) downloaded from the Hugging Face Hub.

## Changes to my shell setup

The Rust installer added one line, `. "$HOME/.cargo/env"`, to `~/.zshenv`, `~/.profile` and
`~/.bash_profile`, so `cargo` and `rustc` work in every new Terminal window. Nothing else changed.

## Using the simulator

From `~/microduck` in Terminal:

```sh
scripts/duck-sim                    # start: MuJoCo window opens, duck stands up
scripts/duck-sim drive 0.4 0        # walk forward 8 s   ← give a speed! see below
scripts/duck-sim drive 0.4 0.5      # walk while turning
scripts/duck-sim drive 0 0.8        # turn on the spot
scripts/duck-sim ctl robot do roulade   # forward roll
scripts/duck-sim status             # is it healthy and standing?
scripts/duck-sim monitor            # live joints and sensors
scripts/duck-sim log                # the daemon's log (Ctrl-C to leave)
scripts/duck-sim down               # stop everything, close the window
```

In the MuJoCo window: drag to rotate the view, scroll to zoom.

### ⚠️ `drive` with no numbers does nothing visible

`scripts/duck-sim drive` defaults to speed 0.15, and today's walking policy treats anything below
about 0.25 as "stand still". Measured 2026-11-03, 4 seconds at each speed:

| speed | distance | |
|---|---|---|
| 0.15 (default) | 6 mm | stands |
| 0.20 | 8 mm | stands |
| 0.30 | 45 cm | walks |
| 0.50 | 82 cm | walks |

So always give a speed of 0.3 or more. (The script's default is probably older than the current
policy; worth telling Pollen.)

## How I checked it works (2026-11-03)

- `scripts/duck-sim` started everything first time: duck stood up, control loop at 50.0 of 50 Hz.
- Walking checked by **measuring the duck's position in the simulation**, not just asking it if it
  was OK (table above).

## The simulated camera

Start the duck with its camera on:

```sh
scripts/duck-sim down
DUCK_SIM_CAMERAS=a scripts/duck-sim     # "duck-a can see — console at http://127.0.0.1:8080"
```

Then open **http://127.0.0.1:8080** in a browser: the same console page a real robot serves, with
the duck's camera view. Checked 2026-11-03: capturing at 32 fps (target 30), console page loads,
and a frame grabbed from the camera socket shows the floor in front of the duck
(`images/duck-eye-2026-11-03.png`).

GStreamer prints a screen of warnings (Python bindings, GTK 3 and GTK 4 both present). They are
about pieces the duck doesn't use and can be ignored.

## microduck-lab: training on the Mac

A community project (`jonathanhawkins/microduck-lab`), not Pollen's. It trains walking policies on the
Mac's CPU with 32 simulated ducks instead of thousands on a GPU. It's for trying out reward ideas, not
for producing a policy for the real robot. Its setup put **its own pinned copies** of Pollen's
`microduck` and `microduck_rl` inside `~/microduck-lab`, separate from mine.

From `~/microduck-lab/microduck_local`:

```sh
uv run train-walk --envs 32 --steps 3_000_000 --run-name first-gait   # train
uv run eval-walk runs/first-gait/policy.onnx                          # test it
uv run duck-lab --world pitch          # the simulated room; then, in ../duck-viewer: npm run dev
```

**My first training run (2026-11-03):** 3 million steps took **9 minutes** (the camera install was
running at the same time). It learned to **stand**, rock-steady, but **not to walk**: 0 falls in the
lab's test battery, yet 0.00 m moved when asked to walk. The whole story, with video:
[`TRAINING.md`](TRAINING.md). The policy is in `~/microduck-lab/microduck_local/runs/first-gait/policy.onnx`.

Setup ran its self-tests: 56 passed, 1 skipped. A `libc++abi … recursive_mutex` crash message
appeared as the test program exited, after the results; it didn't affect anything.

## Readable HTML versions of these notes

Every `.md` in `leland/` (and `CLAUDE.local.md`) has a dark-theme `.html` twin beside it. Open the
`.html` in a browser. They're regenerated by `node leland/tools/md-render-sibling.mjs --auto` (a
Claude Code hook runs it after every edit). Ported from keller-portal; needs `npm install` once in
`leland/tools` (`marked`, ~1 MB).

## Not installed

Not needed on a Mac at all: Docker, CUDA, git-lfs, multi-duck `boot` mode (Linux only).

## Removing it all

```sh
scripts/duck-sim down
rm -rf ~/.cache/duck-sim ~/Pollen/microduck_rl ~/microduck-lab ~/.cache/uv ~/.local/share/uv ~/microduck/target
rustup self uninstall          # removes ~/.rustup, ~/.cargo and the shell lines
brew uninstall uv gstreamer libnice-gstreamer && brew autoremove   # autoremove: the ~60 dependencies
```
