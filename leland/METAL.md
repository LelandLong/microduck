# Training the Microduck on Apple GPUs: my first open-source project

Started 2026-11-03. **Goal:** make Pollen's real Microduck training run well on Apple Silicon Macs, by joining and
helping an existing community effort. **Claude does the engineering; I'm the maintainer:** I decide, review,
and put my name on what goes out.

## Why this is hard (the short version)

Pollen's training runs **4,096 ducks at once on an NVIDIA graphics card**. Everything in it already runs on a
Mac except the physics engine, which is written in NVIDIA's own GPU language:

| Layer | What it does | On Apple's GPU? |
|---|---|---|
| PyTorch | the duck's brain and the learning maths | ✅ yes (Apple's "MPS") |
| rsl_rl | the PPO learning loop | ✅ yes (plain PyTorch) |
| mjlab | the duck's world: rewards, curriculum, randomisation | ⚠️ needs small changes |
| MuJoCo Warp | the physics, thousands of ducks in parallel | ❌ NVIDIA only (written in **Warp** → CUDA) |

A full rewrite would be months of expert GPU work. **But someone has already started.**

## What already exists (found 2026-11-03)

- **[`warp-metal`](https://github.com/innate-inc/warp-metal)** by David Dobas (innate-inc), Apache-2.0, started
  September 2026. It adds an Apple GPU device (`metal:0`) to NVIDIA's Warp, so Warp's GPU code compiles to Apple's
  **Metal** instead of CUDA. Install: `pip install warp-metal` next to `warp-lang` 1.17.0. Needs macOS 15+.
- With **two small patches** to MuJoCo Warp and mjlab (his forks, branches `metal-3.11` and `metal`, PRs open),
  Pollen's framework runs on it.
- **[`DavidDobas/microduck_rl`](https://github.com/DavidDobas/microduck_rl/tree/metal), branch `metal`: the
  Microduck on a Mac.** Just 4 files changed. It also moves from mjlab 1.3.0 (what Pollen uses) to mjlab 1.6.0,
  so results aren't a pure like-for-like comparison with Pollen's.
- **His speed figure:** a humanoid robot (Unitree G1) with 1,024 environments takes about 1.0 s per learning round
  on an M5 Pro, against 0.3 s on an RTX 5090. Apple falls further behind with more environments (GPU threadgroup memory).
- **Known limits:** Apple GPUs have no 64-bit floating point; some atomic operations aren't truly atomic; Apple's
  compiler can miscompile big unrolled matrix maths.
- **Hardly anyone has noticed it yet** (1 star when I found it). Other attempts are narrower: MJX on `jax-metal`
  (reported broken), MLX ports ([RobotFlow-Labs](https://github.com/RobotFlow-Labs/Mujoco-mlx),
  [lucidrains](https://github.com/lucidrains/mujoco_warp)).

## The plan: what I can contribute, in order

1. **Install it on my two Macs** and run the same test as the PC. *(done 2026-11-03, see log)*
2. **Measure:** M4 Max (Studio) and M1 Pro (laptop) against the RTX 3060 on the Microduck, same settings.
3. **Check correctness:** train to 750 rounds on the Studio and put the result through the same walking test as the
   PC duck (which walked 2.46 m in 8 s at 0.5 m/s). GPU bugs can be silent, and the PC is my trusted reference.
4. **Report back** to David: what worked, what broke, the numbers. As a GitHub issue on his repo, friendly and
   specific.
5. **Bring his Microduck branch up to date** with Pollen's latest `develop` (it's 30 commits behind), as a pull
   request to him.
6. Later, if it holds up: help get the patches merged upstream, and **suggest to Pollen** an official "train on a
   Mac" option.

## Roles

- **Me (Leland):** decide what we do and publish; read the write-ups; post or approve anything public (issues,
  pull requests, comments) under my GitHub name; be patient and polite with maintainers.
- **Claude:** installs, tests, measures, writes code and fixes, drafts issues and pull requests for me to approve,
  and explains every result in these notes.
- **Which Claude:** Claude **Opus 5.5** for most of it (installing, testing, measuring, branch updates, write-ups).
  Claude **Fable 5.1**, Anthropic's most capable model, for the hardest parts: misbehaving GPU code, subtle numeric
  differences, design decisions. Switch with `/model` in Claude Code. (There's no "Fable 5.5"; 5.1 is current.)

## Honest caveats

- **Checking is the bottleneck, not writing code.** A GPU bug can let the duck train while learning slightly wrong
  physics. Every result gets checked against the PC.
- **Upstream may never merge it.** NVIDIA and Google don't have to accept Metal support. A well-kept fork that
  people use is still valuable.
- **Usage:** months of heavy work with Claude uses a lot of my plan's allowance, Fable especially.

## GitHub stars, explained

A **star** is GitHub's bookmark-plus-thank-you: it saves the project to my starred list and tells the author (and
everyone) that people value it. It costs nothing and is the friendliest first contact in open source. **Starred
2026-11-03:** `innate-inc/warp-metal` (it went from 1 to 2 stars) and `DavidDobas/microduck_rl`.

## Log

### 2026-11-03: installed on both Macs

- Cloned `DavidDobas/microduck_rl` branch `metal` (commit `71fb768`) to `~/Pollen/microduck_rl-metal` on the
  Studio and the laptop, beside Pollen's original (`~/Pollen/microduck_rl`, untouched).
- **Snag (worth reporting to David):** `uv sync` failed. The lock file pins a **MuJoCo nightly**,
  `3.11.1.dev965888812`, from `py.mujoco.org`, and that server only keeps recent nightlies (now ≥ 3.12.1), so the
  download returns 404. Re-locking fails too, because mjlab 1.6.0 needs `mujoco >=3.11.0,<3.12`.
  **Fix (local, one line):** pin the **3.11.0 release from PyPI** in `[tool.uv] override-dependencies`:
  `"mujoco==3.11.0"`. Then `uv lock` + `uv sync` work. To be confirmed: whether MuJoCo Warp's `metal-3.11` branch
  needed anything from that nightly.
- **Result:** Warp sees the GPU on both Macs: `metal:0 "Apple M4 Max"` (Studio) and `metal:0 "Apple M1 Pro"`
  (laptop). `warp_metal.status()` → active. PyTorch MPS available. `.venv` 1.1 GB.
- Test command (same as the PC's, plus the Mac device):
  `MJLAB_AGENT_DEVICE=mps WANDB_MODE=disabled uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 4096 --agent.max-iterations 50`

### 2026-11-03 19:15: first test, Studio vs PC

Same 50-round test as the PC (4,096 ducks, Microduck flat-ground walking task):

| Machine | Software | Seconds per learning round | Ducks' average time up at round ~50 |
|---|---|---|---|
| Gaming PC, RTX 3060 | Pollen's original (mjlab 1.3, CUDA) | 3.66 (test), 3.36 (750-round run) | 2.7 s |
| **Mac Studio, M4 Max GPU** (32 cores) | **warp-metal** (mjlab 1.6, Metal) | **3.86–4.05, median 4.01** | **2.6 s** |
| Laptop, M1 Pro GPU (16 cores) | warp-metal (mjlab 1.6, Metal) | 13.5–14.7, median 13.7 | 3.2 s |

**The Studio's Apple GPU trains the Microduck at about 90% of the RTX 3060's speed**, and learning looks the same so
far. Caveat: different mjlab versions (1.3 vs 1.6), so it's close but not perfectly like-for-like.
Whole 50-round test: 5 min 9 s including start-up.

**The laptop's 2021 M1 Pro works too, but is 3.4× slower than the Studio** (750 rounds would take ~2.9 h, against
~50 min on the Studio and ~43 min on the PC). Whole test: 14 min 27 s.

**Next (running):** 750 rounds on the Studio (`--agent.run-name metal-750`, started 19:21, log `~/metal-750.log`),
then the walking test, compared with the PC duck. And the same 50-round test on the laptop's M1 Pro.

### 2026-11-03 20:10: the Studio-trained duck walks

750 rounds on the Studio's Apple GPU: **48 min 1 s** (PC: 43 min 28 s). Results copied to the laptop
(`~/microduck-runs/studio/`); the brain is [`policies/studio-metal-750.onnx`](policies/studio-metal-750.onnx).

**How long ducks stayed up during training** (average, in seconds; an attempt ends at a fall or 20 s):

| Round | PC (RTX 3060, CUDA) | **Studio (M4 Max, Metal)** |
|---|---|---|
| 1 | 0.5 | 0.5 |
| 50 | 2.7 | 3.0 |
| 150 | 17.3 | 16.8 |
| 300 | 18.7 | 18.2 |
| 500 | 18.6 | 19.2 |
| 750 | 19.2 | 18.5 |

**Walking test** (same harness as TRAINING.md section 12: microduck-lab's simulator, 8 s, walk forward):

| Speed asked for | PC duck | **Studio duck** |
|---|---|---|
| 0.15 m/s | 0.78 m | **0.53 m** |
| 0.30 m/s | 1.16 m | **1.32 m** |
| 0.50 m/s | 2.46 m | **2.12 m** |

**Both walk at every speed, neither falls, and they're in the same range.** Two separately trained ducks always
differ somewhat (different random starts), so this is the expected kind of difference, not a sign that Metal's
physics is wrong. That's the most important result so far: **the Apple GPU trains a duck that walks, at about
90% of the RTX 3060's speed.**

Not yet checked: the same duck in the full duck simulator (`scripts/duck-sim`), and a like-for-like run (same mjlab
version, same random seed) to separate "Metal" from "newer mjlab".

**Posted 2026-11-03 ~20:20, with my OK: [innate-inc/warp-metal#10](https://github.com/innate-inc/warp-metal/issues/10)**,
my first open-source contribution. (Issues are off on his `microduck_rl` fork, so it went to warp-metal, with one
line explaining that.) Text: [`drafts/warp-metal-issue.md`](drafts/warp-metal-issue.md). Watch for his reply.
