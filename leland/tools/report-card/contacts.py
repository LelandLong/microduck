# Which robot geoms can touch the floor in the compiled stand-up model?
import mujoco
import mjlab_microduck.tasks  # noqa
from mjlab.tasks.registry import load_env_cfg
from mjlab.scene import Scene
c = load_env_cfg("Mjlab-StandUp-Flat-MicroDuck", play=True); c.scene.num_envs = 1
m = Scene(c.scene, device="cpu").compile() if hasattr(Scene, "compile") else None
if m is None:
    from mjlab.envs import ManagerBasedRlEnv
    m = ManagerBasedRlEnv(cfg=c, device="cpu").sim.mj_model
names=[(mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or "#%d(%s)"%(g,mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[g])), int(m.geom_contype[g]), int(m.geom_conaffinity[g])) for g in range(m.ngeom)]
floorlike=[n for n in names if (n[1]&1) or (n[2]&1)]
print(m.ngeom,"geoms;", len(floorlike), "with contact bit 1:", floorlike)
