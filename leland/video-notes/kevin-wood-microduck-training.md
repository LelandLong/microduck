# Kevin Wood: Microduck, getting started training a walking policy with mjlab

[Video](https://youtu.be/ZDvCdIFXANw) (8:20). Watched 2026-10-30. These are my notes, not the
transcript; timestamps link into the video.

## The steps
1. Clone **`pollen-robotics/microduck_rl`**, the training repo, not `microduck`
   ([0:35](https://youtu.be/ZDvCdIFXANw?t=35)).
2. `uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 4096`
3. **On native Windows this fails** with "selected GPUs index out of range"
   ([1:15](https://youtu.be/ZDvCdIFXANw?t=75)). Fix: use **WSL2**. In PowerShell run `wsl --install`,
   pick an Ubuntu version, then repeat steps 1–2 inside WSL ([1:39](https://youtu.be/ZDvCdIFXANw?t=99)).
4. The first `uv run` builds two packages: microduck itself and **BAM** (Better Actuator Models).
5. It then offers a Weights & Biases account for charts. **Option 3 = skip** ([4:53](https://youtu.be/ZDvCdIFXANw?t=293)).
6. Training starts: 50,000 iterations by default, about 3.8 s each on his machine
   ([5:35](https://youtu.be/ZDvCdIFXANw?t=335)).
7. A checkpoint (`model_N.pt`) is saved every 250 iterations under `logs/rsl_rl/...`. You can watch
   one while training continues ([6:50](https://youtu.be/ZDvCdIFXANw?t=410)):
   `uv run play <task> --checkpoint-file logs/rsl_rl/<task>/<date>/model_750.pt`

## Things worth remembering
- **You don't need 50,000 iterations.** It walks after **750** (~48 min at his speed) and walks with
  clear purpose after **4,000** (~4 h). The full default would be ~53 h. Change it with
  `--agent.max_iterations`; in the code it's written `50_000`, Python's way of writing 50,000.
- **The sim-to-real gap** is the difference between how the duck behaves in simulation and in real
  life. Pollen narrows it with **system identification**: they measured the real Dynamixel servos
  and built a matching model (BAM). Friction is usually what separates a policy that works on the
  real robot from one that doesn't.
- **mjlab** is the training framework, an Isaac Lab-style framework on **MuJoCo Warp**
  (GPU-accelerated MuJoCo), which is why training needs an NVIDIA GPU.

## What it means for my setup
- Confirms the plan for my gaming PC (RTX 3060): **WSL2, not native Windows.**
- Cost check for cloud training: 4,000 iterations at a speed like his ≈ 4 h ≈ **$3.20** on Hugging
  Face's L4 ($0.80/h). Not yet measured on any GPU I'd use.
