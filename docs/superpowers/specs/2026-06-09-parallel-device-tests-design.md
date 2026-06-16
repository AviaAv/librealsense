# Parallel Device Tests — Design Spec

**Date:** 2026-06-09
**Status:** Approved — increment 1 (plumbing) implemented
**Author:** Avia Avraham (with Claude Code)

## Problem

The pytest hardware suite runs tests strictly serially. Between test groups the
framework power-cycles the device under test and **disables every other hub port**
(`devices.enable_only`), so exactly one camera is live at a time. On a CI machine
holding multiple cameras (D435 + D455 + D585 + …) this leaves all-but-one camera
idle while one camera's tests run — the serial recycle + enumerate overhead
dominates wall-clock.

Goal: run independent cameras' tests **concurrently** (D435's tests on one worker,
D455's on another, at the same time) to cut nightly wall-clock, without introducing
flaky failures.

## Constraints (measured)

### CI hardware (all four nightly agents profiled 2026-06-09)

| Machine | OS | Model | Cores/Threads | RAM | USB controllers |
|---|---|---|---|---|---|
| vtglnx163 | Linux | NUC12WSKi7 i7-1260P | 12 / 16 | 15 GB | 1 (+TB4) |
| vtglnx164 | Linux | NUC10i7FNH i7-10710U | 6 / 12 | 15 GB | 1 |
| rsdsk254 | Windows | NUC12WSKi7 i7-1260P | 12 / 16 | 16 GB | 2 |
| rsdsk255 | Windows | NUC10i7FNH i7-10710U | 6 / 12 | 16 GB | 1 |

- **Compute is not the bottleneck.** Even the 6-core NUC10s handle 2–3 worker
  processes + frame-conversion callbacks comfortably.
- **USB bandwidth is the binding physical constraint.** Every camera funnels
  through the Acroname hub, whose **upstream is a single 5 Gbps (USB 3.0) link
  shared across all ports** (confirmed: cameras enumerate at 5000M behind 5 Gbps
  hubs on a 10 Gbps root). One D4xx at full depth+color+IR ≈ 1.5–2.5 Gbps; two
  streaming heavy simultaneously can saturate the shared 5 Gbps upstream.
- **Key insight:** USB contention **drops or delays frames; it never corrupts the
  frames that arrive** (reliable transport — a frame is delivered whole or not at
  all). Therefore a test is only bandwidth-sensitive if its pass/fail depends on
  frame **rate, drop-count, count-in-a-time-window, latency/TTFF, or inter-frame
  timing** — NOT if it depends on frame **content** or merely "got N valid frames
  eventually."

### Cross-platform

`pytest-xdist` is pure Python (worker comms via `execnet` popen gateway — spawn,
not fork). Works on Windows, Linux x86, and Jetson ARM64. No compiled deps, so it
pip-installs everywhere (unlike `brainstem`/`paramiko`, which `requirements.txt`
gates off `aarch64`).

## Model: opt-in

Default behavior is **unchanged** — serial, full single-device isolation. A test
runs in parallel **only** when explicitly tagged `@pytest.mark.parallel_safe`.
Untagged tests are never affected → zero flake risk on anything un-vetted. The
cost is a larger one-time tagging effort, traded for an incremental, safe rollout.
**When in doubt, leave a test untagged (serial).**

A test is `parallel_safe` iff:
- it does NOT drive hub ports / `hardware_reset` / enumerate-and-count devices /
  fw-update / require 2 devices / run an external tool that enumerates all devices, AND
- its assertions do NOT depend on frame rate, drop-count, count-in-a-window,
  latency/TTFF, or inter-frame/sync timing.

Tests that read/set options, presets, metadata, config/calibration tables,
extrinsics/intrinsics, send debug HWMC, read fw-logs, play back from recorded
files, or grab a few jitter-tolerant frames to check content → `parallel_safe`.

## Classification (all 116 live files audited)

~45 stay serial (untagged/exclusive), ~71 eligible for `parallel_safe`.

### Stays serial — do NOT tag (~45)

