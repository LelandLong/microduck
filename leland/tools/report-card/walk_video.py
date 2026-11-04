# Film one episode per training stage, tiled side by side with captions.
import sys, numpy as np
from pathlib import Path
import imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFont
from microduck_local.render_rollout import load_driver, make_camera, offscreen_renderer, LOOKAT_Z
from microduck_local.train import env_class
from microduck_local import contract as C  # noqa
out = Path(sys.argv[1]); P = Path.home()/'microduck/leland/policies'
CTRL_DT = 0.02; SECONDS = 8.0; VX = 0.3; W, H = 480, 360; STRIDE = 2   # 25 fps
stages = []
for vx in (0.3, 0.5):
    stages += [(str(P/"pc-first-750.onnx"), f"750 rounds · {vx} m/s", "43 min on the PC", vx),
               (str(P/"pc-walk-4000.onnx"), f"4,000 rounds · {vx} m/s", "3 h 55 min on the PC", vx),
               (str(Path.home()/"microduck-lab/microduck/policies/alpha_walking.onnx"), f"Pollen's walker · {vx} m/s", "official, for comparison", vx)]
try: font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22); small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 17)
except Exception: font = small = ImageFont.load_default()
cls = env_class("microduck", "walk"); tracks = []
for spec, title, sub, VX in stages:
    env = cls(max_episode_s=SECONDS, command_resample_s=1e9, domain_rand=False, obs_noise=False, random_yaw=False, seed=1)
    drv = load_driver(spec); cam = make_camera("three-quarter", 0.9); r = offscreen_renderer(env.model, W, H)
    obs, _ = env.reset(seed=1); env.twist_cmd[:] = [VX, 0.0, 0.0]
    frames = []; fell_at = None; x0 = float(env.data.xpos[env.trunk_body_id][0]); step = 0; done = False
    n = int(SECONDS / CTRL_DT)
    while step < n:
        if not done:
            env.twist_cmd[:] = [VX, 0.0, 0.0]
            obs, _, term, trunc, _ = env.step(drv.fn(obs, env)); step += 1
            if term: done = True; fell_at = step * CTRL_DT
        else: step += 1
        if step % STRIDE == 0:
            cam.lookat[:] = (float(env.data.xpos[env.trunk_body_id][0]), float(env.data.xpos[env.trunk_body_id][1]), LOOKAT_Z)
            r.update_scene(env.data, camera=cam); img = Image.fromarray(r.render().copy()); d = ImageDraw.Draw(img)
            d.rectangle([0, 0, W, 58], fill=(13, 17, 23)); d.text((12, 6), title, font=font, fill=(230, 237, 243)); d.text((12, 33), sub, font=small, fill=(139, 148, 158))
            dist = float(env.data.xpos[env.trunk_body_id][0]) - x0
            status = f"FELL at {fell_at:.1f} s" if fell_at else f"{step*CTRL_DT:4.1f} s · walked {dist:+.2f} m"
            d.rectangle([0, H - 32, W, H], fill=(13, 17, 23)); d.text((12, H - 27), status, font=small, fill=(248, 81, 73) if fell_at else (63, 185, 80))
            frames.append(np.asarray(img))
    r.close(); tracks.append(frames)
    print(f"{title}: {spec.split('/')[-1]} {'fell at %.1f s' % fell_at if fell_at else 'stayed up 8 s'}, moved {dist:+.2f} m")
grid = []
for i in range(len(tracks[0])):
    tiles = [t[i] for t in tracks]
    grid.append(np.vstack([np.hstack(tiles[0:3]), np.hstack(tiles[3:6])]))
out.parent.mkdir(parents=True, exist_ok=True)
with imageio.get_writer(out, fps=1 / (CTRL_DT * STRIDE), macro_block_size=None, quality=7) as w:
    for g in grid: w.append_data(g)
print("wrote", out, out.stat().st_size // 1024, "KB")
