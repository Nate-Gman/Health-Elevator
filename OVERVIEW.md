# OVERVIEW — How HealthElevator.py Works, In Extreme Detail

> This document is an overly expanded, exhaustive walkthrough of every subsystem, every class, every function, every equation, and every data structure in `HealthElevator.py`. It is written for someone who wants to understand not just *what* the program does, but *how every line of it works* — from the rotation matrices in the 3D engine to the dispatch logic in the `Shaft` class to the traffic-spawning gaussians in the `Building` class.

---

## Table of Contents

1. [File-Level Architecture](#1-file-level-architecture)
2. [Section 1 — Engineering Specification (The Numbers)](#2-section-1--engineering-specification-the-numbers)
   - [2.1 The TOWER Dictionary](#21-the-tower-dictionary)
   - [2.2 Derived Constants](#22-derived-constants)
   - [2.3 The DIMS Dictionary](#23-the-dims-dictionary)
   - [2.4 Display Scaling Functions](#24-display-scaling-functions)
   - [2.5 The ZONE_PLAN](#25-the-zone_plan)
   - [2.6 Physical Constants](#26-physical-constants)
   - [2.7 Mechanical Loss Constants](#27-mechanical-loss-constants)
   - [2.8 Token Economy Parameters](#28-token-economy-parameters)
   - [2.9 Walker Model](#29-walker-model)
   - [2.10 Traffic Profile](#210-traffic-profile)
   - [2.11 Reference Energy Figures](#211-reference-energy-figures)
   - [2.12 Economy Pricing](#212-economy-pricing)
3. [Section 2 — Colors and Theme](#3-section-2--colors-and-theme)
4. [Section 3 — The Mini 3D Engine](#4-section-3--the-mini-3d-engine)
   - [4.1 Rotation Matrices](#41-rotation-matrices)
   - [4.2 Utility Functions](#42-utility-functions)
   - [4.3 The Mesh Class](#43-the-mesh-class)
   - [4.4 Primitive Builders](#44-primitive-builders)
   - [4.5 The Part Class](#45-the-part-class)
   - [4.6 Group Helper](#46-group-helper)
5. [Section 4 — Zone Plan and Geometry Builders](#5-section-4--zone-plan-and-geometry-builders)
   - [5.1 The ZoneSpec Class](#51-the-zonespec-class)
   - [5.2 Zone Instances and Sky Lobbies](#52-zone-instances-and-sky-lobbies)
   - [5.3 Population Model](#53-population-model)
   - [5.4 Vault Capacity](#54-vault-capacity)
   - [5.5 Travel Planning Functions](#55-travel-planning-functions)
   - [5.6 Massing and Shaft Layout](#56-massing-and-shaft-layout)
   - [5.7 The TOWER_LIVE Registry](#57-the-tower_live-registry)
   - [5.8 build_tower_parts() — The Whole Building](#58-build_tower_parts--the-whole-building)
   - [5.9 build_machine_parts() — One Zone's Gravity Machine](#59-build_machine_parts--one-zones-gravity-machine)
6. [Section 5 — Gravity Transit Physics](#6-section-5--gravity-transit-physics)
   - [6.1 resist_force_N()](#61-resist_force_n)
   - [6.2 required_advantage_kg()](#62-required_advantage_kg)
   - [6.3 tray_mass_needed_kg()](#63-tray_mass_needed_kg)
   - [6.4 imbalance_ratio()](#64-imbalance_ratio)
   - [6.5 car_accel_ms2()](#65-car_accel_ms2)
   - [6.6 run_time_s()](#66-run_time_s)
   - [6.7 run_energy_J()](#67-run_energy_j)
   - [6.8 tray_units()](#68-tray_units)
   - [6.9 metabolic_kj()](#69-metabolic_kj)
   - [6.10 stair_climb_time_s()](#610-stair_climb_time_s)
   - [6.11 reference_grid_kwh()](#611-reference_grid_kwh)
7. [Section 6 — The Building (Live Simulation)](#7-section-6--the-building-live-simulation)
   - [7.1 The Journey Class](#71-the-journey-class)
   - [7.2 The Shaft Class](#72-the-shaft-class)
   - [7.3 The ZoneState Class](#73-the-zonestate-class)
   - [7.4 The Building Class](#74-the-building-class)
   - [7.5 The DayWorld Class](#75-the-dayworld-class)
   - [7.6 sky_colors()](#76-sky_colors)
8. [Section 7 — Informational Specification](#8-section-7--informational-specification)
9. [Section 8 — HUD and UI Helpers](#9-section-8--hud-and-ui-helpers)
10. [Section 9 — The 3D Renderer](#10-section-9--the-3d-renderer)
    - [10.1 TowerRenderer.__init__()](#101-towerrenderer__init__)
    - [10.2 Camera Controls](#102-camera-controls)
    - [10.3 View Modes](#103-view-modes)
    - [10.4 tick() — Animation Interpolation](#104-tick--animation-interpolation)
    - [10.5 _layout() — Part Positioning](#105-_layout--part-positioning)
    - [10.6 render() — The Main Rendering Pipeline](#106-render--the-main-rendering-pipeline)
    - [10.7 Hover-Picking](#107-hover-picking)
11. [Section 10 — The Application](#11-section-10--the-application)
    - [11.1 App.__init__()](#111-app__init__)
    - [11.2 Event Handling](#112-event-handling)
    - [11.3 Simulation Loop](#113-simulation-loop)
    - [11.4 sync_live() — Writing Simulation to Meshes](#114-sync_live--writing-simulation-to-meshes)
    - [11.5 Drawing: TOWER and MACHINE Modes](#115-drawing-tower-and-machine-modes)
    - [11.6 Drawing: DAY Mode](#116-drawing-day-mode)
    - [11.7 Overlays: Help, Checklist, Info Panel](#117-overlays-help-checklist-info-panel)
    - [11.8 The Main Loop](#118-the-main-loop)
12. [End-to-End Data Flow](#12-end-to-end-data-flow)
13. [Glossary](#13-glossary)

---

## 1. File-Level Architecture

`HealthElevator.py` is a single Python file of approximately 3,790 lines. It is deliberately monolithic — no imports of local modules, no external data files, no build step. The only external dependencies are `numpy` (for vector math and rotation matrices) and `pygame` (for windowing, input, and 2D drawing primitives).

The file is organized into 10 numbered sections, each separated by a banner comment block. The sections are:

1. **Engineering Specification** — All dimensional constants, zone plan, physical constants, economy parameters. These are pure data dictionaries and scalar constants. No functions.
2. **Colors and Theme** — A flat list of RGB tuples. No logic.
3. **Mini 3D Engine** — The `Mesh` class, `Part` class, rotation matrices, and geometric primitive builders. This is a self-contained software 3D renderer toolkit that knows nothing about elevators.
4. **Zone Plan and Geometry Builders** — `ZoneSpec` class, population/floor helpers, travel planning functions, and the two big geometry builders: `build_tower_parts()` and `build_machine_parts()`. These produce lists of `Part` objects.
5. **Gravity Transit Physics** — Pure functions that compute resistance, advantage, acceleration, travel time, energy, and metabolic cost. No state.
6. **The Building** — `Journey`, `Shaft`, `ZoneState`, `Building`, `DayWorld` classes. This is the live simulation: dispatch, boarding, vault plumbing, walkers, shuttles, traffic spawning, statistics.
7. **Informational Specification** — `build_info_sections()` returns a list of (title, lines) tuples that form the scrollable spec panel.
8. **HUD and UI Helpers** — Small drawing utilities: gradient fill, progress bar, panel, text wrapping, label rendering.
9. **3D Renderer** — `TowerRenderer` class: camera, projection, painter's algorithm sorting, lighting, section-cut, exploded/assembly views, hover-picking.
10. **Application** — `App` class: pygame initialization, event handling, simulation loop, all drawing code (topbar, preview, part list, spec card, scale bar, tower legend, machine stats, day mode, zone strip, day HUD, timeline, help, checklist, info panel), and the main loop.

The data flow is:

```
Section 1 (constants)
    ↓
Section 4 (ZoneSpec + geometry builders → Part lists)
    ↓
Section 5 (physics functions, called by Section 6)
    ↓
Section 6 (Building simulation → live state)
    ↓
Section 9 (TowerRenderer projects Part lists to 2D)
    ↓
Section 10 (App ties it all together: events → simulation → render → display)
```

---

## 2. Section 1 — Engineering Specification (The Numbers)

This section (lines 76–287) contains every dimensional constant, physical constant, and tuning parameter in the model. Everything downstream is generated from these numbers. Changing a value here changes the geometry, the physics, and the simulation.

### 2.1 The TOWER Dictionary

```python
TOWER = {
    "floors":            60,      # occupied storeys (>= 50 as specified)
    "floor_h_m":         3.90,    # floor-to-floor height
    "podium_floors":      4,      # wider retail / lobby podium
    "base_w_m":          52.0,    # podium plan (E-W)
    "base_d_m":          46.0,    # podium plan (N-S)
    "mid_w_m":           42.0,    # main shaft plan after the first set-back
    "mid_d_m":           38.0,
    "top_w_m":           34.0,    # upper block after the second set-back
    "top_d_m":           30.0,
    "setback_hi":        48,      # floor of the upper set-back
    "core_w_m":          20.0,    # structural core plan
    "core_d_m":          17.0,
    "crown_h_m":         26.0,    # roof plant + crown above floor 60
    "slab_t_m":          0.32,    # structural slab thickness
    "gross_area_m2": 100000.0,    # gross floor area
    "occupants":       1640,      # design population (declines with height)
}
```

This dictionary defines the **whole-building envelope**. The tower is a 60-storey, 234 m commercial high-rise — not a supertall, just a normal buildable building. The plan dimensions step down twice (podium → mid → upper), which is standard high-rise massing. The structural core is 20 × 17 m and contains all hoistways, counterweight chases, the health stair, and the tray shuttle chases.

The `gross_area_m2` and `occupants` fields are used for the population model and the reference energy calculations.

### 2.2 Derived Constants

```python
FLOORS      = TOWER["floors"]           # 60
FLOOR_H     = TOWER["floor_h_m"]        # 3.90
TOWER_H_M   = FLOORS * FLOOR_H          # 234.0 m to the main roof
```

These are convenience scalars used everywhere downstream. `TOWER_H_M` is the single most-referenced dimension — it sets the vertical scale of the entire 3D model and the energy calculations.

### 2.3 The DIMS Dictionary

The `DIMS` dictionary (lines 110–169) contains the **individual subsystem dimensions**, all in metres and kilograms. Everything the TOWER and MACHINE views draw is positioned and sized from this dictionary. It is organized into groups:

**Hoistway and cabins:**
- `shaft_w_m` = 4.60 — One hoistway is wide enough to hold TWO counter-running cabins side by side
- `shaft_d_m` = 3.20 — Depth of the shaft
- `cabin_w_m` = 2.00 — Each cabin is 2 m wide
- `cabin_d_m` = 2.30 — 2.3 m deep
- `cabin_h_m` = 2.45 — 2.45 m interior height
- `cabin_gap_m` = 0.30 — 30 cm clearance between the paired cabins
- `car_door_w_m` = 1.10 — Door width
- `rail_face_m` = 0.16 — T-section guide-rail blade width (160 mm)
- `roller_d_m` = 0.16 — Roller guide-shoe wheel diameter (160 mm)
- `sheave_d_m` = 1.10 — Head traction sheave diameter (1.1 m, grooved)
- `sheave_t_m` = 0.22 — Sheave thickness
- `diverter_d_m` = 0.68 — Diverter/deflector sheaves in the head
- `block_d_m` = 0.52 — Differential-reeving movable block diameter
- `gov_sheave_d_m` = 0.42 — Overspeed governor sheave diameter
- `gov_rope_d_m` = 0.008 — Governor rope diameter (8 mm)
- `rope_d_m` = 0.013 — Traction rope diameter (13 mm)
- `ropes` = 6 — Six ropes per hoistway
- `rope_kg_per_m` = 0.72 — Steel rope linear mass (720 g/m)
- `buffer_d_m` = 0.30 — Oil buffer diameter in the pit
- `buffer_h_m` = 1.10 — Oil buffer height
- `brake_drum_d_m` = 0.62 — Band brake / ratchet-pawl holding drum diameter
- `brake_drum_t_m` = 0.18 — Brake drum thickness
- `pawl_len_m` = 0.45 — Holding pawl length

**Fixed base counterweight and variable tray mass:**
- `cwt_w_m` = 0.90 — Base counterweight frame width
- `cwt_d_m` = 0.42 — Base counterweight frame depth
- `cwt_h_m` = 2.10 — Base counterweight frame height
- `tray_w_m` = 0.42 — One modular weight tray width
- `tray_d_m` = 0.30 — Tray depth
- `tray_h_m` = 0.075 — Tray height (75 mm — flat and stackable)
- `tray_kg` = 11.34 — 25 lb, the ergonomic backpack/cart unit
- `tray_stack_max` = 26 — Maximum trays a cabin roof rack can hold

**Weight banks and sky-lobby vaults:**
- `bank_w_m` = 1.80 — Quick-load landing bank (tray hopper) width
- `bank_d_m` = 0.70 — Landing bank depth
- `bank_h_m` = 1.10 — Landing bank height
- `bank_capacity` = 120 — Trays per landing bank
- `vault_w_m` = 11.00 — Sky-lobby staged-mass vault width (a structural bay)
- `vault_d_m` = 7.00 — Vault depth
- `vault_h_m` = 3.40 — Vault height
- `vault_capacity` = 14000 — Trays per sky-lobby vault (~159 tonnes staged)
- `ground_reservoir` = 60000 — Ground-level tray store (at grade: no penalty)
- `lobby_extra_h_m` = 3.60 — Sky lobbies are double height

**The health stair:**
- `stair_w_m` = 3.00 — Generous, daylit, tray-cart friendly width
- `stair_d_m` = 6.40 — Stair depth
- `stair_run_m` = 2.90 — Horizontal run of one flight
- `flights_per_floor` = 2 — Two flights per storey (standard switchback)

**Short-haul weight shuttle:**
- `shuttle_w_m` = 1.40 — Narrow chase, pure-gravity tray shuttle
- `shuttle_d_m` = 1.40 — Shuttle depth
- `shuttle_car_h_m` = 1.60 — Shuttle car height
- `shuttle_trays` = 40 — Trays carried per shuttle run

### 2.4 Display Scaling Functions

The 3D engine works in "display units" — an arbitrary coordinate space that the renderer projects to screen pixels. Two scale factors map real metres to display units:

```python
TOWER_DISP = 1.0 / 300.0    # TOWER-view: 1 display unit ≈ 300 m
MACH_DISP  = 1.0 / 9.0      # MACHINE-view: 1 display unit ≈ 9 m
TOWER_Y0   = -0.42           # vertical centring offset for the tower view
```

The TOWER view needs to fit a 234 m building in the viewport, so it uses a 1:300 scale. The MACHINE view shows a single zone's internals (~12 m tall), so it uses a 1:9 scale for more detail.

Three helper functions convert metres to display coordinates:

- `tds(m)` — metres → TOWER-view display units (horizontal/depth)
- `ty(m)` — metres above street level → TOWER-view display Y (includes the `TOWER_Y0` offset so the building sits centered in the viewport)
- `mds(m)` — metres → MACHINE-view display units

### 2.5 The ZONE_PLAN

```python
ZONE_PLAN = [
    (1,  11, 3, 16, 1, 900.0),   # Zone 1: floors 1-11,  3 hoistways, 16 pax, 1:1 reeving, 900 kg
    (11, 21, 3, 16, 1, 900.0),   # Zone 2: floors 11-21, 3 hoistways, 16 pax, 1:1 reeving, 900 kg
    (21, 31, 2, 13, 1, 820.0),   # Zone 3: floors 21-31, 2 hoistways, 13 pax, 1:1 reeving, 820 kg
    (31, 41, 2, 13, 1, 820.0),   # Zone 4: floors 31-41, 2 hoistways, 13 pax, 1:1 reeving, 820 kg
    (41, 51, 2, 10, 2, 700.0),   # Zone 5: floors 41-51, 2 hoistways, 10 pax, 2:1 reeving, 700 kg
    (51, 60, 2,  8, 2, 620.0),   # Zone 6: floors 51-60, 2 hoistways,  8 pax, 2:1 reeving, 620 kg
]
```

Each tuple is `(floor_lo, floor_hi, n_shafts, cabin_capacity, reeving_MA, cabin_mass_kg)`.

This is **traffic-aware sizing**: lower zones carry the heavy commuter load, so they get more hoistways, bigger cabins, and direct 1:1 roping for speed. Upper zones are sparse, so they get fewer, smaller cabins on differential 2:1 reeving, which halves the weight imbalance a run needs at the cost of half the car speed.

The zones **stack**: zone 1's top floor (11) is zone 2's bottom floor. Sky lobbies sit at these overlap points. No hoistway runs the full height — that is why a 60-storey tower needs only 14 shafts instead of the ~24 that conventional full-rise zoning would require.

### 2.6 Physical Constants

```python
G              = 9.80665      # m/s^2, standard gravity
TRAY_KG        = DIMS["tray_kg"]   # 11.34 kg
PAX_KG         = 75.0         # design passenger mass
BODY_KG        = 75.0         # design walker body mass (for stair metabolic work)
```

`PAX_KG` is the mass used for elevator passengers. `BODY_KG` is the mass used for the metabolic cost calculation when someone climbs the stair — it includes the walker's own body mass plus the trays they are carrying.

### 2.7 Mechanical Loss Constants

```python
MU_EFF         = 0.028        # effective resistance coefficient (fraction of W)
MU_SPEC_LO     = 0.030        # published imbalance band, low  (3%)
MU_SPEC_HI     = 0.080        # published imbalance band, high (8%)
IMBAL_MARGIN   = 2.05         # imbalance commanded over the pure friction floor
                              # → 5.7% of suspended mass, inside the 3-8% band
BATCH_HOLD_S   = 14.0         # collect window before a run is released
REPOSITION_S   = 20.0         # wait before an empty car is sent to a call
ROT_INERTIA_FR = 0.11         # sheave/rope rotating inertia as a fraction of M
RECOVERY_EFF   = 0.86         # descending surplus -> re-staged tray height
ROPE_SPEED_MS  = 2.60         # rope speed cap (car speed = this / reeving MA)
ACCEL_CAP_MS2  = 0.95         # comfort limit on car acceleration
JERK_DWELL_S   = 1.6          # levelling + door pre/post time per stop
DOOR_DWELL_S   = 3.4          # nominal door-open dwell
BOARD_S_PER_PAX = 1.05        # extra dwell per boarding/alighting passenger
```

**`MU_EFF`** is the single most important constant in the entire model. It lumps together roller-guide rolling resistance, sheave bearing drag, rope bending stiffness, and door/seal drag into one honest coefficient. Roller guides on machined rails plus well-lubricated grooved sheaves land near 0.028 (2.8%). This is the number the whole design lives or dies on — if friction were higher, the required imbalance would exceed the 3–8% band and the system would need more human-carried mass than is practical.

**`IMBAL_MARGIN`** multiplies the friction floor to get the commanded imbalance. At 2.05 × 0.028 = 0.0574, the commanded imbalance is 5.74% of the suspended mass — comfortably inside the 3–8% specification band.

**`RECOVERY_EFF`** = 0.86 means that when a descending car is heavier than it needs to be, 86% of the excess potential energy is recovered by lifting trays back up into the vault, rather than being wasted in a brake.

**`ROPE_SPEED_MS`** = 2.60 m/s is the rope speed cap. For 1:1 reeving, the car speed equals the rope speed. For 2:1 reeving, the car speed is halved to 1.30 m/s (the rope moves twice as fast as the car, but the force is doubled).

**`ACCEL_CAP_MS2`** = 0.95 m/s² is the comfort limit. Elevator standards typically cap acceleration at 1.5–2.0 m/s² for motor-driven cars, but gravity-driven cars cannot control their acceleration as precisely, so a lower cap is used.

### 2.8 Token Economy Parameters

```python
TOKEN = {
    "base_per_tray_flight": 1.00,   # tokens per tray per floor climbed
    "height_gain":          0.85,   # extra multiplier at the top of the tower
    "scarcity_gain":        2.60,   # extra multiplier when a vault is empty
    "scarcity_floor":       0.55,   # vault fraction at/above which no bonus
    "priority_reserve":     0.06,   # share of slots kept free for incapacity
}
```

The token economy is a **self-balancing incentive gradient**:

- **Base rate**: 1 token per tray per floor climbed. Carry 2.2 trays up 10 floors = 22 tokens.
- **Height gain**: Up to +85% at the top of the tower. A tray staged at the roof vault is worth more joules than one staged at the ground, so the credit rate rises with the height of the deposit.
- **Scarcity gain**: Up to +260% when a vault falls below 55% full. When an upper vault runs low, the multiplier spikes, pulling carriers exactly where they are needed.
- **Priority reserve**: 6% of slots are kept free for genuine incapacity and jump the queue.

The multiplier formula (implemented in `ZoneState.multiplier()`) is:

```
multiplier = 1.0 + height_gain × (lobby_height / tower_height) + scarcity_gain × max(0, (scarcity_floor - vault_fraction) / scarcity_floor)
```

### 2.9 Walker Model

```python
WALK = {
    "base_rate_per_100":  2.10,   # climbs per 100 zone occupants per minute
    "incentive_gain":     1.60,   # extra climbs when the multiplier is high
    "trays_per_carry":    2.2,    # 2.2 × 11.34 kg = 25 kg in a stair cart
    "climb_speed_fl_s":   0.16,   # floors climbed per second (loaded)
    "metabolic_eff":      0.23,   # mechanical work / metabolic energy
    "kcal_per_kj":        0.239,  # conversion factor
}
```

Not everyone climbs — the fraction that does responds to the live token multiplier. The base rate is 2.10 climbs per 100 zone occupants per minute, which increases by up to 160% when the multiplier is high.

Each carry is 2.2 trays (25 kg in a stair cart). The climb speed is 0.16 floors per second (about 6.25 seconds per floor when loaded), which is a brisk but sustainable stair-climbing pace.

The metabolic efficiency of 23% means that for every joule of mechanical work done (lifting mass against gravity), the body actually consumes about 4.35 joules of metabolic energy. The rest is lost as heat. This is why the kilocalorie figures are much larger than the stored energy figures.

### 2.10 Traffic Profile

```python
TRAFFIC = {
    "am_peak_h":   8.30, "am_sigma_h": 1.10, "am_amp":  9.00,
    "lunch_h":    12.50, "lunch_sigma": 0.80, "lunch_amp": 5.80,
    "pm_peak_h":  17.80, "pm_sigma_h": 1.30, "pm_amp":   7.60,
    "inter_amp":   3.00, "inter_start": 7.0, "inter_end": 19.0,
    "queue_cap":    420,          # per-zone hall queue before riders balk
}
```

Person-trips per minute for the whole building are modeled as **sums of Gaussians** over the 24-hour clock:

- A sharp **morning up-peak** centered at 8:30 AM (σ = 1.1 h, amplitude = 9.0 trips/min)
- A **two-way lunch period** centered at 12:30 PM (σ = 0.8 h, amplitude = 5.8 trips/min)
- A broad **evening down-peak** centered at 5:48 PM (σ = 1.3 h, amplitude = 7.6 trips/min)
- A flat **interfloor background** of 3.0 trips/min during 7:00 AM – 7:00 PM, dropping to 0.25 outside that window

The `queue_cap` of 420 is the per-zone hall queue limit. If a zone's queue exceeds this, riders start balking — they take the stairs instead (and may carry a tray while doing so, earning tokens).

### 2.11 Reference Energy Figures

```python
REFERENCE = {
    "kwh_per_trip":   0.055,      # typical traction-lift energy per passenger trip
    "standby_kw":     1.10,       # per lift standby/controller draw
    "lifts":          14,
    "tariff_usd_kwh": 0.16,
    "co2_kg_kwh":     0.37,
}
```

These figures represent what a **conventional geared/gearless lift bank** would have drawn for the same work. They are used purely as the honest reference for the "0 kWh" claim and for pricing the token economy in real dollars.

- `kwh_per_trip` = 0.055 kWh is a typical figure for a traction elevator serving a mid-rise to high-rise zone.
- `standby_kw` = 1.10 kW per lift is the controller/standby draw that a conventional lift bank consumes even when idle.
- `tariff_usd_kwh` = $0.16/kWh is a typical US commercial electricity tariff.
- `co2_kg_kwh` = 0.37 kg CO₂/kWh is the US grid average emissions factor.

### 2.12 Economy Pricing

```python
ECONOMY = {
    "walker_payout_frac": 1.00,
}
```

`walker_payout_frac = 1.0` means 100% of the avoided electricity bill is passed straight through to walkers as token value. This is the **honest upper bound** — it assumes the building keeps none of the saving for itself. Lower this fraction if the building should also bank some of the saving.

The walker pool in dollars is:

```
walker_pool_usd = avoided_kwh × tariff × walker_payout_frac
```

And the value per token is:

```
usd_per_token = walker_pool_usd / total_tokens_issued
```

### 2.13 Global Scale Estimates

```python
GLOBAL = {
    "elevators_world":  20_000_000,   # installed elevator units worldwide
    "twh_year":         300.0,        # TWh/year global lift electricity consumption
    "avg_kwh_per_lift": 15_000,       # kWh per elevator per year (global average)
}
```

These figures are **conservative mid-points from industry sources** used to estimate what the savings would be if the gravity-transit principle replaced every traction and hydraulic lift on the planet:

- **`elevators_world`** = 20 million — The commonly cited figure for installed elevator units worldwide (Elevator World, IAEC estimates). This includes everything from single-stop hydraulic units in two-storey buildings to high-rise traction banks in supertalls.

- **`twh_year`** = 300 TWh — Global elevator electricity consumption per year, approximately 1% of world electricity production. Some sources cite up to 400 TWh; 300 is conservative.

- **`avg_kwh_per_lift`** = 15,000 kWh — Average energy per elevator per year. Most of the world's elevators are low-rise, low-traffic units in residential and small commercial buildings that consume far less than the model tower's high-rise traction lifts. The model tower's 14 lifts avoid ~267,000 kWh/year (~19,000 kWh per lift), well above the global average because they serve a 60-storey building with heavy commuter traffic.

**Global savings if all elevators were replaced:**

| Metric | Calculation | Value |
|---|---|---|
| Avoided electricity | 300 TWh/year | 300,000,000,000 kWh/year |
| Avoided cost | 300 TWh × $0.16/kWh | ~$48 billion/year |
| Avoided CO₂ | 300 TWh × 0.37 kg/kWh | ~111 million tonnes/year |
| Equivalent cars off road | 111 Mt ÷ 4.6 t/car-year | ~24 million cars |
| Equivalent nuclear reactors | 300 TWh ÷ 8.76 TWh/GW-year | ~34 GW ≈ 34 reactors |
| Equivalent coal plants | 300 TWh ÷ 4.38 TWh/500MW-year | ~68 plants |

The info panel in the program (press **I**) presents these figures in the "5. THE MONEY" section, and the DAY HUD shows a compact summary in the statistics panel.

---

## 3. Section 2 — Colors and Theme

Lines 290–335 define every color used in the UI as a flat list of RGB tuples. They are organized by subsystem:

- **Building structure**: `C_CONCRETE`, `C_SLAB`, `C_PODIUM`, `C_GLASS`, `C_GLASS_HI`, `C_MULLION`, `C_CROWN`, `C_GROUND`
- **Transit system**: `C_SHAFT`, `C_CABIN`, `C_CABIN_B`, `C_CWT`, `C_TRAY`, `C_TRAY_LOW`, `C_BANK`, `C_VAULT`, `C_STAIR`, `C_SHUTTLE`
- **Mechanical parts**: `C_ROPE`, `C_SHEAVE`, `C_STEEL`, `C_RAIL`, `C_BRAKE`
- **UI**: `C_TEXT`, `C_TEXT_DIM`, `C_ACCENT`, `C_GOOD`, `C_WARN`, `C_BAD`, `C_GRAV`, `C_PANEL`, `C_PANEL_HI`
- **Sky**: `C_SKY_DAY1`, `C_SKY_DAY2`, `C_SKY_NIGHT1`, `C_SKY_NIGHT2`, `C_SUN`, `C_CITY`
- **Background**: `BG_TOP`, `BG_BOT`

The color scheme is a dark technical theme: deep navy backgrounds, warm gold for cabins, cool blue for the counter-running twin, green for trays (the human-carried currency), orange for the health stair, purple for shuttles, and a gravity-green accent (`C_GRAV`) for the "free energy" claims.

---

## 4. Section 3 — The Mini 3D Engine

Lines 337–534 implement a **self-contained software 3D renderer** built on pygame's 2D drawing primitives. It knows nothing about elevators — it is a geometry-agnostic toolkit that can render any collection of `Part` objects.

### 4.1 Rotation Matrices

Three functions return 3×3 rotation matrices as numpy arrays:

- `rot_x(a)` — Rotation about the X axis
- `rot_y(a)` — Rotation about the Y axis (used for camera azimuth)
- `rot_z(a)` — Rotation about the Z axis (used for mesh spin)

Each returns a standard rotation matrix. For example, `rot_y(a)` returns:

```
[[ cos(a),  0,  sin(a)],
 [      0,  1,       0],
 [-sin(a),  0,  cos(a)]]
```

These are used in two places:
1. The camera transformation (`Rcam = rot_x(el) @ rot_y(az)`) — rotates the world to simulate camera orbit.
2. Mesh spinning (`v @ rot_z(angle * spin).T`) — rotates sheaves and governor sheaves about their axis.

### 4.2 Utility Functions

- `clamp(x, lo=0.0, hi=1.0)` — Clamps a value to a range. Used everywhere for fractions, blend amounts, and acceleration caps.
- `_mix(c1, c2, t)` — Linear interpolation between two RGB colors. Used for color blending (e.g., vault stock going from green to red as it depletes, sky transitioning from night to day).

### 4.3 The Mesh Class

```python
class Mesh:
    def __init__(self, verts, faces, color, name="", spin=0.0, group="default",
                 pivot=(0.0, 0.0, 0.0), tilt=(0.0, 0.0), selectable=False):
```

A `Mesh` is a bag of vertices (numpy array of N×3) and polygon faces (list of tuples of vertex indices) with a base color. Key attributes:

- **`verts`** — N×3 numpy array of vertex coordinates in display units
- **`faces`** — List of tuples, each containing indices into `verts` (typically 4 vertices per face for quads, 3 for triangles)
- **`color`** — Base RGB tuple
- **`name`** — Optional label string (shown in exploded/assembly views)
- **`spin`** — Rotation ratio against the master angle of its `group`. 0 = static, 1 = spins with the group angle. Used for sheaves.
- **`group`** — Name of the animation group this mesh belongs to (e.g., `"sheave"`, `"gov"`, `"static"`). The renderer looks up the group's current angle and applies it.
- **`pivot`** — 3D offset for the local origin. Used to place spinners (sheaves built at the origin) at their correct position in the assembly.
- **`tilt`** — Static (rx, ry) rotation for off-axis spinners. Some sheaves are tilted to face a different direction.
- **`dyn`** — A LIVE 3D translation (numpy zeros(3)) that the simulation writes every frame. This is how cabins move without rebuilding geometry: the mesh is built once at the zone floor, and `dyn[1]` (the Y component) is updated each frame to reflect the cabin's current height.
- **`mix_col`** / **`mix_t`** — A LIVE color blend. `mix_col` is the target color, `mix_t` is the blend amount (0 = base color, 1 = fully mixed). Used for vault stock (green when full, red when empty) and tray racks (green when loaded, shaft-colored when empty).
- **`hidden`** — If True, the mesh is skipped during rendering. (Not heavily used in the current code.)

The `world_verts(angle)` method computes the final world-space vertex positions by applying spin rotation, tilt rotation, pivot offset, and the live `dyn` translation:

```python
def world_verts(self, angle=0.0):
    v = self.verts
    if self.spin:
        v = v @ rot_z(angle * self.spin).T
    rx, ry = self.tilt
    if rx or ry:
        v = v @ (rot_x(rx) @ rot_y(ry)).T
    return v + self.pivot + self.dyn
```

The `shade_color()` method returns the base color, or a blend with `mix_col` if `mix_t` is significant:

```python
def shade_color(self):
    if self.mix_col is not None and self.mix_t > 0.001:
        return _mix(self.color, self.mix_col, clamp(self.mix_t))
    return self.color
```

### 4.4 Primitive Builders

These functions return (vertices, faces) tuples that are then wrapped in `Mesh` objects:

- **`_box(cx, cy, cz, sx, sy, sz)`** — An axis-aligned box centered at (cx, cy, cz) with dimensions (sx, sy, sz). Returns 8 vertices and 6 quad faces. This is the workhorse primitive — most of the tower is built from boxes.

- **`_solid_cylinder(r, z0, z1, seg=28)`** — A solid cylinder of radius `r` from z0 to z1, with `seg` segments around the circumference. Includes end caps. Used for rollers, buffers, sheave shafts.

- **`_annulus_cylinder(r_out, r_in, z0, z1, seg=30)`** — A hollow ring (annulus) closed at both axial ends. Used for sheave rims and rope grooves — the grooved traction sheave is an annulus, not a solid cylinder.

- **`_pipe(p0, p1, r, col, seg=6, name="")`** — A straight round rod between two 3D points. Used for ropes, rails, struts, and the roof mast. It constructs a local coordinate frame from the pipe's axis and builds a tube of `seg` sides.

- **`remap_yz(v)`** — Swaps Y and Z coordinates: `(x, y, z) → (x, z, y)`. This rotates a Z-axis primitive (built with `_solid_cylinder` or `_annulus_cylinder`) so its long axis points UP (+Y), which is the "up" direction in the renderer's world space.

- **`_static(v, f, col, name, group)`** — Wraps vertices and faces into a non-spinning `Mesh` with `spin=0.0`. Most of the tower's parts are static.

- **`_spinner(v, f, col, pivot, tilt, group, name)`** — Wraps vertices and faces into a spinning `Mesh` with `spin=1.0`, placed at `pivot` with optional `tilt`. Used for sheaves and governor sheaves.

### 4.5 The Part Class

```python
class Part:
    def __init__(self, key, name, meshes, specs, order, explode, color):
```

A `Part` is a named, spec'd logical component made of one or more `Mesh` objects. Key attributes:

- **`key`** — Short identifier (e.g., `"slabs"`, `"cabA"`, `"head"`)
- **`name`** — Display name (e.g., `"FLOOR PLATES (60 storeys)"`, `"CABIN A (ascending car)"`)
- **`meshes`** — List of `Mesh` objects that make up this part
- **`specs`** — List of human-readable specification strings shown in the inspector panel when this part is hovered or pinned
- **`order`** — Assembly order (integer). In assembly view, parts appear one at a time in this order.
- **`explode`** — 3D offset vector for the exploded view. When the exploded view is active, each part is translated by `explode × explode_amt`.
- **`color`** — Representative color (used for the part list sidebar)
- **`popdir`** — Normalized direction of the explode offset (computed in `__init__`). Used for the hover "pop" effect — when you hover a part, it moves slightly toward you.

### 4.6 Group Helper

```python
def _grp(meshes, group):
    for m in meshes:
        m.group = group
    return meshes
```

Sets the animation group on a list of meshes. Not heavily used in the current code but available for grouping related spinners.

---

## 5. Section 4 — Zone Plan and Geometry Builders

Lines 536–1217. This section takes the dimensional constants from Section 1 and turns them into `Part` objects that the renderer can draw.

### 5.1 The ZoneSpec Class

```python
class ZoneSpec:
    def __init__(self, index, lo, hi, n_shafts, cap, reeving, cabin_kg):
```

`ZoneSpec` is the fixed, dimensional description of one vertical zone. Both the 3D geometry and the transit physics are generated from these numbers. Key computed attributes:

- **`n_floors`** = `hi - lo + 1` — Number of floors served
- **`rise_m`** = `(hi - lo) × FLOOR_H` — Vertical rise of this zone in metres
- **`base_h_m`** = `(lo - 1) × FLOOR_H` — Height of the zone's base above street level
- **`top_h_m`** = `(hi - 1) × FLOOR_H` — Height of the zone's top above street level
- **`tray_J`** = `TRAY_KG × G × rise_m` — Joules of potential energy stored per staged tray. This is the energy one tray holds by virtue of being at the top of the zone instead of the bottom.
- **`v_max`** = `ROPE_SPEED_MS / reeving` — Car speed cap. For 1:1 reeving, this is 2.60 m/s. For 2:1 reeving, this is 1.30 m/s.
- **`rope_kg`** = `ropes × rope_kg_per_m × rise_m × 2.2` — Total rope mass per hoistway. The factor 2.2 accounts for both rope falls plus some extra for compensation.

The `suspended_kg()` method computes the total mass hanging on the head sheave:

```python
def suspended_kg(self, load_a=0.0, load_b=0.0, trays=0.0):
    return (2.0 * self.cabin_kg + load_a + load_b
            + trays * TRAY_KG + self.rope_kg + self.base_cwt_kg())
```

This includes both cabin masses, both passenger loads, tray mass, rope mass, and the fixed base counterweight. This is the mass that friction acts on.

The `base_cwt_kg()` method sizes the fixed base counterweight:

```python
def base_cwt_kg(self):
    return 0.45 * self.cap * PAX_KG
```

This is 45% of the maximum passenger load (capacity × 75 kg per passenger). It is sized for the **average** zone load, not the maximum — only the variable add-on tray mass is ever carried by people.

### 5.2 Zone Instances and Sky Lobbies

```python
ZONES = [ZoneSpec(i, *row) for i, row in enumerate(ZONE_PLAN)]
NZONES = len(ZONES)                          # 6
SKY_LOBBIES = [z.lo for z in ZONES] + [ZONES[-1].hi]  # [1, 11, 21, 31, 41, 51, 60]
LOBBY_H_M = [(f - 1) * FLOOR_H for f in SKY_LOBBIES]  # heights of each lobby above street
TOTAL_SHAFTS = sum(z.n_shafts for z in ZONES)          # 14
```

`SKY_LOBBIES` lists the floor numbers of every sky lobby, including the ground (floor 1) and the roof (floor 60). There are 7 lobby levels (level 0 = ground, level 6 = roof), and 5 intermediate sky lobbies (floors 11, 21, 31, 41, 51).

`LOBBY_H_M` gives the height in metres of each lobby above street level. This is used for energy calculations (the potential energy of a tray at a given lobby height).

### 5.3 Population Model

```python
def floor_population(f):
    t = (f - 1) / max(1.0, FLOORS - 1.0)
    return max(6.0, 46.0 * math.exp(-1.15 * t))
```

Occupancy **falls exponentially with height**. Floor 1 has ~46 occupants; floor 60 has ~6. The parameter `1.15` controls the decay rate. This is the reason upper zones need incentives — fewer people are there to carry trays.

```python
def zone_population(z):
    return sum(floor_population(f) for f in range(z.lo, z.hi))
```

Sums the per-floor population across a zone's floors. This is used to compute the walker climb rate (more people = more potential climbers).

### 5.4 Vault Capacity

```python
def vault_cap(level):
    return DIMS["ground_reservoir"] if level == 0 else DIMS["vault_capacity"]
```

Level 0 (ground) has a 60,000-tray reservoir because it is at grade — no structural penalty. All other levels have 14,000-tray vaults (~159 tonnes each), limited by the floor loading capacity of a structural bay.

### 5.5 Travel Planning Functions

**`zone_for_travel(f, going_up)`** — Returns the `ZoneSpec` that serves a trip starting at floor `f` in the given direction. Sky-lobby floors belong to two zones; the function picks the one that reaches onward in the desired direction.

**`plan_legs(src, dst)`** — Breaks a journey from `src` to `dst` into per-zone legs via the sky lobbies. This is the **cascade**: a trip from floor 5 to floor 55 becomes:

1. Zone 1: floor 5 → floor 11 (sky lobby)
2. Zone 2: floor 11 → floor 21 (sky lobby)
3. Zone 3: floor 21 → floor 31 (sky lobby)
4. Zone 4: floor 31 → floor 41 (sky lobby)
5. Zone 5: floor 41 → floor 51 (sky lobby)
6. Zone 6: floor 51 → floor 55

Each leg is served by one zone's hoistways. The rider transfers at each sky lobby. This is why cross-tower trips take longer — but no walker ever hauls mass past the next sky lobby.

The function uses a guard counter (max 12 iterations) to prevent infinite loops in edge cases.

### 5.6 Massing and Shaft Layout

**`massing_plan(height_m)`** — Returns the plan dimensions (width, depth) of the tower shell at a given height. Below the podium (4 floors): 52 × 46 m. Below the upper set-back (floor 48): 42 × 38 m. Above: 34 × 30 m.

**`shaft_x_m(n, i)`** — Returns the plan X position of hoistway `i` of `n` inside the core. For 3 hoistways, they are spread across 13.8 m; for 2, across 9.8 m.

Several module-level constants define the Z positions of subsystems within the core:

```python
SHAFT_Z_M   = 2.40      # hoistways sit in the front half of the core
CWT_Z_M     = -1.60     # base-counterweight chases behind them
SHUTTLE_X_M = -9.20     # short-haul tray shuttle chase
SHUTTLE_Z_M = -5.60
STAIR_X_M   = 8.80      # the health stair
STAIR_Z_M   = -5.40
BANK_Z_M    = 6.40      # landing weight banks, in the lift lobby
VAULT_Z_M   = -6.90     # sky-lobby staged-mass vaults
```

### 5.7 The TOWER_LIVE Registry

```python
TOWER_LIVE = {"cabA": {}, "cabB": {}, "cwt": {}, "trayA": {}, "trayB": {},
              "bank": {}, "vault": {}, "shuttle": {}}
```

This is a dictionary of dictionaries that holds **references to the live meshes**. When `build_tower_parts()` creates a cabin mesh, it stores a reference in `TOWER_LIVE["cabA"][(zone_index, shaft_index)]`. Later, `sync_live()` can write `mesh.dyn[1]` to move the cabin without rebuilding any geometry.

This is the key design pattern that makes the simulation efficient: geometry is built once, and live state is written onto the existing meshes every frame.

### 5.8 build_tower_parts() — The Whole Building

This function (lines 680–938) constructs the entire 234 m tower as a list of `Part` objects. It is called once at startup and the parts are reused for the lifetime of the program.

The parts are built in this order:

1. **GROUND / PLAZA / CITY CONTEXT** — A street-level ground plane and four neighboring building blocks (drawn to scale for reference).

2. **FLOOR PLATES** — One structural slab per storey (60 slabs). Sky-lobby floors are highlighted with a warm gold color and have thicker slabs (2.4× normal). The slabs step down in plan dimensions at the podium/mid/upper transitions.

3. **CURTAIN WALL + SET-BACKS** — Two faces of the tower (W and N) are drawn as glass curtain walls with mullion corner columns. The other two faces are left open as a cutaway so the transit core is visible. Three vertical blocks correspond to the podium, mid, and upper sections.

4. **STRUCTURAL CORE** — Four corner piers and a shear wall, forming the 20 × 17 m core that contains all hoistways, counterweight chases, the stair, and the shuttle chases.

5. **HOISTWAYS + LIVE COUNTER-RUNNING CABINS** — For each zone, for each shaft:
   - A hoistway enclosure spanning exactly that zone's height
   - A machine head (sheave beam housing) at the zone top
   - Two counter-running cabins (A and B) built at the zone floor, registered in `TOWER_LIVE`
   - A roof tray rack on each cabin (for the variable add-on mass), registered in `TOWER_LIVE`
   - A fixed base counterweight in its own chase, registered in `TOWER_LIVE`

6. **LANDING WEIGHT BANKS** — One quick-load tray hopper at every landing (60 banks), alternating left/right sides of the lobby. Registered in `TOWER_LIVE`.

7. **SKY-LOBBY VAULTS** — One staged-mass vault at each lobby level (7 vaults). Registered in `TOWER_LIVE`.

8. **THE HEALTH STAIR** — A stair shaft with individual stair flights, drawn at ±30° angles to create a switchback pattern. Two flights per floor.

9. **SHORT-HAUL TRAY SHUTTLES** — One narrow chase per zone with a shuttle car. Registered in `TOWER_LIVE`.

10. **ROOF PLANT + CROWN** — Three stepped roof blocks and a mast. No machine room — the head sheaves sit at each zone top, not the roof.

After all parts are built, the explode vectors are scaled down (×0.30) because the tower is only ~0.78 display units tall, and raw explode vectors would throw parts off the viewport.

### 5.9 build_machine_parts() — One Zone's Gravity Machine

This function (lines 951–1217) constructs a detailed mechanical view of one zone's hoistway, using the upper zone's specifications (2:1 reeving). It is also called once at startup.

The parts are built in this order:

1. **PIT + OIL BUFFERS** — Pit slab and two oil buffers (one under each car). The pit is also the low tray landing for this zone.

2. **GUIDE RAILS + ROLLER SHOES** — T-section guide rails (4 per car: 2 on each side) and roller guide shoes (8 per car: 4 corners × 2 sides). The rollers are built as small cylinders tilted to face the right direction.

3. **CABIN A (ascending car)** — Cabin shell, platform/sling, crosshead, two doors, upper/lower frame bars, and a roof tray rack with 4 visible tray layers.

4. **CABIN B (descending car)** — Identical to cabin A, positioned on the other rope fall.

5. **HEAD SHEAVE ASSEMBLY** — Head beam, grooved traction sheave (annulus cylinder with 3 rope groove rings), sheave shaft, and two diverter sheaves.

6. **DIFFERENTIAL REEVING BLOCKS (2:1)** — Two movable reeving blocks on the car side, a block frame, and a dead-end hitch. This is what gives the upper zones their 2:1 mechanical advantage.

7. **TRACTION ROPES** — Three visible rope falls (of the 6 actual ropes), each running from car A's reeving block up over the head sheave and down to car B.

8. **BASE COUNTERWEIGHT + TRAYS** — The fixed counterweight frame with 9 visible stacked weight trays and a cwt hitch.

9. **OVERSPEED GOVERNOR + SAFETY GEAR** — Governor sheave, tension sheave, governor ropes, safety-gear trip, and wedge safety gear. This is purely mechanical — flyweights, no electronics.

10. **HOLDING BRAKE + RATCHET PAWL** — Brake drum with 12 ratchet teeth, holding pawl, pawl pivot, and band brake anchor. This is the ONLY powered actuator in the machine — and it is a latch, not a motor. Fail-safe: springs apply, nothing holds it off.

11. **LANDING BANK + CALL REGISTER** — Landing weight bank with 6 visible deposited trays, a registration post, a call/credit register, and a tray cart run.

After all parts are built, the explode vectors are scaled down (×0.26) to fit the viewport.

---

## 6. Section 5 — Gravity Transit Physics

Lines 1220–1303. This section contains **pure functions** that compute the physics of the gravity transit system. They take numbers in, return numbers out, and have no side effects or state.

### 6.1 resist_force_N()

```python
def resist_force_N(m_susp_kg):
    return MU_EFF * m_susp_kg * G
```

Total rolling/bearing/rope resistance referred to the rope, in newtons. This is the force that the weight imbalance must overcome for the system to move. It is simply the effective friction coefficient times the suspended mass times gravity.

For a typical zone-1 hoistway with ~4,000 kg suspended mass, the resistance is about 0.028 × 4,000 × 9.80665 ≈ 1,098 N (about 112 kgf).

### 6.2 required_advantage_kg()

```python
def required_advantage_kg(m_susp_kg, reeving):
    return IMBAL_MARGIN * MU_EFF * m_susp_kg / reeving
```

The mass advantage the descending side must hold for the run to go. This is the friction floor times a working margin, divided by the reeving ratio. Differential 2:1 reeving halves the mass a run needs.

For the same ~4,000 kg suspended mass with 1:1 reeving: 2.05 × 0.028 × 4,000 / 1 = 229.6 kg. The descending side must be ~230 kg heavier than the ascending side.

With 2:1 reeving: 229.6 / 2 = 114.8 kg. Only ~115 kg of advantage is needed — but the car speed is also halved.

### 6.3 tray_mass_needed_kg()

```python
def tray_mass_needed_kg(m_susp_kg, reeving, net_advantage_kg):
    return max(0.0, required_advantage_kg(m_susp_kg, reeving) - net_advantage_kg)
```

Tray mass to pre-position on the descending side. `net_advantage_kg` is the mass difference between the descending car's load and the ascending car's load. When a loaded car is already going down against a light one, `net_advantage_kg` is positive and the run may need **no trays at all** — it makes them instead.

### 6.4 imbalance_ratio()

```python
def imbalance_ratio(delta_kg, m_susp_kg):
    return abs(delta_kg) / max(1.0, m_susp_kg)
```

The headline number: commanded imbalance as a fraction of hanging mass. The design target is 3–8%. At 5.7%, the system is comfortably within the band.

### 6.5 car_accel_ms2()

```python
def car_accel_ms2(delta_kg, m_susp_kg, reeving):
    f_net = delta_kg * reeving * G - resist_force_N(m_susp_kg)
    a = f_net / max(1.0, m_susp_kg * (1.0 + ROT_INERTIA_FR))
    return clamp(a, 0.0, ACCEL_CAP_MS2)
```

Car acceleration from a commanded imbalance. The net force is the weight difference (× reeving for mechanical advantage) minus friction. This is divided by the effective mass (suspended mass × (1 + rotating inertia fraction)) to get acceleration, which is then capped at 0.95 m/s² for comfort.

The rotating inertia fraction (`ROT_INERTIA_FR = 0.11`) accounts for the sheave and rope inertia — about 11% of the suspended mass is "extra" inertia that must be accelerated.

### 6.6 run_time_s()

```python
def run_time_s(dist_m, a_ms2, v_max):
```

Computes the **trapezoidal travel profile**: accelerate to v_max, cruise, decelerate to stop. If the distance is too short to reach v_max, the profile is triangular (accelerate then immediately decelerate). A levelling dwell (`JERK_DWELL_S = 1.6 s`) is added to every run.

The function handles three cases:
1. **Zero distance**: returns just the levelling dwell.
2. **Triangular profile** (never reaches v_max): `2 × sqrt(dist / a) + dwell`.
3. **Trapezoidal profile** (reaches v_max): `2 × (v_max / a) + (dist - 2 × d_acc) / v_max + dwell`.

### 6.7 run_energy_J()

```python
def run_energy_J(load_up_kg, load_dn_kg, m_susp_kg, ds_m):
    return (load_up_kg - load_dn_kg) * G * abs(ds_m) + MU_EFF * m_susp_kg * G * abs(ds_m)
```

Net energy the staged mass must supply for one segment, in joules. Positive = drawn from the vault above. Negative = surplus, re-stages trays upward at `RECOVERY_EFF`.

The first term is the net lift work (up load minus down load × g × distance). The second term is the friction loss. When up and down loads are equal, the first term is zero and only friction is consumed — this is the balanced case where counter-running pairs shine.

### 6.8 tray_units()

```python
def tray_units(n_trays, ds_m, rise_m):
    return n_trays * (abs(ds_m) / max(1e-6, rise_m))
```

Converts a number of trays moved through a partial distance into "vault units" — whole-zone equivalents. If 5 trays move through half the zone rise, that's 2.5 vault units. This is how the vault plumbing tracks partial movements.

### 6.9 metabolic_kj()

```python
def metabolic_kj(mass_kg, rise_m):
    return mass_kg * G * rise_m / WALK["metabolic_eff"] / 1000.0
```

Metabolic energy a walker actually spends lifting `mass_kg` through `rise_m`, in kilojoules. The mechanical work is `mass × g × rise`, but the body only converts 23% of metabolic energy to mechanical work, so the metabolic cost is ~4.35× the mechanical work.

The `mass_kg` includes both the walker's body mass (`BODY_KG = 75 kg`) and the trays they are carrying. Climbing stairs with 25 kg of trays burns significantly more calories than climbing empty.

### 6.10 stair_climb_time_s()

```python
def stair_climb_time_s(floors):
    return floors / WALK["climb_speed_fl_s"]
```

Time to climb `floors` flights at the loaded climb speed of 0.16 floors/second. This is about 6.25 seconds per floor — a brisk but sustainable pace.

### 6.11 reference_grid_kwh()

```python
def reference_grid_kwh(trips, lift_hours):
    return (trips * REFERENCE["kwh_per_trip"]
            + lift_hours * REFERENCE["lifts"] * REFERENCE["standby_kw"])
```

What a conventional traction lift bank would have drawn for the same work. This is the honest reference for the "0 kWh" claim and for pricing the token economy. It includes both the per-trip energy and the standby draw (controllers, lighting, ventilation running 24/7).

---

## 7. Section 6 — The Building (Live Simulation)

Lines 1305–2016. This is the heart of the program — the live simulation that models the building's operation over a 24-hour day.

### 7.1 The Journey Class

```python
class Journey:
    __slots__ = ("src", "dst", "legs", "leg_i", "t_reg", "t_leg_reg", "cur",
                 "priority", "waited", "rides", "done", "t_start")
```

A `Journey` represents one person's registered trip from floor `src` to floor `dst`. Key attributes:

- **`legs`** — The list of per-zone legs, computed by `plan_legs(src, dst)`. Each leg is a tuple `(zone_index, from_floor, to_floor)`.
- **`leg_i`** — Index of the current leg (starts at 0, advances after each leg completes).
- **`t_reg`** — Timestamp when the journey was registered.
- **`t_leg_reg`** — Timestamp when the current leg was registered (reset after each transfer).
- **`cur`** — Current floor (starts at `src`, updates after each leg).
- **`priority`** — If True, this passenger has genuine incapacity and jumps the queue.
- **`rides`** — Number of elevator rides taken so far.
- **`done`** — True when the entire journey is complete.

The `leg` property returns the current leg tuple or `None` if the journey is done. The `target_floor()` method returns the destination floor of the current leg. The `advance(t)` method finishes the current leg and returns `True` if the whole journey is complete.

### 7.2 The Shaft Class

```python
class Shaft:
    STALL_COOL = 6.0  # seconds a held run waits before re-trying
```

A `Shaft` represents one hoistway: two rope-linked cabins with one degree of freedom. The key state variable is `s` — cabin A's height above the zone floor in metres. Cabin B is always at `(rise_m - s)`. A rises exactly as B descends.

**State machine:**

- **`IDLE`** — Neither car is moving. The dispatcher is called to look for work.
- **`RUN`** — A run is in progress. The timer counts down; `s` interpolates from `run_from` to `target_s`.
- **`DOORS`** — The run has arrived. Doors are open for boarding/alighting. Timer counts down based on passenger count.
- **`STALLED`** — Not enough staged mass in the vault above. The run is held until mass arrives. The scarcity multiplier pulls carriers up the stair to fix it.

**Dispatch modes:**

- **`idle`** — No work found.
- **`collecting`** — Waiting for more riders to batch into one run (up to `BATCH_HOLD_S = 14` seconds).
- **`reposition`** — Moving an empty car to the oldest registered call (only after `REPOSITION_S = 20` seconds of waiting).
- **`paired`** — Both cars have passengers going opposite directions — the ideal case.
- **`single`** — Only one car has passengers.

**Key methods:**

- **`floor_a`** / **`floor_b`** — The floor number each car is currently at (rounded to the nearest floor).
- **`height_a_m()`** / **`height_b_m()`** — The absolute height above street level of each car.
- **`_board(floor, car, want_up, t)`** — Loads registered calls at `floor` heading the right way into `car`. Priority slots first, then longest wait first. Returns the number of passengers boarded.
- **`_next_stop_s(up)`** — Finds the next stop position (in A's coordinate) where either car has a passenger destination or can pick up an intermediate hall call.
- **`_demand(up)`** — Counts waiting passengers at both cars' current floors heading the given direction.
- **`_oldest_call(t)`** — Finds the floor with the longest-waiting registered call.
- **`dispatch(t)`** — The main dispatch logic. Decides whether to collect, reposition, or commit a run. Returns `True` if a run was committed.
- **`_commit(ds)`** — Pre-positions the counter-mass, then releases the run. This is the only place staged mass is ever spent, and the only place a run can stall. If the vault doesn't have enough mass, the run enters `STALLED` mode and the scarcity multiplier kicks in.
- **`arrive(t)`** — Unloads passengers whose leg ends at the current floor. Hands transfers to the next zone via `Building.complete_leg()`.
- **`update(dt, t)`** — Advances the state machine by `dt` seconds. In `RUN` state, interpolates `s` based on the remaining timer. In `DOORS` state, counts down the dwell timer. In `IDLE` state, calls `dispatch()`.

### 7.3 The ZoneState Class

```python
class ZoneState:
```

`ZoneState` holds the live state of one zone: hall queues, hoistways, banks, and incentives.

**Hall queues:**
- **`waiting`** — Dictionary mapping floor number → list of `Journey` objects waiting at that floor.

**Vault plumbing (the cascade):**
- **`top_level`** — The lobby level above this zone (zone index + 1).
- **`bot_level`** — The lobby level below this zone (zone index).
- **`vault_frac()`** — Fraction of the top vault that is full.
- **`draw_vault(units)`** — Spends staged mass: trays ride DOWN from the top vault to the bottom vault. Returns `False` if there isn't enough mass (causing a stall).
- **`stage_vault(units)`** — Surplus from a descending load lifts trays back UP the zone. This is the recovery mechanism.
- **`stored_J()`** — Total potential energy stored in the top vault.

**Incentives:**
- **`multiplier()`** — The live token multiplier for this zone, combining height and scarcity:
  ```
  multiplier = 1.0 + 0.85 × (lobby_height / tower_height) + 2.60 × max(0, (0.55 - vault_fraction) / 0.55)
  ```
  When the vault is full (vault_fraction = 1.0), the scarcity term is 0. When the vault is empty (vault_fraction = 0), the scarcity term is 2.60, giving a total multiplier of up to 1.0 + 0.85 + 2.60 = 4.45×.

**Wait statistics:**
- **`wait_push(w)`** — Records a wait time.
- **`wait_stats()`** — Returns (average, 90th percentile) of recent wait times.

**Walkers:**
- **`walkers(dt, t)`** — Simulates people climbing the health stair with trays. This is the ONLY energy input to the building. The climb rate depends on:
  - Zone population (more people = more potential climbers)
  - The live token multiplier (higher multiplier = more climbers)
  - A scarcity gate that prevents a zone from stripping the vault that feeds the zone below it

  Each carry takes trays from the bottom vault/landing banks and deposits them in the top vault. The metabolic cost and token credit are recorded.

- **`carry_once(trays, mult, full=True)`** — Executes one stair carry. If `full=True`, the carry reaches the sky lobby vault. If `full=False`, it deposits at a random landing bank within the zone. Records climbs, trays carried, flights, human energy, and tokens.

**Short-haul tray shuttle:**
- **`shuttle(dt)`** — Moves trays from landing banks to the top vault using the pure-gravity shuttle. The shuttle only runs when the vault is above 30% charge (it needs mass to spend on its own gravity drive). It moves at most `shuttle_trays × dt / 45` trays per tick, with a gravity cost of `n × frac_up × 1.15` vault units.

**Queue management:**
- **`queue_len()`** — Total waiting passengers across all floors.
- If the queue exceeds `TRAFFIC["queue_cap"]` (420), riders start balking — they take the stairs instead and may carry a tray while doing so.

**Update:**
- **`update(dt, t)`** — Updates all shafts, runs walkers, runs the shuttle, and handles balking.

### 7.4 The Building Class

```python
class Building:
```

`Building` is the whole vertical transit economy: 6 zones, 14 hoistways, 7 cascading vaults, one stair.

**Initialization:**
- Creates 6 `ZoneState` objects.
- Initializes the cascading vaults: level 0 (ground) starts at 30% capacity; all other levels start at 92% (staged from the night before).
- Initializes landing banks with 8 trays each.
- Sets the simulation clock to 06:00 (6.0 × 3600 seconds).
- Initializes all statistics counters.

**Floor selection:**
- **`_floor_weights()`** — Computes a cumulative distribution of destination floors, weighted by population (more people = more likely destination).
- **`pick_floor()`** — Picks a random destination floor using the cumulative distribution.

**Registration:**
- **`register(src, dst, t)`** — Creates a `Journey`, assigns priority (6% chance), and enqueues it in the appropriate zone's waiting list.
- **`_enqueue(j)`** — Places a journey in the waiting queue for its current leg's starting floor.
- **`complete_leg(j, t)`** — Called when a car arrives and a passenger's leg ends. If the journey is complete, records statistics. Otherwise, enqueues the passenger for the next leg (a transfer).

**Traffic spawning:**
- **`_spawn(dt)`** — Generates passenger traffic based on the time of day. Computes three Gaussian peaks (morning, lunch, evening) plus a flat interfloor background. Emits up-trips (floor 1 → random), down-trips (random → floor 1), and interfloor trips (random → random).

**Main tick:**
- **`update(dt)`** — Advances the clock, spawns traffic, and updates all zones. The clock wraps at 24 hours and increments the day counter.

**Sampling:**
- **`sample()`** — Records a history point (hour, vault fraction, wait time, queue length) for the timeline chart.

**Statistics:**
- **`wait_stats()`** — Building-wide average and worst-zone 90th percentile wait.
- **`cars_moving()`** — Count of shafts currently in RUN state.
- **`stalls()`** — Total stalls across all zones.
- **`kcal()`** — Total kilocalories burned by walkers.
- **`flights()`** — Total flights of stairs climbed.
- **`avg_trip_min()`** — Average door-to-door journey time in minutes.
- **`saved_kwh()`** — What a conventional lift bank would have consumed.
- **`saved_usd()`** — Avoided electricity cost in dollars.
- **`walker_pool_usd()`** — The real-dollar pool backing the token economy.
- **`usd_per_token()`** / **`usd_per_carry()`** / **`usd_per_flight()`** — Value of each token/carry/flight in real dollars.

**Operating mode:**
- **`mode()`** — Returns a string describing the current operating state based on the time of day and vault levels:
  - `"MASS SHORTFALL"` — Stalls with very low vaults
  - `"UP-PEAK (vaults discharging)"` — 6:48–10:00 AM
  - `"DOWN-PEAK (vaults re-staging)"` — 4:30–7:30 PM
  - `"LUNCH (two-way, near balance)"` — 11:30 AM–1:48 PM
  - `"NIGHT (stair carries + shuttles)"` — Before 6 AM or after 9 PM
  - `"INTERFLOOR (balanced)"` — Everything else

### 7.5 The DayWorld Class

```python
class DayWorld:
    TIME_WARP = [1.0, 10.0, 60.0, 300.0, 900.0]
```

`DayWorld` manages the time-warp for DAY mode. The `TIME_WARP` list gives five speed levels: 1× (real time), 10×, 60× (1 simulated minute per real second), 300× (5 simulated minutes per real second), and 900× (15 simulated minutes per real second — a full 24-hour day in ~96 real seconds).

The `sun(hour)` method returns a 0–1 brightness value based on the hour of day: 0 at night, 1 at midday, following a sine curve from 5:00 AM to 8:00 PM.

### 7.6 sky_colors()

```python
def sky_colors(sun):
    t = clamp(sun * 1.5)
    return (_mix(C_SKY_NIGHT1, C_SKY_DAY1, t), _mix(C_SKY_NIGHT2, C_SKY_DAY2, t))
```

Returns two sky colors (top and bottom of the gradient) based on the sun brightness. At night, both are dark navy. At midday, both are bright blue. The `sun * 1.5` factor makes the transition happen faster than the actual sun brightness (so the sky is fully daytime before the sun reaches its peak).

---

## 8. Section 7 — Informational Specification

Lines 2018–2307. The `build_info_sections()` function returns a list of (title, lines) tuples that form the content of the scrollable specification panel (accessed by pressing **I**).

The sections are:

1. **ABOUT THIS MODEL** — What the program is and how it was built.
2. **THE CORE LOOP (start here)** — The whole system in one paragraph: counter-running pairs, natural cancellation, leftover imbalance, vaults, tokens.
3. **THE BUILDING** — Key dimensions and counts.
4. **1. ZONING** — Why zones, how they stack, traffic-aware sizing.
5. **2. COUNTER-RUNNING CABIN PAIRS** — Two cars, one rope, one DOF, friction-only pairing.
6. **3. CASCADING WEIGHT BANKS + THE VAULT BATTERY** — Trays as currency, vaults as batteries, the cascade.
7. **4. THE TOKEN ECONOMY** — Height + scarcity multipliers, self-balancing.
8. **5. THE MONEY** — What a token is worth in real dollars, reference day figures, and **global scale estimates** if every elevator on the planet were replaced (~300 TWh/year, ~$48B/year, ~111 Mt CO₂/year avoided).
9. **6. REGISTERED DEMAND** — Timestamped calls, pre-positioning, batching, priority slots.
10. **7. THE MECHANICS** — How the imbalance got to 3–8%, worked example, differential reeving.
11. **8. THE HEALTH DIVIDEND** — Stair carries, kilocalories, fitness programme.
12. **MEASURED** — What one full simulated day actually does (calls, waits, carries, kcal, 0 kWh).
13. **HONEST PHYSICS** — What is and isn't claimed: not perpetual motion, three real effects, speed and mass costs.
14. **VERIFICATION CHECKLIST** — 16-point checklist of every implemented feature.
15. **CONTROLS** — Full key reference.

The function also computes reference-day dollar figures from the `REFERENCE` and `ECONOMY` constants so they track any parameter changes.

---

## 9. Section 8 — HUD and UI Helpers

Lines 2310–2383. Small drawing utilities used throughout the UI:

- **`vgradient(surf, top, bot)`** — Fills a surface with a vertical gradient from `top` to `bot` color. Used for the background and the DAY-mode sky.

- **`bar(surf, font, x, y, w, h, frac, color, label, valtext, lo=None)`** — Draws a horizontal progress bar with a label above and a value text. The `lo` parameter draws a warning tick mark at a specific fraction. Used for vault charge bars, queue bars, and day progress.

- **`panel(surf, x, y, w, h, alpha=210)`** — Draws a semi-transparent dark panel with a thin border. Used for all UI panels.

- **`wrap_text(font, text, maxpx)`** — Word-wraps a string to fit within `maxpx` pixels. Returns a list of lines.

- **`_toc_label(head)`** — Shortens a spec section header to a TOC-rail entry. E.g., "1. ZONING (the biggest single efficiency gain)" → "1. Zoning".

- **`_split_key_line(ln)`** — Splits a CONTROLS line on the first 3+-space gap. E.g., "TAB           cycle modes" → ("TAB", "cycle modes").

- **`_label(surf, font, text, pos, accent=False)`** — Draws a 3D label at a screen position with a small dot marker and a semi-transparent background. Used for part labels in the 3D view.

---

## 10. Section 9 — The 3D Renderer

Lines 2385–2643. The `TowerRenderer` class projects and paints `Part` objects using a **painter's algorithm** (sort polygons by depth, draw far-to-near).

### 10.1 TowerRenderer.__init__()

```python
def __init__(self, parts_builder, outline=False, detail_labels=True,
             home_az=0.72, home_el=0.16, home_dist=1.45):
```

- **`parts_builder`** — A function that returns a list of `Part` objects (either `build_tower_parts` or `build_machine_parts`).
- **`outline`** — If True, draw polygon outlines (used for the machine view).
- **`detail_labels`** — If True, show per-mesh labels in exploded view (used for the machine; too cluttered for the tower).
- **`home_az`**, **`home_el`**, **`home_dist`** — Default camera position (azimuth, elevation, distance).

Two renderers are created:
- **Tower renderer**: `home_az=0.72, home_el=0.08, home_dist=1.12` — slightly elevated, close enough to see the whole building.
- **Machine renderer**: `home_az=0.62, home_el=0.24, home_dist=2.30` — more elevated, farther back to see the mechanical detail.

The renderer also stores:
- **`light`** — A normalized 3D vector defining the light direction for shading.
- **`view`** — Current view mode: "full", "exploded", or "assembly".
- **`section`** — Boolean for the half-section cut.
- **`explode_amt`** — Animated explode amount (0 = assembled, 1 = fully exploded).
- **`assembled`** — In assembly view, the number of parts that have been placed so far.
- **`hovered`** / **`selected`** — Indices of the hovered/pinned part.
- **`pop`** — Per-part animation array for the hover "pop" effect.

### 10.2 Camera Controls

- **`reset_view()`** — Returns to the home camera position.
- **`zoom_at(factor, mouse_pos, rect)`** — Zooms by `factor`, optionally anchored to the mouse position (so the point under the cursor stays put).
- **`orbit(dx, dy)`** — Adjusts azimuth and elevation based on mouse drag deltas.
- **`pan_by(dx, dy)`** — Adjusts the pan offset based on right-drag deltas.

### 10.3 View Modes

- **`set_view(mode)`** — Sets the view to "full", "exploded", or "assembly". In assembly mode, if all parts are already placed, resets to 0 (start over).
- **`toggle_section()`** — Toggles the half-section cut.
- **`assembly_next()`** / **`assembly_prev()`** — Steps the assembly build forward/backward by one part.
- **`assembly_all()`** / **`assembly_clear()`** — Places all parts / clears all parts.

### 10.4 tick() — Animation Interpolation

```python
def tick(self, dt):
```

Animates the explode amount toward its target (1.0 for exploded, 0.0 for full) with exponential easing. Also animates the hover "pop" effect — the hovered part moves slightly toward the viewer.

### 10.5 _layout() — Part Positioning

```python
def _layout(self, pi, vw, eamt):
```

Returns the offset, dim factor, and tag for a part in the current view:

- **Full view**: no offset, full opacity, "normal".
- **Exploded view**: offset by `part.explode × eamt`, full opacity, "normal".
- **Assembly view**:
  - Parts already placed (`order < assembled`): no offset, full opacity, "normal".
  - The part being placed (`order == assembled`): half-offset, full opacity, "active" (highlighted gold).
  - Parts not yet placed (`order > assembled`): full offset, 28% opacity, "pending" (dimmed).

### 10.6 render() — The Main Rendering Pipeline

```python
def render(self, surf, rect, angles, mouse_pos=None, show_labels=True,
           label_font=None, interactive=False):
```

This is the core rendering method. The pipeline is:

1. **Set clip rectangle** to the viewport.
2. **Compute camera matrix**: `Rcam = rot_x(el) @ rot_y(az)`.
3. **For each part**, for each mesh:
   a. Compute world vertices: `wv = mesh.world_verts(angle) + offset`.
   b. Transform to camera space: `cam = wv @ Rcam.T`, then add `dist` to z.
   c. Compute the mesh color (with mix blend, dim factor, and highlight).
   d. For each face:
      - Skip if behind the section cut plane (if section is active and the face's average X > 0.004).
      - Skip if any vertex is behind the camera (z ≤ 0.05).
      - Compute the face normal via cross product of two edge vectors.
      - Flip the normal if it points away from the camera (back-face culling).
      - Compute Lambertian shading: `shade = 0.46 + 0.54 × max(0, normal · light)`. The 0.46 ambient ensures no face is fully black.
      - Compute the average depth and add to the polygon list.
   e. Collect label positions and hover-pick circles.
4. **Sort polygons** by average depth (far to near).
5. **Draw polygons** using `pygame.draw.polygon()`.
6. **Draw leader lines** for assembly mode (connecting the active part to its target position).
7. **Draw labels** with anti-overlap stacking.
8. **Hover-pick**: if interactive, find the nearest part circle to the mouse.

The projection is a simple perspective projection:

```
screen_x = cx + focal × cam_x / cam_z
screen_y = cy - focal × cam_y / cam_z
```

Where `focal = min(rect.w, rect.h) × 1.12` and `cx`, `cy` are the viewport center plus pan offset.

### 10.7 Hover-Picking

After rendering, if `interactive` is True and `mouse_pos` is not None, the renderer finds the nearest part to the mouse by checking if the mouse is within each part's bounding circle (center and radius computed during rendering). The nearest (smallest depth) part wins.

---

## 11. Section 10 — The Application

Lines 2646–3790. The `App` class ties everything together: pygame initialization, event handling, simulation, rendering, and the main loop.

### 11.1 App.__init__()

- Initializes pygame with a 1480×900 window.
- Creates fonts in several sizes (11px, 12px, 14px, 20px bold, 30px bold).
- Creates two `TowerRenderer` instances: one for the tower, one for the machine.
- Creates a `Building` instance (the live simulation).
- Creates a `DayWorld` instance (time-warp manager).
- Sets the initial mode to "tower".
- Initializes angle accumulators for sheave/governor spin animation.
- Pre-renders the background gradient.
- Computes the info panel section offsets for the TOC.

### 11.2 Event Handling

The `handle_events()` method processes pygame events:

- **QUIT** → stops the program.
- **KEYDOWN** → calls `_key()` which handles all keyboard shortcuts.
- **MOUSEBUTTONDOWN**:
  - Left click: first checks modal overlays (info/help/checklist), then mode tabs, then part list, then preview buttons. If none of those, starts orbit-dragging and pins the hovered part.
  - Right click: starts panning.
  - Wheel: zooms.
- **MOUSEWHEEL** → zooms.
- **MOUSEBUTTONUP** → stops dragging/panning.
- **MOUSEMOTION** → if dragging, orbits; if panning, pans.

### 11.3 Simulation Loop

The `update(dt)` method:

1. Calls `rend().tick(dt)` to animate the renderer (explode amounts, hover pop).
2. Computes the simulation time step: `sim_dt = dt × warp` (only DAY mode time-warps).
3. Subdivides the simulation step into chunks of at most 0.45 seconds (to maintain simulation stability at high time-warp).
4. Calls `Building.update(step)` for each chunk.
5. Samples the building state every 0.5 real seconds for the timeline chart.
6. Calls `sync_live()` to write the simulation state onto the 3D meshes.
7. Advances the sheave/governor spin angles based on how many cars are moving and at what speed.

### 11.4 sync_live() — Writing Simulation to Meshes

This is the critical method that connects the simulation to the 3D visualization. It writes the live state onto the pre-built meshes without rebuilding any geometry:

**Cabins**: For each zone, for each shaft, writes `mesh.dyn[1]` (the Y offset) for cabin A and cabin B based on `shaft.s` (the current position). Cabin A's Y offset is `tds(sh.s)`, cabin B's is `tds(rise_m - sh.s)`.

**Counterweights**: The counterweight moves opposite to cabin A, so its Y offset matches cabin B's.

**Tray racks**: The tray rack on the descending side is shown as loaded (green, `mix_t = 0.0`), and the one on the ascending side is shown as empty (shaft-colored, `mix_t = 0.92`).

**Landing banks**: `mix_t` is set based on how many trays are in the bank (1.0 = empty/dim, 0.0 = full/bright green).

**Vaults**: `mix_t` is set based on the vault fraction (1.0 = empty/red, 0.0 = full/green).

**Shuttles**: `dyn[1]` is set based on the shuttle position (oscillating with a sine wave for visual effect).

### 11.5 Drawing: TOWER and MACHINE Modes

The `draw_preview()` method:

1. Calls `TowerRenderer.render()` to draw the 3D scene.
2. Draws view tabs (FULL / EXPLODED / ASSEMBLY / SECTION + assembly controls).
3. Draws the part list (left sidebar) — scrollable list of all parts with click-to-select.
4. Draws the scale bar — a dynamically computed reference bar showing the scale in metres.
5. Draws the spec card — the inspector panel showing the active part's name and specifications.
6. Draws the right-hand panel:
   - **TOWER mode**: `draw_tower_legend()` — building spec table, zone plan with live vault charge bars.
   - **MACHINE mode**: `draw_machine_stats()` — machine specs, "what one run costs" worked examples, force path diagram.
7. Draws the footer with control hints and toggle buttons.

### 11.6 Drawing: DAY Mode

The `draw_day()` method:

1. Draws the sky gradient based on the current sun brightness.
2. Draws the sun (day) or moon + stars (night) at the correct position in the sky arc.
3. Draws city silhouette buildings and ground.
4. Renders the tower in the scene using the tower renderer (with a gentle automatic camera drift).
5. Draws the **live zone elevation strip** — a 2D cut-away elevation showing:
   - Each zone as a colored block (color = vault charge status)
   - Each hoistway with the two counter-running cabins as small bars
   - Vault charge bars
   - Queue length and average wait
   - Token multiplier
   - Sky lobby lines
6. Draws the **DAY HUD** — a comprehensive statistics panel with:
   - Operating mode and clock
   - 0 kW grid draw (always)
   - Average wait time
   - Progress bars (lowest vault, staged mass, hall queue, day progress)
   - Tray flow ledger (5 categories)
   - Full statistics (20+ metrics including per-tower savings)
   - **Global scale estimates** (~300 TWh/year, ~$48B/year, ~111 Mt CO₂/year, ~24M cars off road)
7. Draws the **timeline** — a 24-hour chart of vault charge with a live cursor.

### 11.7 Overlays: Help, Checklist, Info Panel

- **`draw_help()`** — A centered modal with the full controls reference, formatted as key/description pairs.
- **`draw_checklist()`** — A centered modal with the 19-point verification checklist in two columns.
- **`draw_info()`** — A large centered modal with a TOC rail on the left and scrollable content on the right. Supports mouse-wheel scrolling, arrow-key scrolling, and TOC-click navigation. Includes a scrollbar thumb.

### 11.8 The Main Loop

```python
def run(self):
    _print_banner()
    while self.running:
        dt = min(self.clock.tick(45) / 1000.0, 0.05)
        self.handle_events()
        self.update(dt)
        self.draw()
    pygame.quit()
```

The main loop runs at 45 FPS (capped by `clock.tick(45)`). The `dt` is clamped to 0.05 seconds to prevent huge time steps if the window is dragged or the system stalls.

Each frame:
1. **Handle events** — process all pending input.
2. **Update** — advance the simulation and sync the 3D meshes.
3. **Draw** — render everything to the screen.

The `_print_banner()` function prints a summary to the console before the window opens.

---

## 12. End-to-End Data Flow

Here is the complete data flow for one frame of the program:

```
1. pygame events (keyboard, mouse)
   ↓
2. App.handle_events()
   → updates camera, view mode, selection, time-warp
   ↓
3. App.update(dt)
   → TowerRenderer.tick(dt) — animate explode/hover
   → compute sim_dt = dt × warp (DAY mode only)
   → subdivide into steps ≤ 0.45 s
   → for each step: Building.update(step)
      → Building._spawn(step) — generate traffic
      → for each ZoneState: ZoneState.update(step, t)
         → for each Shaft: Shaft.update(step, t)
            → Shaft.dispatch(t) — find work
            → Shaft._commit(ds) — pre-position mass, release run
               → ZoneState.draw_vault(units) — spend staged mass
               → or ZoneState.stage_vault(units) — recover surplus
            → Shaft arrive(t) — unload passengers
         → ZoneState.walkers(step, t) — stair carries
         → ZoneState.shuttle(step) — tray shuttles
         → handle balking if queue too long
   → App.sync_live() — write simulation onto 3D meshes
   → advance sheave/governor spin angles
   ↓
4. App.draw()
   → draw background
   → if DAY mode: draw_day()
      → sky, sun/moon, city, tower, zone strip, HUD, timeline
   → else: draw_preview()
      → TowerRenderer.render() — project and paint 3D parts
      → view tabs, part list, spec card, scale bar
      → tower legend or machine stats
      → footer
   → draw topbar
   → draw overlays (help/info/checklist if open)
   → pygame.display.flip()
```

---

## 13. Glossary

| Term | Definition |
|---|---|
| **Counter-running** | Two cabins on one rope over one sheave: one rises as the other descends |
| **Sky lobby** | A transfer floor between zones where riders switch elevators |
| **Vault** | A structural bay at a sky lobby that stores staged weight trays — the building's "battery" |
| **Tray** | A modular 11.34 kg (25 lb) weight unit, the currency of the system |
| **Landing bank** | A quick-load tray hopper at every floor where walkers deposit trays |
| **Staged mass** | Trays that have been carried up and stored in a vault, ready to drop |
| **Token** | Internal credit earned by carrying trays up stairs, used as an allocation signal |
| **Multiplier** | The live token rate for a zone, combining height and scarcity factors |
| **Scarcity** | How low a vault's stock is; low stock multiplies the token payout to attract carriers |
| **Imbalance** | The mass difference between the two sides of the rope, expressed as a % of suspended mass |
| `mu_eff` | Effective resistance coefficient (2.8%), lumping all friction sources |
| **Reeving** | The rope arrangement; 1:1 = direct, 2:1 = mechanical advantage (half the force, half the speed) |
| **Base counterweight** | A fixed mass sized for the average zone load; never carried by people |
| **Shuttle** | A narrow pure-gravity chase that moves trays from landing banks to vaults |
| **Health stair** | The generous, daylit stair where walkers carry trays — the only energy input |
| **Balking** | When a rider gives up waiting and takes the stairs instead |
| **Stall** | When a run cannot proceed because the vault above lacks sufficient staged mass |
| **Batching** | Holding a run briefly to collect more same-direction riders into one balanced run |
| **Pre-positioning** | Setting the counter-mass on the descending side before the rider arrives |
| **Recovery** | When a descending car is heavier than needed, the excess lifts trays back up (86% efficient) |
| **Painter's algorithm** | Rendering technique: sort polygons by depth, draw far-to-near |
| **`dyn`** | A live 3D translation on a Mesh, written by the simulation every frame |
| **`mix_t`** | A live color blend amount on a Mesh (0 = base color, 1 = mixed color) |
| **`Part`** | A named logical component made of one or more Meshes, with specs and an explode offset |
| **`ZoneSpec`** | The fixed dimensional description of one vertical zone |
| **`Shaft`** | The live state of one hoistway: position, state machine, passengers, trays |
| **`ZoneState`** | The live state of one zone: queues, shafts, vaults, walkers, incentives |
| **`Building`** | The whole simulation: zones, vaults, traffic, statistics, the clock |
| **`DayWorld`** | Time-warp manager for DAY mode |
| **`TowerRenderer`** | The 3D renderer: camera, projection, sorting, lighting, views, picking |
| **`App`** | The pygame application: events, simulation loop, all drawing |