**Hub / port / reset / enumerate / external-tool / flash-write (16)**
- `hw-reset/pytest-sanity`, `hw-reset/pytest-stress`, `hw-reset/pytest-t2enum`,
  `hw-reset/pytest-hub-recycle-imu`, `hw-reset/pytest-notifications-callback-gil`,
  `hw-reset/pytest-advanced-mode-toggle` *(confirmed: `toggle_advanced_mode()` forces a device reconnect/re-enumerate)*
- `config/pytest-device-hub`, `config/pytest-eth-config` *(writes eth config to flash — serial, "when in doubt")*
- `d500/test-detect-D555`, `d500/safety/test-interface-config-get-set`
- `options/pytest-uvc-power-stress-test`
- `tools/pytest-enumerate-devices`, `tools/pytest-dds-config`, `tools/pytest-realsense-viewer`
- `multi_devices/pytest-devices-enumeration`, `multi_devices/pytest-devices-streaming`

**Rate / drop / TTFF / throughput (11)**
- `frames/pytest-fps-performance`, `frames/pytest-fps-permutations`,
  `frames/pytest-fps-single-stream`, `frames/pytest-fps-manual-exposure`,
  `frames/pytest-D455_frame_drops`, `frames/pytest-color_frame_drops`,
  `frames/pytest-t2ff-pipeline`, `frames/pytest-t2ff-sensor`,
  `frames/pytest-ah-configurations`, `syncer/pytest-throughput`,
  `hdr/pytest-hdr-performance`

**Inter-frame / sync timing (8)**
- `camera-sync/pytest-intra-camera-sync`, `metadata/pytest-alive`,
  `metadata/pytest-sync`, `options/pytest-drops-on-set`,
  `d400/pytest-depth-ae-convergence`, `d400/pytest-depth-ae-toggle`,
  `d400/pytest-emitter-on-off`, `d400/pytest-d405-calibration-stream`
  *(asserts all-3-streams-per-frameset — composition/sync sensitive)*

**D585S inter-frame ts budget (2)**
- `d500/safety/test-3d-mapping-metadata`, `d500/safety/test-metadata`

**Calibration (4)** — *user decision: serial (convergence sensitive to frame consistency)*
- `calib/pytest-occ-calibrations`, `calib/pytest-tare-calibrations`,
  `calib/pytest-advanced-occ-calibrations`, `calib/pytest-advanced-tare-calibrations`

**rec-play that record from a live camera (4)**
- `rec-play/pytest-got-playback-frames`, `rec-play/pytest-pause-playback-frames`,
  `rec-play/pytest-record-and-stream`, `rec-play/pytest-ros2-compression`

### Eligible for `parallel_safe` (~71)

All option/preset/advanced-mode get-set, metadata reads, calib/config-table get-set,
extrinsics/intrinsics, debug HWMC, fw-logs, dfu compatibility-check, **all
image-quality**, **all file-playback rec-play**, software-device, and brief
jitter-tolerant frame grabs. Representative (full list generated from the audit):
- `image-quality/pytest-{basic-color,basic-depth,has-depth,texture-mapping}`
- `d500/sc-landing-zone/test-stream-{color,depth-dpp,depth-infrared,imu,safety-occ-lpc}`
- `d500/safety/test-{preset-*,app-config-*,verify-default-preset,y16-calibration-format,operational-mode}`
- `d500/test-{get-set-config-table,read-serial-number,temperatures-xu-vs-hwmc,dds-embedded-filters}`
- `d400/pytest-{auto-limits,depth-ae-metadata,depth-ae-mode,disparity-modulation,emitter-frequency*,mipi-motion,pipeline-set-device,hdr-long,hdr-sanity}`
- `hdr/pytest-{hdr-configurations,hdr-preset}`
- `options/pytest-{advanced-mode,options-watcher,out-of-range-throw,presets,rgb-*,set-gain-stress-test,timestamp-domain}`
- `metadata/pytest-{connection-type-found,enabled,usb-type-found,depth-unit}`
- `fw/pytest-fw-errors`, `streaming/pytest-y16-calibration-format`
- `rec-play/pytest-{native-ros2-playback,non-realtime,playback-step,playback-stress,record-software-device}`, `tools/pytest-rs-convert-to-db3`
- `extrinsics/pytest-{consistency,imu}`, `intrinsics/test-motion`
- `debug_protocol/pytest-{build-command,hwmc-errors}`, `fw-logs/pytest-{extended,legacy,xml-helper}`, `dfu/pytest-device-fw-compatibility`

