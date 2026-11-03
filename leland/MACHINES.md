# My three machines for the Microduck

Set up 2026-11-03. The **laptop** is home base, the **Mac Studio** upstairs is the always-on workhorse,
and the **gaming PC** will be the NVIDIA training box: switched on only when a run needs it.

| | MacBook Pro (laptop) | Mac Studio (upstairs) | Gaming PC (office) |
|---|---|---|---|
| Chip | M1 Pro (2021) | **M4 Max** (2025) | Intel i7-12700F + **NVIDIA RTX 3060** |
| Processor cores | 10 (8 fast, 2 efficient) | **14** (10 fast, 4 efficient) | 12 (20 threads) |
| Memory | 32 GB | 36 GB | 16 GB (+ **12 GB** on the graphics card) |
| Free space | 63 GB (Finder) | 136 GB (Finder) | C: SSD 124 of 453 GB · D: hard drive 887 of 931 GB |
| Network | AT&T Wi-Fi | AT&T, wired | AT&T, wired |
| Name on the network | Leland's MacBook Pro | `CHS-Leland-Mac-Studio-2025.local` | `RERUN_GAMER` |
| Status | ✅ everything installed | ✅ everything installed | ⏳ not set up yet |

**Both Macs must be on the AT&T network** to see each other (not Spectrum).

## What each machine is for

- **Laptop:** where I sit and work with Claude: editing, quick experiments, watching results.
- **Mac Studio:** Mac training runs (2.2× faster than the laptop), long runs while the laptop stays free,
  the simulator on its three screens. Never sleeps.
- **Gaming PC:** **Pollen's official training**, which needs an NVIDIA graphics card. No Mac can do it.
- **Hugging Face Jobs** (rented cloud graphics cards, about $0.80 an hour) when I don't want the PC's heat and noise.

## The training race (2026-11-03)

The same Mac training run on both Macs, at the same time, both machines quiet: 3 million practice steps,
32 simulated ducks, using microduck-lab.

| | Time | Practice steps per second |
|---|---|---|
| **Mac Studio** | **2 min 35 s** | ~19,400 |
| Laptop | 5 min 36 s | ~8,950 |

**The Studio is 2.2× faster.** 16.7 hours of duck practice in under 3 minutes. A 20-million-step run would
take about 17 minutes on the Studio, about 37 on the laptop. (The laptop's earlier 9 minutes was slowed by
an install running at the same time.)

## Mac Studio: how the laptop connects to it

### Using it

```sh
ssh studio                 # a Terminal on the Studio, no password
```

