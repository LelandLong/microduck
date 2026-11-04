# Film a crowd of ducks (all trained in parallel) at several training stages; tile the stages with captions.
import sys
from dataclasses import asdict
from pathlib import Path
import numpy as np, torch, imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFont
import mjlab_microduck.tasks  # noqa
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.viewer.viewer_config import ViewerConfig
TASK = sys.argv[1]; run = Path(sys.argv[2]); out = Path(sys.argv[3]); stages = sys.argv[4:]   # "model_N.pt=Caption"
N = int(__import__("os").environ.get("CROWD", 64)); SEED = 3; W, H = 640, 400; SECONDS = float(__import__("os").environ.get("SECONDS", 8))
font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22); small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
tracks = []
for st in stages:
    ck, title = st.split("=", 1)
    c = load_env_cfg(TASK, play=True); c.scene.num_envs = N; c.seed = SEED; c.scene.env_spacing = 0.45
    v = c.viewer; v.origin_type = ViewerConfig.OriginType.WORLD; v.lookat = (0.6, 0.0, 0.0); v.distance = 4.6
    v.elevation = -32.0; v.azimuth = 150.0; v.max_extra_envs = N - 1; v.width = W; v.height = H; v.enable_reflections = False
    env = ManagerBasedRlEnv(cfg=c, device="cpu", render_mode="rgb_array"); agent = load_rl_cfg(TASK)
    venv = RslRlVecEnvWrapper(env, clip_actions=agent.clip_actions)
    r = load_runner_cls(TASK)(venv, asdict(agent), device="cpu")
    if ck != "zero":
        r.load(str(run / ck), load_cfg={"actor": True}, strict=True, map_location="cpu")
    pol = r.get_inference_policy(device="cpu"); obs = venv.get_observations(); frames = []
    zero = ck == "zero"
    with torch.inference_mode():
        for i in range(int(SECONDS / env.step_dt)):
            a = pol(obs); obs, *_ = venv.step(a * 0 if zero else a)
            if i % 2 == 0:
                img = Image.fromarray(env.render()); d = ImageDraw.Draw(img)
                d.rectangle([0, 0, W, 34], fill=(13, 17, 23)); d.text((10, 6), title, font=font, fill=(230, 237, 243))
                d.text((W - 150, 9), f"{N} ducks · {(i+1)*env.step_dt:3.1f} s", font=small, fill=(139, 148, 158))
                frames.append(np.asarray(img))
    print(title, "done", flush=True); tracks.append(frames); env.close()
cols = 2 if len(tracks) > 1 else 1
grid = []
for fr in zip(*tracks):
    rows = [np.hstack(fr[i:i + cols]) for i in range(0, len(fr), cols)]
    grid.append(np.vstack(rows))
with imageio.get_writer(out, fps=25, macro_block_size=None, quality=7) as w:
    for g in grid: w.append_data(g)
imageio.imwrite(str(out).replace(".mp4", ".png"), grid[len(grid) // 2]); print("wrote", out)