## Architecture

All new logic lives in the **pytest layer** (`conftest.py` + `rspy/pytest/parallel.py`).
**No changes to legacy `run-unit-tests.py`.**

### 1. Worker ↔ device binding
`--dist loadgroup` + `@pytest.mark.xdist_group("<serial>")`. The group marker is
attached **at parametrize time** (`pytest_generate_tests` → `device_helpers`
wraps each `_test_device_serial` value via `parallel.serial_param`), so loadgroup
keeps all tests of one serial **wholesale on one worker, sequentially** —
preserving per-device serial semantics. Spawn `-n min(num_devices, physical_cores)`;
with workers ≥ devices, one camera per worker. No custom scheduler.

**Deterministic device discovery is required for grouping (`devices.by_spec`).**
`by_product_line`/`by_name` return a *set*; string set-iteration order varies per
process (hash seed). Under xdist each worker is a separate process, so a single-spec
`device("D400*")` ("first matching device") resolved to a *different* serial on each
worker → `Different tests were collected between gw0 and gw1` → xdist aborts the run.
Fix: `by_spec` yields `sorted(...)`, so every process resolves the same first match.
`device_each` was already immune (it takes all serials), but sorting also stabilizes
its parametrization order across workers. Verified on hardware: the full mixed
file-set crashed instantly before the fix, runs to completion after.

Two further implementation gotchas (each cost a real debugging cycle, encoded in the code):
- **Stamp at parametrize time, not in `pytest_collection_modifyitems`.** xdist
  derives the loadgroup `@<group>` nodeid suffix in its own *worker-side* collection
  hook (`xdist/remote.py`), which runs before conftest's hook. A marker added in a
  conftest collection hook arrives too late → xdist sees nothing → round-robin →
  the same camera is split across workers → concurrent hub access. Adding the
  marker during parametrization makes it present before xdist reads it.
- **Gate on xdist *presence*, not worker count.** `pytest_generate_tests` runs on
  the xdist worker, whose config does NOT carry `numprocesses` (only the controller
  does). Gating the stamp on `numprocesses` silently disables grouping on workers.
  Gate on `config.pluginmanager.hasplugin("xdist")` (true in both processes).

### 2. Hub is a single-owner resource → controller powers, workers run hub-less
**Verified on real hardware (perclnx466, Acroname USBHub3p):** the BrainStem
accepts only ONE process connection (a 2nd `connect()` → `result=25`), BUT
`disconnect()` does not cut port power, and a hub-less process enumerates the
powered cameras fine via plain `rs.context()`. So the design is **not** an
inventory handoff (the heavy draft was discarded) — it's simply:

- **Worker** (`is_xdist_worker`): `devices.disable_hub()` → never connects the hub;
  runs hub-less. Its own `devices.query()` enumerates the controller-powered
  cameras (using the full enumeration window — a fresh worker process needs it),
  so device-marker resolution at collection works with no handoff.
