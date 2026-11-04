# Fly-over: a crowd of ducks with one brain, the camera slowly circling down from high above to one duck.
import os, sys, math
from dataclasses import asdict
from pathlib import Path
import numpy as np, torch, imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFont
import mjlab_microduck.tasks  # noqa
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.viewer.viewer_config import ViewerConfig
TASK, run, ck, out, title = sys.argv[1], Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4]), sys.argv[5]
N = int(os.environ.get("CROWD", 128)); SECONDS = float(os.environ.get("SECONDS", 24)); W, H = 1280, 720
font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30); small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
c = load_env_cfg(TASK, play=True); c.scene.num_envs = N; c.seed = 3; c.scene.env_spacing = 0.45
v = c.viewer; v.origin_type = ViewerConfig.OriginType.WORLD; v.distance = 8.0; v.max_extra_envs = N - 1
v.width = W; v.height = H; v.enable_reflections = False
env = ManagerBasedRlEnv(cfg=c, device="cpu", render_mode="rgb_array"); agent = load_rl_cfg(TASK)
venv = RslRlVecEnvWrapper(env, clip_actions=agent.clip_actions)
r = load_runner_cls(TASK)(venv, asdict(agent), device="cpu")
r.load(str(run / ck), load_cfg={"actor": True}, strict=True, map_location="cpu"); pol = r.get_inference_policy(device="cpu")
obs = venv.get_observations(); rob = env.scene["robot"]
pos = lambda: rob.data.root_link_pos_w.detach().cpu().numpy()
p0 = pos(); centre = p0.mean(0); star = int(np.argmin(np.linalg.norm(p0[:, :2] - centre[:2], axis=1)))
ease = lambda t: t * t * (3 - 2 * t)
n = int(SECONDS / env.step_dt); frames = 0
with imageio.get_writer(out, fps=25, macro_block_size=None, quality=8) as w, torch.inference_mode():
    for i in range(n):
        obs, *_ = venv.step(pol(obs))
        if i % 2: continue
        t = i / (n - 1); e = ease(t); p = pos()
        cam = env._offline_renderer._cam
        target = (1 - e) * p.mean(0) + e * p[star]
        cam.lookat[:] = (target[0], target[1], 0.08 * e)
        cam.distance = 7.5 * (1.1 / 7.5) ** e          # 7.5 m → 1.1 m, steady in perceived speed
        cam.elevation = -60 + 38 * e                    # from high above down to a low angle
        cam.azimuth = 120 + 140 * t                     # one slow partial orbit
        img = Image.fromarray(env.render()); d = ImageDraw.Draw(img)
        a = int(255 * max(0.0, min(1.0, (0.25 - t) / 0.08)))  # title fades out after ~5 s
        if a:
            d.rectangle([0, 0, W, 50], fill=(13, 17, 23)); d.text((18, 9), title, font=font, fill=(230, 237, 243))
        d.text((W - 260, H - 34), f"{N} ducks, one brain · {i*env.step_dt:4.1f} s", font=small, fill=(230, 237, 243))
        w.append_data(np.asarray(img)); frames += 1
        if frames in (2, 300, 590): imageio.imwrite(str(out).replace(".mp4", f"-{frames}.png"), np.asarray(img))
print("wrote", out, frames, "frames, star duck", star)
