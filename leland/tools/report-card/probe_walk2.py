import sys
from microduck_local.render_rollout import load_driver
from microduck_local.train import env_class
cls = env_class("microduck", "walk")
for spec in sys.argv[1:]:
    for vx in (0.15, 0.3, 0.5):
        env = cls(max_episode_s=8, command_resample_s=1e9, domain_rand=False, obs_noise=False, random_yaw=False, seed=1)
        drv = load_driver(spec); obs, _ = env.reset(seed=1)
        x0 = float(env.data.xpos[env.trunk_body_id][0]); fell = None
        for step in range(400):
            env.twist_cmd[:] = [vx, 0, 0]
            obs, _, term, _, _ = env.step(drv.fn(obs, env))
            if term: fell = step * 0.02; break
        x = float(env.data.xpos[env.trunk_body_id][0]) - x0; y = float(env.data.xpos[env.trunk_body_id][1]); import math; q = env.data.xquat[env.trunk_body_id]; yaw = math.degrees(math.atan2(2*(q[0]*q[3]+q[1]*q[2]), 1-2*(q[2]**2+q[3]**2)))
        print(f"{spec.split('/')[-2] if '/' in spec else spec:>22} vx={vx}: forward {x:+.2f} m, sideways {y:+.2f} m, facing {yaw:+.0f} deg{'  FELL at %.1fs' % fell if fell else ''}  obs twist={list(round(float(v),2) for v in obs[48:51])}")