- **Controller** (parallel phase only): after `init_hub()`, `hub.connect()` +
  `hub.enable_ports()` — power ALL ports **once, without** `query()`'s
  recycle (disable+enable) churn (a mid-enumeration disable would empty the
  workers' device list). The controller runs no tests; it exists to power ports.
- `devices.query(recycle_ports=not parallel)` so the controller doesn't recycle in
  parallel; workers are hub-less so recycle is a no-op anyway.

### 3. The one real defect found + fixed (1 line)
`devices.map_unknown_ports()` calls `hub.disable_ports()` (to leave a clean state
for the *serial* path). The controller was running it in the parallel phase →
powering every camera **off** before the hub-less workers enumerated → workers saw
0 devices → `SKIP-<pattern>` sentinels. Fix: guard it `if not worker and not
parallel:`. No non-exclusive `enable_only`, no file-lock, no `module_device_setup`
rewrite were needed — `module_device_setup` only gains `recycle = ... and not
is_xdist_worker(...)` (workers don't recycle; the controller already powered them).

### 4. Phasing — two pytest invocations, sequenced at the CI step
- **Phase 1 (serial):** `pytest -p no:xdist -m "not parallel_safe"` — untagged +
  exclusive, exactly today's path, full isolation.
- **Phase 2 (parallel):** `pytest -n <N> --dist loadgroup -m parallel_safe` —
  vetted-safe tests, device-pinned.

The two tag-pools are statically disjoint, so **no runtime exclusive-barrier** is
needed (an exclusive hub/reset test can never run concurrently with a streamer).
Jenkins Groovy continues to parse per-test `.log` files for clickable links; only
the two console summaries concatenate.

### 5. Bandwidth — handled by the tag, not a separate governor
`parallel_safe` is defined to exclude every rate/drop/TTFF/sync assertion, so
concurrent streaming on the shared 5 Gbps upstream cannot fail a tagged test by
construction. The worker cap (`--max-device-workers`, default
`min(devices, cores)`) is the only throttle.

### 6. Degrade paths
- **No hub (local dev):** workers `hw_reset` only their own device; non-exclusive
  enable is effectively a wait-for-enumeration. Parallel still works.
- **Single device:** `-n 1`, collapses to serial — no regression.
- **xdist absent / `-n0` / no tags:** everything runs serial as today; the
  `parallel_safe` marker is inert (xdist treated as OPTIONAL, not required).

## Rollout

1. **[DONE] Land the plumbing with no behavioral risk** — `parallel_safe` marker,
   `rspy/pytest/parallel.py` (xdist_group stamping, `resolve_num_workers`, graceful
   degrade), `pytest-xdist` in requirements (optional). No tests tagged → behavior
   identical to today. Verified: 3 hardware-free sanity tests pass serially and
   across 2 xdist workers; infra regression suite 139/139 pass.
2. **[DONE] Hub single-owner model (§2, §3)** — workers hub-less, controller powers
   ports once (no recycle), skip `map_unknown_ports()` in parallel. ~8 lines net.
   **Validated on perclnx466 (Acroname hub, D436/D455/D585S/D555):** parallel smoke
   `-n2 --dist loadgroup` → 10 passed (D436 and D455 concurrent on separate workers),
   including a cold start with all ports initially disabled.
3. Tag a small first batch of obviously-safe tests; enable Phase 2 on one CI
   machine; compare against the serial baseline before widening.
4. Expand the `parallel_safe` set incrementally, watching nightly for regressions.

### Hardware validation (2026-06-09, 2 cameras: D455 + D405, no hub)

- Marker + xdist_group pinning verified live: each camera's tests stay on one
  worker (`@<serial>` suffix), no concurrent same-camera access.
- `device_each` subset (5 real files, fast metadata/extrinsics reads): serial
  131s → parallel 73s = **1.8×** — near-ideal, because light read tests don't
  contend on USB and many tests amortize the one-time per-camera setup.
- Full mixed 9-file set, after the `by_spec` determinism fix: runs to completion,
  serial 190s → parallel 133s = **1.4×**. Lower than 1.8× for two reasons, both
  about single-spec `device()` tests → increment-2 refinements:
  - **Balancing:** deterministic ordering pins *every* single-spec `device()` test
    to the lowest serial, overloading one camera's worker while the other idles.
    A least-loaded assignment (rather than lowest-serial) would rebalance.
  - **Transient robustness:** concurrent enumeration on the shared (no-hub) bus
    occasionally drops a camera at fixture setup ("Camera not connected"). Masked
    by `--retries` (CI default; conftest already retries setup-phase failures) and
    removed by the increment-2 hub port-ownership model. Worst-case on no-hub;
    a managed hub isolates per-port power.
- The worst-case ratio (0.76) was a synthetic 3-heavy-concurrent-depth-stream test
  with tiny test count — bandwidth contention + no amortization. Representative
  read/control tests do not hit that.

## Open items
- Verify BrainStem (Acroname) and UniFi-SSH hub clients tolerate the file-locked
  serialized access pattern under N workers (expected yes; validate on hardware).
- Latent bug noted (not fixed — out of scope): `devices.py` does
  `sys.path.insert(1, repo.find_pyrs_dir())` unguarded; when no build dir exists
  AND a stale pyrealsense2 sits in the user-site, `None` is inserted into
  `sys.path` and the user-site block-finder raises `TypeError`. Harmless on CI
  (build always present). Flag for a follow-up guard.
