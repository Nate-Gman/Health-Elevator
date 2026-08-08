# HealthElevator.py — Gravity Tower Digital Twin

> A 100% standalone Python monolith that builds, animates, and **operates** a 60-storey skyscraper whose elevators run on **nothing but gravity and human weight** — in real time, mechanically and energetically to scale, in a single file.

---

## Table of Contents

- [What This Is](#what-this-is)
- [The Big Idea (30-Second Version)](#the-big-idea-30-second-version)
- [Quick Start](#quick-start)
- [Dependencies](#dependencies)
- [Running the Program](#running-the-program)
- [Three Modes](#three-modes)
  - [1. TOWER Mode](#1-tower-mode)
  - [2. MACHINE Mode](#2-machine-mode)
  - [3. DAY Mode](#3-day-mode)
- [Controls Reference](#controls-reference)
- [Project Structure](#project-structure)
- [Architecture at a Glance](#architecture-at-a-glance)
- [Key Engineering Concepts](#key-engineering-concepts)
  - [Zoning](#zoning)
  - [Counter-Running Cabin Pairs](#counter-running-cabin-pairs)
  - [Cascading Weight Banks and Vault Battery](#cascading-weight-banks-and-vault-battery)
  - [Token Economy](#token-economy)
  - [Registered Demand and Batching](#registered-demand-and-batching)
  - [Low-Imbalance Mechanics](#low-imbalance-mechanics)
  - [Health Dividend](#health-dividend)
- [The Building Specification](#the-building-specification)
- [Zone Plan](#zone-plan)
- [Physics Model](#physics-model)
- [Token Economy and Real Dollars](#token-economy-and-real-dollars)
- [What a Simulated Day Looks Like](#what-a-simulated-day-looks-like)
- [Honesty Disclaimer](#honesty-disclaimer)
- [For a Deeper Dive](#for-a-deeper-dive)

---

## What This Is

`HealthElevator.py` is a **to-scale digital twin** of a gravity-and-human-power vertical transit system. It models a 60-storey, 234-metre commercial tower where the entire elevator system has **zero motors, zero drives, and zero grid connection for motion**. The only energy input is the potential energy of mass that people carry up the stairs.

It is the vertical re-engineering of the HOHEV modelling method: the same to-scale Part/Mesh geometry, the same honest first-order energy ledger, the same three-mode inspector — but every subsystem is re-hosted in a tower and the "fuel" is now the **potential energy of mass** that people carried up the stairs.

The program is a single Python file (approximately 3,790 lines) with no external assets, no build step, and no data files. Everything — the 3D geometry, the physics simulation, the token economy, the 24-hour traffic model, the UI, and the informational specification — is generated from code.

---

## The Big Idea (30-Second Version)

Every hoistway holds **two cars** on **one rope**, over **one sheave**. Whichever side is heavier falls, and its fall pulls the other side up. If a loaded car is going DOWN at the exact moment another car needs to go UP, the down car's own weight does the lifting — for free, no tray, no effort.

The only time a **human** has to supply weight is when the two sides do NOT naturally balance — an up call with nobody going down to match it. For exactly that moment, the system needs a bank of pre-carried weight already sitting in the sky-lobby **vault** above, ready to drop. That weight got there earlier because someone walked a tray of it up the stairs and banked it — and was paid in **tokens** for doing so.

**Natural counter-traffic pays for itself automatically. The leftover imbalance — and only the leftover — is what people are carrying, and it is what they are paid for.**

---

## Quick Start

```bash
# Install dependencies
pip install numpy pygame

# Run the program
python HealthElevator.py
```

That's it. No build step, no configuration, no data files.

---

## Dependencies

| Dependency | Purpose | Version |
|---|---|---|
| **Python 3** | Runtime | 3.8+ recommended |
| **numpy** | Vector math, rotation matrices, vertex arrays | Any recent |
| **pygame** | Window, rendering, input, 2D drawing primitives | Any recent |

No other packages are needed. The 3D engine is a custom software renderer built on pygame's 2D drawing primitives — no OpenGL, no external 3D library.

---

## Running the Program

```bash
python HealthElevator.py
```

On launch, a banner prints to the console summarizing the building, then a 1480×900 pygame window opens in **TOWER** mode.

---

## Three Modes

Cycle between modes with **TAB** or click the mode tabs in the top bar.

### 1. TOWER Mode

Orbit the whole 234 m building to scale. See:

- 60 floor plates with two structural set-backs (podium → mid → upper)
- 6 independent vertical zones, each with its own hoistways
- 5 sky lobbies (transfer floors between zones)
- 14 hoistways containing 28 live counter-running cabins
- Fixed base counterweights in their own chases
- 60 landing weight banks (one per storey)
- 7 sky-lobby staged-mass vaults (the building's "battery")
- The health stair (the only energy input)
- Short-haul tray shuttles (pure-gravity tray movers)
- Roof plant and crown

All cabins, counterweights, tray stocks, and shuttles **move live** as the simulation runs. The 3D parts are built from the `DIMS` and `TOWER` specification tables at the top of the file, so every dimension is real and drawn to scale.

### 2. MACHINE Mode

Orbit **one zone's gravity machine** in mechanical detail. See:

- Pit slab and oil buffers
- T-section guide rails with sprung roller guide shoes
- Two counter-running cabins (A ascending, B descending) with sling, crosshead, doors, and roof tray racks
- Head sheave assembly (grooved traction sheave, diverter sheaves, sheave shaft)
- Differential 2:1 reeving blocks (mechanical advantage for upper zones)
- Traction ropes (6 × 13 mm steel ropes)
- Base counterweight with stacked weight trays
- Overspeed governor and wedge safety gear (purely mechanical)
- Holding brake / ratchet-pawl (the only actuators — latches, not motors)
- Landing weight bank with registration post and call/credit register

Four view styles: **full**, **exploded**, **assembly** (step-through build), and **section-cut** (half-cut to see inside the shaft).

### 3. DAY Mode

Run a **full 24-hour operating day** at adjustable time-warp (1× to 900×). See:

- Live sky that transitions from day to night with a sun/moon arc
- The tower rendered in the scene with live cabin positions
- A **live zone elevation strip** showing every zone, every cabin position, every vault charge bar, queue length, average wait, and token multiplier — updating in real time
- A **DAY HUD** with:
  - Operating mode (UP-PEAK / DOWN-PEAK / LUNCH / INTERFLOOR / NIGHT / MASS SHORTFALL)
  - 0 kW grid draw (always)
  - Average hall wait time
  - Vault charge bars (lowest vault, staged mass, hall queue, day progress)
  - Tray flow ledger (staged by walkers, spent on lifts, re-staged by descent, moved by shuttles, in landing banks)
  - Full statistics: registered calls, journeys completed, transfers, journey time, worst-zone p90 wait, cars moving, stalls, balked, stair carries, flights climbed, human work stored, kilocalories burned, tokens issued, grid energy (0), conventional comparison, avoided cost, CO₂ avoided, walker pool $, $/token, $/carry, **global scale estimates** (~300 TWh/year, ~$48B/year, ~111 Mt CO₂/year)
- A **timeline** at the bottom showing vault charge over the 24-hour cycle with a live cursor

Use `,` and `.` to slow down or speed up the time-warp.

---

## Controls Reference

| Key / Action | What It Does |
|---|---|
| **TAB** | Cycle TOWER / MACHINE / DAY modes |
| **click tabs** | Or click the mode tabs in the top bar |
| **drag** | Orbit the model (rotate camera) |
| **right-drag** | Pan the camera |
| **wheel** | Zoom in / out (or scroll the info panel) |
| **click part** | Pin it in the inspector (left sidebar) |
| **click PARTS list** | Select any part from the left sidebar list |
| **1** | Full view (assembled) |
| **2** | Exploded view |
| **3** | Assembly view (step-through build) |
| **4** or **X** | Section-cut (half-cut to see inside) |
| **E** | Quick exploded toggle |
| **L** | Toggle part labels |
| **R** | Reset the camera |
| **[** / **]** | Step the assembly build backward / forward |
| **A** | Assemble all parts |
| **C** | Clear the assembly |
| **,** / **.** | Slow / speed up TIME-WARP (DAY mode only) |
| **V** | Verification checklist overlay |
| **I** | Full informational specification panel (scrollable, with TOC) |
| **H** | Quick help card |
| **Esc** | Close a panel, or quit at the top level |
| **Q** | Quit |

---

## Project Structure

```
HealthElevator/
├── HealthElevator.py    # The entire program (3,790 lines, single file)
├── Goal.md              # The original design goals (5-point specification)
├── ReferenceCode/       # Reference code from the HOHEV/SE.py marine twin
├── README.md            # This file
└── OVERVIEW.md          # Extremely detailed technical overview
```

---

## Architecture at a Glance

The program is organized into 10 numbered sections within a single file:

| Section | Lines (approx.) | What It Contains |
|---|---|---|
| **1 — Engineering Specification** | 76–287 | All dimensional constants, zone plan, physical constants, token economy parameters, walker model, traffic profile, reference energy figures, economy pricing |
| **2 — Colors & Theme** | 290–335 | Every color used in the UI, organized by subsystem |
| **3 — Mini 3D Engine** | 337–534 | `Mesh` class, `Part` class, rotation matrices, primitive builders (`_box`, `_solid_cylinder`, `_annulus_cylinder`, `_pipe`), static/spinner mesh helpers |
| **4 — Zone Plan + Geometry Builders** | 536–1217 | `ZoneSpec` class, zone/floor/population helpers, `build_tower_parts()` (the whole 234 m tower), `build_machine_parts()` (one zone's gravity machine) |
| **5 — Gravity Transit Physics** | 1220–1303 | Resistance force, required advantage, tray mass needed, imbalance ratio, car acceleration, run time, run energy, metabolic energy, reference grid kWh |
| **6 — The Building** | 1305–2016 | `Journey`, `Shaft`, `ZoneState`, `Building`, `DayWorld` — the full live simulation: dispatch, boarding, vault plumbing, walkers, shuttles, traffic spawning, statistics |
| **7 — Informational Specification** | 2018–2307 | `build_info_sections()` — the full scrollable spec panel content (about, core loop, building, zoning, cabins, vaults, token economy, money, demand, mechanics, health dividend, measured results, honest physics, verification checklist, controls) |
| **8 — HUD / UI Helpers** | 2310–2383 | Gradient fill, progress bar, panel, text wrapping, TOC label, key-line splitting, 3D label rendering |
| **9 — 3D Renderer** | 2385–2643 | `TowerRenderer` class — camera, projection, painter's algorithm sorting, lighting, section-cut, exploded/assembly views, hover-picking, label placement |
| **10 — Application** | 2646–3790 | `App` class — pygame init, event handling, simulation loop, live mesh sync, all drawing (topbar, preview, part list, spec card, scale bar, tower legend, machine stats, day mode, zone strip, day HUD, timeline, help, checklist, info panel), main loop |

---

## Key Engineering Concepts

### Zoning

The tower is divided into **6 independent vertical zones** of 9–11 floors each, joined by **5 sky lobbies** (transfer floors). No hoistway runs the full height of the building. No walker ever hauls mass past the next sky lobby.

- **Lower zones** (highest traffic): more hoistways, bigger cabins, direct 1:1 roping for speed
- **Upper zones** (lowest traffic): fewer, smaller cabins, differential 2:1 reeving (halves the weight imbalance needed, at the cost of half the speed)

This is the single biggest efficiency gain. Total human-carried mass-distance drops dramatically.

### Counter-Running Cabin Pairs

Every hoistway holds **two rope-linked cabins** on one head sheave. Cabin A rises exactly as cabin B descends. The loaded descending car IS the lift power for the ascending car.

When the dispatcher pairs an up call with a down call, the net energy of the run falls to the **friction loss alone** — not the full lift work.

### Cascading Weight Banks and Vault Battery

Modular **11.34 kg (25 lb) trays** are the currency of the system. Walkers deposit them at landing banks and are credited on the spot. Trays are then staged upward in steps by:

1. Short-haul pure-gravity tray shuttles
2. The lifts' own surplus energy (descending load recovery)

A sky-lobby **vault** of staged trays is literally the building's battery: stored joules = mass × g × height. Zone *i* draws from vault *i+1* (above) and returns to vault *i* (below). Down-peak traffic pushes trays back up.

### Token Economy

Credit = trays × flights climbed × height factor × **scarcity**.

- **Height** adds up to +85% at the top of the tower
- **Scarcity** adds up to +260% when a vault falls below 55% full

Because fewer people go to the top, the upper multipliers run higher and pull carriers exactly where the mass is short. This turns the "less traffic higher up" problem into a **self-balancing incentive gradient** — no central control needed.

### Registered Demand and Batching

Every hall call is registered with a timestamp at the landing post. Because the system knows the call before the rider is in the car, it:

- Pre-positions the exact counter-mass first
- Batches same-direction riders into one balanced run
- Keeps 6% of slots free for genuine incapacity (priority queue jumping)
- Shows estimated wait so riders can choose to walk part-way and carry a tray instead

### Low-Imbalance Mechanics

Roller guide shoes on machined T-rails, lubricated grooved sheaves, and compensated rope mass bring total resistance to `mu_eff = 0.028` (2.8% of suspended mass). The commanded imbalance is `2.05 × 0.028 = 5.7%` — inside the 3–8% specification band.

Upper zones add **differential 2:1 reeving** (car 2:1, counterweight 1:1), which halves the tray mass a run needs and halves car speed to 1.30 m/s — exactly the right trade where traffic is light.

### Health Dividend

The only energy input to the whole tower is people climbing stairs with trays, at 23% metabolic efficiency. The building does not have an energy bill; it has a **fitness programme** that happens to move everybody vertically.

One carry of 2.2 trays up zone 1 (10 floors, 39 m) = ~4,340 J stored and about 18 kcal burned. Over a simulated day, that's roughly 105 flights and 420 kcal per occupant.

---

## The Building Specification

| Parameter | Value |
|---|---|
| **Storeys** | 60 |
| **Height to main roof** | 234.0 m |
| **Floor-to-floor height** | 3.90 m |
| **Gross floor area** | 100,000 m² |
| **Design population** | 1,640 (declines with height) |
| **Podium floors** | 4 (wider retail/lobby base) |
| **Podium plan** | 52.0 × 46.0 m |
| **Mid shaft plan** | 42.0 × 38.0 m |
| **Upper block plan** | 34.0 × 30.0 m |
| **Structural core** | 20.0 × 17.0 m |
| **Crown height** | 26.0 m (roof plant only — no machine room) |

### Cabin Dimensions

| Parameter | Value |
|---|---|
| **Cabin** | 2.00 × 2.30 × 2.45 m |
| **Shaft (holds 2 cabins)** | 4.60 × 3.20 m |
| **Head traction sheave** | 1.10 m diameter, 6 rope grooves |
| **Rope** | 13 mm steel, 6 per hoistway, 0.72 kg/m |
| **Tray** | 0.42 × 0.30 × 0.075 m, 11.34 kg (25 lb) |
| **Tray stack max** | 26 trays on a cabin roof rack |

---

## Zone Plan

| Zone | Floors | Hoistways | Capacity | Reeving | Car Speed | Cabin Mass |
|---|---|---|---|---|---|---|
| 1 | 1–11 | 3 | 16 pax | 1:1 | 2.60 m/s | 900 kg |
| 2 | 11–21 | 3 | 16 pax | 1:1 | 2.60 m/s | 900 kg |
| 3 | 21–31 | 2 | 13 pax | 1:1 | 2.60 m/s | 820 kg |
| 4 | 31–41 | 2 | 13 pax | 1:1 | 2.60 m/s | 820 kg |
| 5 | 41–51 | 2 | 10 pax | 2:1 | 1.30 m/s | 700 kg |
| 6 | 51–60 | 2 | 8 pax | 2:1 | 1.30 m/s | 620 kg |

**Total: 14 hoistways, 28 cabins, 0 motors.**

Sky lobbies (transfer floors): **11, 21, 31, 41, 51**

---

## Physics Model

The whole machine is one equation: **a rope over a sheave with mass on both sides**. Whichever side is heavier falls, and the difference has to beat the friction.

### Key Equations (all in SI units)

- **Resistance force**: `F_resist = mu_eff × m_suspended × g` (newtons)
- **Required advantage**: `m_advantage = IMBAL_MARGIN × mu_eff × m_suspended / reeving` (kg)
- **Car acceleration**: `a = (delta_kg × reeving × g - F_resist) / (m_suspended × (1 + rot_inertia_fr))`, capped at 0.95 m/s²
- **Run time**: trapezoidal profile (accelerate → cruise → decelerate) + levelling dwell
- **Run energy**: `E = (load_up - load_dn) × g × |ds| + mu_eff × m_suspended × g × |ds|` (joules)
- **Metabolic energy**: `E_metabolic = mass × g × rise / metabolic_eff / 1000` (kJ)

### Key Constants

| Constant | Value | Meaning |
|---|---|---|
| `G` | 9.80665 m/s² | Standard gravity |
| `MU_EFF` | 0.028 | Effective resistance coefficient (roller guides + lubricated sheaves) |
| `IMBAL_MARGIN` | 2.05 | Imbalance commanded over the friction floor → 5.7% |
| `RECOVERY_EFF` | 0.86 | Descending surplus → re-staged tray height efficiency |
| `ROPE_SPEED_MS` | 2.60 m/s | Rope speed cap (car speed = this / reeving MA) |
| `ACCEL_CAP_MS2` | 0.95 m/s² | Comfort limit on car acceleration |
| `BATCH_HOLD_S` | 14.0 s | Collect window before a run is released |
| `REPOSITION_S` | 20.0 s | Wait before an empty car is sent to a call |

---

## Token Economy and Real Dollars

Goal.md only specifies tokens as internal credit. The program prices them against the one real saving on the books: **the electricity a conventional lift bank would have burned**.

At 100% payout (`ECONOMY.walker_payout_frac = 1.0`), the entire avoided bill becomes the walker pool. The building never pays out more than it saved.

### Reference Day Figures (measured from a simulated 24-hour run)

| Metric | Value |
|---|---|
| Avoided electricity | ~732 kWh/day |
| Avoided cost | ~$117/day (~$42,705/year) |
| Avoided CO₂ | ~271 kg/day |
| Tokens issued | ~532,700/day |
| Stair carries | ~17,400/day |
| Flights climbed | ~173,000/day |
| Value per token | ~$0.00022 |
| Value per stair carry | ~$0.0067 |
| Value per flight | ~$0.00068 |

The token's real job was never the payout — it is the **allocation signal** that steers carriers to whichever vault is running low. The dividend that actually matters at this scale is the **exercise**, not the cash.

### Global Scale: If Every Elevator Were Replaced

Industry estimates put the global installed elevator fleet at **~20 million units** consuming **~300 TWh/year** — roughly **1% of world electricity production**. Most are low-rise, low-traffic units averaging ~15,000 kWh/year each. The model tower's 14 lifts avoid ~267,000 kWh/year (well above average because they serve a 60-storey building with heavy commuter traffic).

If the gravity-transit principle replaced every traction and hydraulic lift on the planet:

| Metric | Value |
|---|---|
| Avoided electricity | ~300 TWh/year |
| Avoided cost | ~$48 billion/year |
| Avoided CO₂ | ~111 million tonnes/year |
| Equivalent cars off the road | ~24 million |
| Equivalent nuclear reactors | ~80 (1 GW each, running flat out) |
| Equivalent coal plants | ~150 (500 MW each) |

300 TWh is not a rounding error — it is **~80 nuclear reactors or ~150 coal plants running flat out for a year**, just to move elevators. Gravity transit would zero that line item, not by using less electricity, but by **removing the motor entirely**.

---

## What a Simulated Day Looks Like

On the default traffic profile and 1,640-person population:

- ~6,700 calls registered, ~6,600 journeys completed
- 0 balked, 0 stalls, ~12,300 sky-lobby transfers
- Average hall wait: 22 seconds
- Worst zone 90th percentile wait: 44 seconds
- Average door-to-door journey: ~10 minutes (including transfers)
- ~17,400 stair carries, ~173,000 flights climbed
- ~165 MJ of human lift work banked
- ~690,000 kcal burned
- Vaults settle into a steady band and stay there
- **Grid energy for motion: 0.00 kWh** (vs ~732 kWh conventional)

Per occupant: roughly **105 flights and 420 kcal per day**. This building only works if a real share of the population actually carries trays up stairs, every day. It is a fitness programme with a lift attached, not a lift that happens to be free.

---

## Honesty Disclaimer

This is **NOT perpetual motion** and **NOT free energy**. Every joule that lifts a passenger was put in by a human leg muscle, at a metabolic cost several times the mechanical work.

The system wins on three real effects, nothing else:

1. **Counterweighting** — you only pay for the difference
2. **Counter-running pairs** — the down traffic pays for the up
3. **Zoning** — mass-distance drops because nobody carries far

Over a balanced day, up and down passenger work cancel almost exactly, so the true net input is the **friction loss** — which is why `mu_eff` is the number the whole design lives or dies on.

It is **slower** than a motor (2.60 m/s vs 6–10 m/s for modern high-rise banks), and cross-tower trips require transfers. Speed is the price paid for the zero.

The other price is **mass**: roughly 1,300+ tonnes of tray steel is in circulation, and a full sky-lobby vault puts ~159 tonnes on one structural bay. If the vaults run dry, the cars **stall** — the model shows this happening rather than hiding it, and the token multiplier is the mechanism that fixes it.

---

## For a Deeper Dive

See **[OVERVIEW.md](OVERVIEW.md)** for an extremely detailed, overly expanded technical walkthrough of every subsystem, every class, every function, every equation, and every data structure in the program — from the rotation matrices in the 3D engine to the dispatch logic in the `Shaft` class to the vault plumbing in the `ZoneState` class to the traffic-spawning gaussians in the `Building` class.
