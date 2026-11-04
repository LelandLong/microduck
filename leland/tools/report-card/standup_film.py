# Film the same sitting ducks (fixed seed) with several checkpoints, close-up; tile with captions.
import sys
from dataclasses import asdict
from pathlib import Path
import numpy as np, torch, imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFont
import mjlab_microduck.tasks  # noqa
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
TASK = "Mjlab-StandUp-Flat-MicroDuck"; N = 64; SEED = 7; W, H = 400, 320
run = Path(sys.argv[1]); out = Path(sys.argv[2]); cks = sys.argv[3:]
font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20); small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
def make(idx, render):
    c = load_env_cfg(TASK, play=True); c.scene.num_envs = N; c.seed = SEED
    c.viewer.env_idx = idx; c.viewer.max_extra_envs = 0; c.viewer.distance = 0.55; c.viewer.elevation = -12.0
    c.viewer.azimuth = 135.0; c.viewer.width = W; c.viewer.height = H
    return c, ManagerBasedRlEnv(cfg=c, device="cpu", render_mode="rgb_array" if render else None)
c, env = make(0, False); RslRlVecEnvWrapper(env, clip_actions=load_rl_cfg(TASK).clip_actions); z0 = env.scene["robot"].data.root_link_pos_w[:, 2].cpu().numpy().copy(); env.close()
deep = [int(i) for i in np.where(z0 < 0.075)[0][:2]]
print("deep-sit ducks", deep, z0[deep], flush=True)
rows = []
for idx in deep:
    tiles = []
    for ck in cks:
        c, env = make(idx, True); agent = load_rl_cfg(TASK)
        venv = RslRlVecEnvWrapper(env, clip_actions=agent.clip_actions)
        r = load_runner_cls(TASK)(venv, asdict(agent), device="cpu")
        r.load(str(run / ck), load_cfg={"actor": True}, strict=True, map_location="cpu"); pol = r.get_inference_policy(device="cpu")
        obs = venv.get_observations(); rob = env.scene["robot"]; frames = []
        print(ck, "duck", idx, "start z %.3f" % float(rob.data.root_link_pos_w[idx, 2]), flush=True)
        n = int(c.episode_length_s / env.step_dt) - 2
        with torch.inference_mode():
            for i in range(n):
                obs, *_ = venv.step(pol(obs))
                if i % 2 == 0:
                    z = float(rob.data.root_link_pos_w[idx, 2]); img = Image.fromarray(env.render()); d = ImageDraw.Draw(img)
                    rounds = int(ck.split("_")[1].split(".")[0]); title = "Before training" if rounds == 0 else f"After {rounds + (1 if rounds == 749 else 0)} rounds"
                    d.rectangle([0, 0, W, 34], fill=(13, 17, 23)); d.text((10, 7), title, font=font, fill=(230, 237, 243))
                    up = z > 0.105
                    d.rectangle([0, H - 28, W, H], fill=(13, 17, 23))
                    d.text((10, H - 24), f"{(i+1)*env.step_dt:4.1f} s · " + ("STANDING" if up else "not up"), font=small, fill=(63, 185, 80) if up else (139, 148, 158))
                    frames.append(np.asarray(img))
        print("  end z %.3f" % float(rob.data.root_link_pos_w[idx, 2]), flush=True)
        tiles.append(frames); env.close()
    rows.append([np.hstack(f) for f in zip(*tiles)])
grid = [np.vstack(fr) for fr in zip(*rows)]
with imageio.get_writer(out, fps=25, macro_block_size=None, quality=7) as w:
    for _ in range(12): w.append_data(grid[0])
    for g in grid: w.append_data(g)
    for _ in range(25): w.append_data(grid[-1])
imageio.imwrite(str(out).replace(".mp4", ".png"), grid[-1])
print("wrote", out)
