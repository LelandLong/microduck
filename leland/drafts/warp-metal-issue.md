# Draft: GitHub issue for DavidDobas/microduck_rl (not posted, waiting for Leland's OK)

**Where:** https://github.com/DavidDobas/microduck_rl/issues/new (his Microduck `metal` branch).
**Title:** Microduck on M4 Max: ~90% of an RTX 3060, and it walks (+ a lockfile fix)

---

Hi David, thanks for warp-metal and the Microduck `metal` branch. I've pre-ordered a Microduck and tried your
branch on two Macs, with a Windows/WSL2 RTX 3060 running Pollen's `develop` as a reference. Results below, plus
one install problem with a one-line fix.

**1. Install: the locked MuJoCo nightly is gone**

`uv sync` on a fresh clone (`71fb768`) fails with a 404 for
`mujoco-3.11.1.dev965888812` from `py.mujoco.org`. That index now only keeps newer nightlies (≥ 3.12.1),
and `uv lock --upgrade-package mujoco` can't resolve, because mjlab 1.6.0 needs `mujoco>=3.11.0,<3.12`.
Pinning the 3.11.0 release from PyPI works for me:

```toml
[tool.uv]
override-dependencies = [
    "mujoco==3.11.0",
    ...
]
```

After `uv lock && uv sync`, both Macs show `metal:0` and `warp_metal.status()` → `(True, 'active')`.
I don't know if `mujoco_warp@metal-3.11` relied on anything specific to that nightly. Everything below ran on 3.11.0.

**2. Speed:** `Mjlab-Velocity-Flat-MicroDuck`, 4,096 envs, `MJLAB_AGENT_DEVICE=mps`

| Machine | Stack | s / iteration |
|---|---|---|
| RTX 3060 12 GB (WSL2, Ubuntu 24.04) | Pollen `develop` `bae39f59` (mjlab 1.3, CUDA) | 3.36–3.66 |
| **Mac Studio M4 Max (32-core GPU, 36 GB)** | your `metal` branch | **3.86–4.05** |
| MacBook Pro M1 Pro (16-core GPU, 32 GB) | your `metal` branch | 13.5–14.7 |

macOS 26.6. Not perfectly like-for-like (mjlab 1.3 vs 1.6).

**3. It learns to walk.** 750 iterations on the M4 Max (48 min) vs the 3060 (43 min). Episode length follows the
same curve (round 150: 840 vs 865 steps; round 750: 924 vs 961). Both exported ONNX policies walk at
0.15/0.3/0.5 m/s without falling in an independent CPU MuJoCo harness (microduck-lab): M4 Max policy 0.53/1.32/2.12 m
in 8 s, 3060 policy 0.78/1.16/2.46 m.

Happy to run anything else that would help (a fixed-seed comparison, a longer run, the full robot stack in
Pollen's `duck-sim`), or to send a PR rebasing the branch onto Pollen's current `develop` (30 commits ahead).

Thanks again!
— Leland
