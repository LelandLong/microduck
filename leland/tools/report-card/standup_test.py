# Stand-up report card: start N ducks sitting, run each checkpoint for 6 s, measure trunk height; film duck 0.
import sys, os
from dataclasses import asdict
from pathlib import Path
import numpy as np, torch, imageio.v2 as imageio
import mjlab_microduck.tasks  # noqa: registers tasks
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
TASK = "Mjlab-StandUp-Flat-MicroDuck"
run = Path(sys.argv[1]); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
N = 64; device = os.environ.get("MJLAB_SIM_DEVICE", "metal:0"); agent_dev = os.environ.get("MJLAB_AGENT_DEVICE", "cpu")
for ck in sys.argv[3:]:
    env_cfg = load_env_cfg(TASK, play=True); env_cfg.scene.num_envs = N
    agent_cfg = load_rl_cfg(TASK)
    env = ManagerBasedRlEnv(cfg=env_cfg, device=device, render_mode="rgb_array")
    venv = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
    runner = load_runner_cls(TASK)(venv, asdict(agent_cfg), device=agent_dev)
    runner.load(str(run / ck), load_cfg={"actor": True}, strict=True, map_location=agent_dev)
    policy = runner.get_inference_policy(device=agent_dev)
    obs = venv.get_observations(); robot = env.scene["robot"]
    z = lambda: robot.data.root_link_pos_w[:, 2].detach().cpu().numpy().copy()
    z0 = z(); zs = [z0]; frames = []
    steps = int(env_cfg.episode_length_s / env.step_dt) - 2
    with torch.inference_mode():
        for i in range(steps):
            obs, _, _, _ = venv.step(policy(obs))
            zs.append(z())
            if i % 2 == 0: frames.append(env.render())
    zs = np.array(zs); zend = zs[-1]
    up = (zend > 0.105).mean(); tumbled = (zs.min(0) < 0.04).mean()
    print(f"{ck}: start z {z0.mean():.3f} m, end z {zend.mean():.3f} m (median {np.median(zend):.3f}), "
          f"stood up (z>0.105): {up*100:.0f}% of {N}, dropped below 4 cm: {tumbled*100:.0f}%", flush=True)
    np.save(out / f"{Path(ck).stem}_z.npy", zs)
    with imageio.get_writer(out / f"{Path(ck).stem}.mp4", fps=round(1 / (2 * env.step_dt)), macro_block_size=None) as w:
        for f in frames: w.append_data(f)
    env.close()
