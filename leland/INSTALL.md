# What's installed on my Mac for the Microduck

Installed 2026-11-03 on my MacBook Pro (Apple Silicon, macOS 26.6.2). **About 6 GB in total.** Finder's
available space went from 69.4 GB to 64.1 GB.

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

Nothing went into system folders. Everything except `uv` is inside my home folder.

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

## Not installed (yet)

- **Simulated camera**: `brew install gstreamer libnice-gstreamer`, ~1.5–2.5 GB, 58 Homebrew packages.
- **microduck-lab** (training experiments on the Mac, no NVIDIA GPU): ~3 GB.
- Not needed on a Mac at all: Docker, CUDA, git-lfs, multi-duck `boot` mode (Linux only).

## Removing it all

```sh
scripts/duck-sim down
rm -rf ~/.cache/duck-sim ~/Pollen/microduck_rl ~/.cache/uv ~/.local/share/uv ~/microduck/target
rustup self uninstall          # removes ~/.rustup, ~/.cargo and the shell lines
brew uninstall uv
```
