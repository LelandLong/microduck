# Draft: follow-up comment on innate-inc/warp-metal#10 (POSTED 2026-11-04: https://github.com/innate-inc/warp-metal/issues/10#issuecomment-6634458130)

---

A follow-up, and a bug that I don't think is Metal's fault.

**Stand-up on Metal.** I trained `Mjlab-StandUp-Flat-MicroDuck` for 750 iterations on the M4 Max (48 min, about
3.8 s/iteration). When I filmed it, the ducks that failed to stand had sunk through the floor. I counted the robot
geoms that can collide with the terrain in the compiled model:

| Model | Pollen's `develop` (mjlab 1.3.0) | your `metal` branch (mjlab 1.6.0) |
|---|---|---|
| `robot_walk.xml` (velocity) | 2 (feet) | 2 (feet) |
| `robot_groundcontact.xml` (standup, sitstand, ground pick, roulade, rollers) | **10** (trunk, hips, legs, jaw, feet) | **2** (feet only) |

The cause seems to be the mjlab upgrade, not warp-metal. The body-contact geoms in `robot_groundcontact.xml` have no
names. Both versions apply `FULL_COLLISION` (`.*_collision`) with `disable_other_geoms=True`, but:
- mjlab 1.3 disabled the non-matching geoms by name, so the unnamed ones accidentally kept their contacts;
- mjlab 1.6 iterates over the geom objects, so they're now (correctly) disabled.

Your `contype=1, conaffinity=1` change keeps the named feet colliding, but not the unnamed body parts.

Velocity/walking is unaffected, and I confirmed my earlier walking result stands. Possible fixes: name those geoms
so they match `.*_collision`, or set `disable_other_geoms=False` on the ground-contact robot's `CollisionCfg`. I'm
happy to open a PR for whichever you prefer.

**Walking, longer run, for reference:** on the RTX 3060 I resumed the 750-iteration run to 4,000 (about 3 h 10 min
more). It now walks straight; the 750-iteration policy curved about 70° over 8 s, which I'd missed by only measuring
forward distance.