- **See its screens from downstairs:** the **Screen Sharing** app → `CHS-Leland-Mac-Studio-2025.local`.
  (This already worked: Keller's Remote Management includes it.)
- **Watch Claude's work upstairs:** Claude can open Terminal windows and the simulator **on the Studio's
  own screens**, because it logs in as me. Training runs and the simulator are started that way so I can
  watch. (macOS asked once for permission to let it control Terminal; I allowed it.)
- A plain `ssh` command, with no window, runs out of sight. That's normal.

### How it was set up (in case I need to do it again)

1. **On the Studio:** System Settings → General → Sharing → **Remote Login** on, access limited to my
   account (important: the Studio is also on Keller's ZeroTier network). Screen Sharing was already on.
   System Settings → Energy: never sleeps, wakes for network access.
2. **On the laptop:** a `studio` shortcut in `~/.ssh/config` (old copy saved as
   `~/.ssh/config.bak-2026-11-03`):

   ```
   Host studio
     HostName CHS-Leland-Mac-Studio-2025.local
     User lelandlong
     IdentityFile ~/.ssh/id_ed25519
     IdentitiesOnly yes
   ```

   `IdentitiesOnly yes` matters: the laptop's keychain holds 23 keys, and the Studio refuses anyone after 6
   wrong ones. That was the "Too many authentication failures" error.
3. `ssh-copy-id -i ~/.ssh/id_ed25519.pub studio` once, typing the Studio's password. Never needed again.
4. Studio's identity (the laptop warns if it ever changes): ED25519 `SHA256:jO1/OvVIODfO5bDW8yAI0ew6Q1c6/vI+YSxFxF8fnU0`.

### Other Macs that show up on the network

Macs named "SAN …" and "CHS …" (other than mine) are colleagues' machines, seen through **ZeroTier**
(Keller's private network). They are not mine, and nothing here connects to them.

### What's installed on the Studio

The same as the laptop (see [`INSTALL.md`](INSTALL.md)), about 8 GB:

| What | Where | Size |
|---|---|---|
| Homebrew (I ran its installer: it needs my password) | `/opt/homebrew` | 1.4 GB with packages |
| uv, Node, gh, GStreamer + libnice-gstreamer (camera) | via Homebrew | (included above) |
| Rust 1.99.1 | `~/.rustup`, `~/.cargo` | 1.6 GB |
| My fork, `leland` branch (+ `upstream` = Pollen) | `~/microduck` | 2.1 GB built (in **32 s**, laptop: 51 s) |
| Pollen's microduck_rl (`develop`, `bae39f59`) | `~/Pollen/microduck_rl` | 1.1 GB |
| microduck-lab (`8dad921`) | `~/microduck-lab` | 1.8 GB |
| uv's download cache | `~/.cache/uv` | 1.6 GB |

**Checked working:** the simulator stood up (control loop 49.9 of 50 times a second, none missed) and
`drive 0.4 0` walked the duck **1.31 m**, measured from the simulator's own position readings.

The Studio is a **Keller machine**. I'm in Keller IT, with admin rights and permission to install.

## Gaming PC: the plan (being set up)

**Found on the network 2026-11-03:** `rerun-gamer.local`, 192.168.1.194, network card `50:eb:f6:ca:72:a1`
(needed later to wake it remotely). Laptop shortcut: `ssh pc` (user `lelan`, same key as the Studio).

**Step 1, SSH into Windows:** in an **administrator** PowerShell on the PC, run [`pc/setup-ssh.ps1`](pc/setup-ssh.ps1):

```powershell
irm https://raw.githubusercontent.com/LelandLong/microduck/leland/leland/pc/setup-ssh.ps1 | iex
```

It installs Windows' own OpenSSH server, limits it to the home network, trusts only my laptop's key
(fetched from `github.com/LelandLong.keys`) and turns password logins off.

**How it will work:**
- **Switched on from the laptop** (Wake-on-LAN, over the wired home network). Needs two settings checked on
  the PC: one in the BIOS, one on the network adapter.
- **Every training run ends by shutting the PC down.** No idling, so less heat and fan noise in the office.
- Optional: **cap the graphics card's power** (about 170 W → 120 W): much quieter and cooler, perhaps
  10–20% slower.
- Then `ssh pc` from the laptop, just like the Studio.

**Linux on the PC (WSL2):** Linux runs inside Windows as **one big file**, with no partitioning and no
choosing Windows or Linux at startup. It goes on the **second drive** (`wsl --install --location D:\WSL\…`),
grows as needed, and needs about 20–50 GB. Pollen's training doesn't work in plain Windows (Kevin Wood's
video shows it failing) but does in WSL2.

**Keeping it from being used as a bot without me knowing:**
- **Nothing on the internet can reach it.** The AT&T gateway blocks unrequested connections from outside,
  and no port on the router will ever be opened.
- **Only my laptop can log in.** Key only, no passwords, and Windows Firewall allows it only from the home network.
- **No ZeroTier on the PC**, so Keller's network can't reach it.
- **No remote-control apps** (TeamViewer, AnyDesk…). Windows Update and Defender stay on.
- **I can check anytime:** Claude can list everything running and every outside connection.
- **Belt and braces:** the AT&T gateway can block one device's internet (Device Access controls).

**Known from its System Information (2026-11-03):** Windows 11 Home build 26200 (WSL2 works on Home),
NVIDIA driver 596.36 (Pollen's training needs 580+), **"Virtualization-based security: Running"** = the
processor's virtualization is already switched on (WSL2 needs it), UEFI + Secure Boot, Windows user `lelan`.

**Checked 2026-11-03 (Task Manager + This PC):**
- **Graphics card memory: 12.0 GB.** (System Information's "1 MB" was the Windows bug.) Driver now
  32.0.15.9649 = NVIDIA 596.49, dated 2026-05-05.
- **C: is a fast SSD (NVMe), 124 GB free of 453. D: "DATA" is a spinning hard drive (SATA HDD), 887 GB free
  of 931.**
- Decision on where Linux goes: see below.

**Where Linux should go: C: (SSD) or D: (hard drive)?** (open, my call)

| | Linux on **C:** (SSD) | Linux on **D:** (hard drive) |
|---|---|---|
| Space | 124 GB free; Linux takes 20–50 GB | 887 GB free, room for anything |
| Installing (thousands of small files) | minutes | noticeably slower, maybe 5–10× |
| Starting a training run | seconds | slower to load |
| Training itself | same: the graphics card does the work | same |

Recommended: **Linux on C:** for speed, and **old runs, videos and archives on D:**, which Linux can
reach as `/mnt/d`. If C: ever gets tight, the Linux file can move to D: with one command
(`wsl --manage <name> --move D:\WSL`).
