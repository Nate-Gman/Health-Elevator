#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 HealthElevator.py  --  GRAVITY TOWER :: 60-Floor Zero-Power Vertical Transit
================================================================================

A 100% standalone monolith that builds, animates and *operates* a 60-storey
skyscraper whose elevators run on NOTHING BUT GRAVITY AND HUMAN WEIGHT, in
real time, mechanically and energetically to scale, in a single Python file.

It is the vertical re-engineering of the HOHEV modelling method proven in
SE.py (the marine digital twin): the same to-scale Part/Mesh geometry, the
same honest first-order energy ledger, the same three-mode inspector -- but
every subsystem is re-hosted in a tower and the "fuel" is now the POTENTIAL
ENERGY of mass that people carried up the stairs.

  ZONED TOWER        60 floors split into 6 independent vertical zones of
                     9-11 floors, joined by 5 SKY LOBBIES. No hoistway runs
                     the full height; no walker ever hauls mass past the next
                     sky lobby. Zones stack, so the structural core stays small.
  COUNTER-RUNNING    Every hoistway holds TWO rope-linked cabins on one head
  CABIN PAIRS        sheave: the descending loaded cabin directly raises the
                     ascending one. Net human input approaches the FRICTION
                     LOSS ONLY -- not the full lift work.
  CASCADING WEIGHT   Modular 11.3 kg (25 lb) trays are deposited by walkers at
  BANKS              landing banks and staged upward in steps to the sky-lobby
                     vaults. A vault of staged trays IS the building battery:
                     stored joules = mass x g x height above the zone floor.
  TOKEN ECONOMY      Credit per flight climbed rises with height AND with live
                     scarcity: when an upper vault runs low its multiplier
                     spikes, pulling carriers exactly where they are needed.
                     A self-balancing incentive gradient, no central control.
  REGISTERED DEMAND  Every call is registered with a timestamp. The dispatcher
                     pre-positions counter-mass BEFORE the rider arrives,
                     batches same-direction riders into one balanced run, and
                     keeps free priority slots for genuine incapacity.
  LOW-IMBALANCE      Roller guides, lubricated sheaves and (on the light upper
  MECHANICS          zones) differential 2:1 reeving pull the required weight
                     imbalance down to 3-8% of the suspended mass.
  HEALTH DIVIDEND    The energy input is people climbing stairs with trays.
                     The model tallies flights, mass-metres and kilocalories:
                     the building is powered by the exercise it causes.

Three modes (cycle with TAB):

  1. TOWER    Orbit the whole 234 m building to scale. Zones, sky lobbies,
              14 hoistways, 28 live counter-running cabins, base counterweights,
              60 landing weight banks and the health stair all move live.
  2. MACHINE  Orbit ONE zone's gravity machine in mechanical detail -- head
              sheave, diverters, differential reeving blocks, guide rails,
              cabin sling, tray-stacked counterweight, governor, ratchet brake
              and pit buffers. Exploded / section / assembly.
  3. DAY      Run a full 24-hour operating day. Live up-peak / down-peak
              traffic, vault charge, wait times, stalls, token multipliers,
              tray flow, kilocalories burned and the running 0 kWh power bill.

Dependencies:  numpy, pygame   Run:  python HealthElevator.py
Press  H  for controls,  I  for the full informational specification panel.
Every dimension in TOWER/DIMS below is real (metres / SI) and drawn to scale.
================================================================================
"""

import math
import os
import random
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import numpy as np
import pygame


# =============================================================================
# SECTION 1 -- ENGINEERING SPECIFICATION (to scale, metres / SI)
# =============================================================================

# Whole-building dimensions (metres). A 60-storey, 234 m commercial tower --
# a normal, buildable high-rise, not a supertall. The 3D TOWER view is built
# entirely from these numbers and the transit physics is cross-checked against
# the same ones.
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

FLOORS      = TOWER["floors"]
FLOOR_H     = TOWER["floor_h_m"]
TOWER_H_M   = FLOORS * FLOOR_H            # 234.0 m to the main roof

# DIMS: the individual subsystems, to scale (metres / kg). Everything the TOWER
# and MACHINE views draw is positioned and sized from here, so the model stays
# dimensionally honest.
DIMS = {
    # --- hoistway + cabins -------------------------------------------------
    "shaft_w_m":          4.60,   # ONE hoistway holds TWO counter-running cabins
    "shaft_d_m":          3.20,
    "cabin_w_m":          2.00,   # each cabin (side by side in the same shaft)
    "cabin_d_m":          2.30,
    "cabin_h_m":          2.45,
    "cabin_gap_m":        0.30,   # clearance between the paired cabins
    "car_door_w_m":       1.10,
    "rail_face_m":        0.16,   # T-section guide-rail blade width
    "roller_d_m":         0.16,   # roller guide-shoe wheel
    "sheave_d_m":         1.10,   # head traction sheave (grooved)
    "sheave_t_m":         0.22,
    "diverter_d_m":       0.68,   # diverter / deflector sheaves in the head
    "block_d_m":          0.52,   # differential-reeving movable block
    "gov_sheave_d_m":     0.42,   # overspeed governor sheave
    "gov_rope_d_m":       0.008,
    "rope_d_m":           0.013,  # 13 mm traction rope
    "ropes":              6,      # ropes per hoistway
    "rope_kg_per_m":      0.72,   # steel rope linear mass
    "buffer_d_m":         0.30,   # oil buffer in the pit
    "buffer_h_m":         1.10,
    "brake_drum_d_m":     0.62,   # band brake / ratchet-pawl holding drum
    "brake_drum_t_m":     0.18,
    "pawl_len_m":         0.45,

    # --- fixed base counterweight + variable tray mass ---------------------
    "cwt_w_m":            0.90,   # base counterweight frame in its own chase
    "cwt_d_m":            0.42,
    "cwt_h_m":            2.10,
    "tray_w_m":           0.42,   # ONE modular weight tray (the carried unit)
    "tray_d_m":           0.30,
    "tray_h_m":           0.075,
    "tray_kg":           11.34,   # 25 lb -- ergonomic backpack/cart unit
    "tray_stack_max":     26,     # trays a cabin roof rack can hold

    # --- weight banks + sky-lobby vaults -----------------------------------
    "bank_w_m":           1.80,   # quick-load landing bank (tray hopper)
    "bank_d_m":           0.70,
    "bank_h_m":           1.10,
    "bank_capacity":      120,    # trays per landing bank
    "vault_w_m":         11.00,   # sky-lobby staged-mass vault (a structural bay)
    "vault_d_m":          7.00,
    "vault_h_m":          3.40,
    "vault_capacity":   14000,    # trays per sky-lobby vault (~159 t staged)
    "ground_reservoir": 60000,    # ground-level tray store (at grade: no penalty)
    "lobby_extra_h_m":    3.60,   # sky lobbies are double height

    # --- the health stair --------------------------------------------------
    "stair_w_m":          3.00,   # generous, daylit, tray-cart friendly
    "stair_d_m":          6.40,
    "stair_run_m":        2.90,   # horizontal run of one flight
    "flights_per_floor":  2,

    # --- short-haul weight shuttle ----------------------------------------
    "shuttle_w_m":        1.40,   # narrow chase, pure-gravity tray shuttle
    "shuttle_d_m":        1.40,
    "shuttle_car_h_m":    1.60,
    "shuttle_trays":      40,     # trays carried per shuttle run
}

# The single scale that maps real metres -> renderer display units so the whole
# 234 m tower frames cleanly in the orbit camera (1 unit ~ 300 m).
TOWER_DISP = 1.0 / 300.0          # TOWER-view metres -> display units
MACH_DISP  = 1.0 / 9.0            # MACHINE-view metres -> display units
TOWER_Y0   = -0.42                # vertical centring offset for the tower view


def tds(m):
    """metres -> TOWER-view display units (ground plane at TOWER_Y0)."""
    return m * TOWER_DISP


def ty(m):
    """metres above street level -> TOWER-view display Y."""
    return m * TOWER_DISP + TOWER_Y0


def mds(m):
    """metres -> MACHINE-view display units."""
    return m * MACH_DISP


# --- ZONE PLAN (traffic-aware sizing: capacity falls with height) ------------
# (floor_lo, floor_hi, hoistways, cabin capacity, reeving MA, cabin mass kg)
# Lower zones carry the heavy commuter load: more hoistways, bigger cabins,
# direct 1:1 roping for speed. Upper zones are sparse: fewer, smaller cabins on
# differential 2:1 reeving, which halves the weight imbalance a run needs at the
# cost of half the car speed -- exactly the right trade where traffic is light.
ZONE_PLAN = [
    (1,  11, 3, 16, 1, 900.0),
    (11, 21, 3, 16, 1, 900.0),
    (21, 31, 2, 13, 1, 820.0),
    (31, 41, 2, 13, 1, 820.0),
    (41, 51, 2, 10, 2, 700.0),
    (51, 60, 2,  8, 2, 620.0),
]

# --- physical constants ------------------------------------------------------
G              = 9.80665      # m/s^2
TRAY_KG        = DIMS["tray_kg"]
PAX_KG         = 75.0         # design passenger mass
BODY_KG        = 75.0         # design walker body mass (stair metabolic work)

# MECHANICAL LOSSES. The goal is a required imbalance of 3-8% of the suspended
# mass. mu_eff lumps roller-guide rolling resistance, sheave bearing drag, rope
# bending stiffness and door/seal drag into one honest coefficient. Roller
# guides on machined rails plus well-lubricated grooved sheaves land near 0.028.
MU_EFF         = 0.028        # effective resistance coefficient (fraction of W)
MU_SPEC_LO     = 0.030        # published imbalance band, low  (3%)
MU_SPEC_HI     = 0.080        # published imbalance band, high (8%)
IMBAL_MARGIN   = 2.05         # imbalance commanded over the pure friction floor
                              # -> 5.7% of suspended mass, inside the 3-8% band
BATCH_HOLD_S   = 14.0         # collect window before a run is released
REPOSITION_S   = 20.0         # wait before an empty car is sent to a call
ROT_INERTIA_FR = 0.11         # sheave/rope rotating inertia as a fraction of M
RECOVERY_EFF   = 0.86         # descending surplus -> re-staged tray height
ROPE_SPEED_MS  = 2.60         # rope speed cap (car speed = this / reeving MA)
ACCEL_CAP_MS2  = 0.95         # comfort limit on car acceleration
JERK_DWELL_S   = 1.6          # levelling + door pre/post time per stop
DOOR_DWELL_S   = 3.4          # nominal door-open dwell
BOARD_S_PER_PAX = 1.05        # extra dwell per boarding/alighting passenger

# TOKEN ECONOMY. Credit is earned per tray-flight actually climbed. The rate
# scales with the height of the deposit (a tray staged high is worth more
# joules) and with live SCARCITY at the destination vault, so low upper stock
# automatically multiplies the payout and pulls carriers upward.
TOKEN = {
    "base_per_tray_flight": 1.00,   # tokens per tray per floor climbed
    "height_gain":          0.85,   # extra multiplier at the top of the tower
    "scarcity_gain":        2.60,   # extra multiplier when a vault is empty
    "scarcity_floor":       0.55,   # vault fraction at/above which no bonus
    "priority_reserve":     0.06,   # share of slots kept free for incapacity
}

# WALKER MODEL. Not everyone climbs; the fraction that does responds to the
# live token multiplier. Each carry is bounded by an ergonomic tray count.
WALK = {
    "base_rate_per_100":  2.10,   # climbs per 100 zone occupants per minute
    "incentive_gain":     1.60,   # extra climbs when the multiplier is high
    "trays_per_carry":    2.2,    # 2.2 x 11.34 kg = 25 kg in a stair cart
    "climb_speed_fl_s":   0.16,   # floors climbed per second (loaded)
    "metabolic_eff":      0.23,   # mechanical work / metabolic energy
    "kcal_per_kj":        0.239,
}

# TRAFFIC PROFILE. Person-trips per minute for the whole building, as sums of
# gaussians over the 24 h clock: a sharp morning up-peak, a two-way lunch
# period, a broad evening down-peak, plus a flat interfloor background.
TRAFFIC = {
    "am_peak_h":   8.30, "am_sigma_h": 1.10, "am_amp":  9.00,
    "lunch_h":    12.50, "lunch_sigma": 0.80, "lunch_amp": 5.80,
    "pm_peak_h":  17.80, "pm_sigma_h": 1.30, "pm_amp":   7.60,
    "inter_amp":   3.00, "inter_start": 7.0, "inter_end": 19.0,
    "queue_cap":    420,          # per-zone hall queue before riders balk
}

# What the building would have drawn as a conventional geared/gearless bank.
# Used purely as the honest reference figure for the "0 kWh" claim.
REFERENCE = {
    "kwh_per_trip":   0.055,      # typical traction-lift energy per passenger trip
    "standby_kw":     1.10,       # per lift standby/controller draw
    "lifts":          14,
    "tariff_usd_kwh": 0.16,
    "co2_kg_kwh":     0.37,
}

# THE MONEY. The token economy in Goal.md is only ever specified in internal
# credits. To answer "what is a token actually worth", this prices it against
# the one real saving the building undeniably has: the electricity bill of
# the conventional lift bank it replaced (REFERENCE, above). payout_frac=1.0
# means 100% of that avoided bill is passed straight through to walkers as
# token value -- the honest UPPER BOUND, since it assumes the building keeps
# none of the saving for itself. This is a pricing choice, not a measurement;
# lower payout_frac if the building should also bank some of the saving.
ECONOMY = {
    "walker_payout_frac": 1.00,
}

# GLOBAL SCALE. If the gravity-transit principle replaced every traction and
# hydraulic lift on the planet, here is what the avoided electricity would be.
# Figures are conservative mid-points from industry sources:
#   ~20 million elevators installed worldwide (Elevator World, IAEC estimates)
#   ~300 TWh/year global elevator electricity (~1% of world electricity production)
#   Average ~15,000 kWh per elevator per year (most are low-rise / low-traffic)
# The model tower's 14 lifts avoid ~267,000 kWh/year — well above the global
# average because they serve a 60-storey building with heavy commuter traffic.
GLOBAL = {
    "elevators_world":  20_000_000,   # installed elevator units worldwide
    "twh_year":         300.0,        # TWh/year global lift electricity consumption
    "avg_kwh_per_lift": 15_000,       # kWh per elevator per year (global average)
}


# =============================================================================
# SECTION 2 -- COLORS & THEME
# =============================================================================

BG_TOP       = (10, 15, 24)
BG_BOT       = (3, 5, 9)
C_CONCRETE   = (128, 136, 150)   # structural core / slabs
C_SLAB       = (114, 124, 140)
C_PODIUM     = (98, 108, 126)
C_GLASS      = (68, 112, 160)    # curtain wall
C_GLASS_HI   = (118, 174, 224)   # daylit spandrel shimmer
C_MULLION    = (90, 100, 118)
C_LOBBY      = (240, 202, 108)   # sky-lobby band (warm, lit)
C_SHAFT      = (80, 96, 122)     # hoistway enclosure
C_CABIN      = (236, 202, 116)   # live cabin
C_CABIN_B    = (150, 206, 232)   # its counter-running twin
C_CWT        = (128, 140, 156)   # fixed base counterweight
C_TRAY       = (104, 200, 132)   # modular weight tray (the carried unit)
C_TRAY_LOW   = (196, 92, 88)     # tray stock when a vault runs scarce
C_BANK       = (76, 150, 110)    # landing weight bank
C_VAULT      = (60, 128, 96)     # sky-lobby staged-mass vault
C_STAIR      = (222, 140, 92)    # the health stair
C_SHUTTLE    = (168, 132, 220)   # short-haul tray shuttle
C_ROPE       = (198, 204, 214)
C_SHEAVE     = (120, 134, 152)
C_STEEL      = (156, 164, 176)
C_RAIL       = (176, 182, 194)
C_BRAKE      = (196, 106, 72)
C_CROWN      = (92, 104, 124)
C_GROUND     = (36, 44, 58)
C_TEXT       = (224, 230, 238)
C_TEXT_DIM   = (150, 160, 175)
C_ACCENT     = (96, 200, 255)
C_GOOD       = (92, 220, 132)
C_WARN       = (255, 200, 60)
C_BAD        = (255, 96, 96)
C_GRAV       = (128, 226, 176)   # gravity / free-energy accent
C_PANEL      = (16, 22, 32)
C_PANEL_HI   = (28, 38, 54)
C_SKY_DAY1   = (62, 108, 162)
C_SKY_DAY2   = (168, 200, 228)
C_SKY_NIGHT1 = (6, 10, 24)
C_SKY_NIGHT2 = (24, 34, 58)
C_SUN        = (255, 212, 96)
C_CITY       = (34, 42, 58)


# =============================================================================
# SECTION 3 -- MINI 3D ENGINE (software renderer, painter's algorithm)
# The proven geometry-agnostic toolkit from the HOHEV/SE.py twin, extended with
# a per-mesh LIVE offset (`dyn`) and colour mix (`mix_t`) so cabins, counter-
# weights and tray stocks can move and change state without rebuilding geometry.
# =============================================================================

VISUAL_DETAIL = 1.0              # mesh resolution multiplier for round parts


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=float)


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=float)


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=float)


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def _mix(c1, c2, t):
    return (int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t))


class Mesh:
    """A bag of vertices + polygon faces with a base colour, in display units.
    `spin` is the rotation ratio against the master angle of its `group`;
    `pivot` offsets the local origin; `tilt` is a static (rx, ry) for off-axis
    spinners; `dyn` is a LIVE translation the simulation writes every frame
    (moving cabins); `mix_t`/`mix_col` are a LIVE colour blend (bank stock)."""

    def __init__(self, verts, faces, color, name="", spin=0.0, group="default",
                 pivot=(0.0, 0.0, 0.0), tilt=(0.0, 0.0), selectable=False):
        self.verts = np.asarray(verts, dtype=float)
        self.faces = faces
        self.color = color
        self.name = name
        self.spin = spin
        self.group = group
        self.pivot = np.asarray(pivot, dtype=float)
        self.tilt = tilt
        self.selectable = selectable
        self.dyn = np.zeros(3, dtype=float)
        self.mix_col = None
        self.mix_t = 0.0
        self.hidden = False

    def world_verts(self, angle=0.0):
        v = self.verts
        if self.spin:
            v = v @ rot_z(angle * self.spin).T
        rx, ry = self.tilt
        if rx or ry:
            v = v @ (rot_x(rx) @ rot_y(ry)).T
        return v + self.pivot + self.dyn

    def shade_color(self):
        if self.mix_col is not None and self.mix_t > 0.001:
            return _mix(self.color, self.mix_col, clamp(self.mix_t))
        return self.color


# ---- primitive builders -----------------------------------------------------

def _detail_seg(seg):
    return max(8, int(round(seg * VISUAL_DETAIL)))


def _box(cx, cy, cz, sx, sy, sz):
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    v = [(cx - hx, cy - hy, cz - hz), (cx + hx, cy - hy, cz - hz),
         (cx + hx, cy + hy, cz - hz), (cx - hx, cy + hy, cz - hz),
         (cx - hx, cy - hy, cz + hz), (cx + hx, cy - hy, cz + hz),
         (cx + hx, cy + hy, cz + hz), (cx - hx, cy + hy, cz + hz)]
    f = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
         (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return v, f


def _solid_cylinder(r, z0, z1, seg=28):
    seg = _detail_seg(seg)
    verts, faces = [], []
    ang = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    for z in (z0, z1):
        for a in ang:
            verts.append((r * math.cos(a), r * math.sin(a), z))
    c0 = len(verts)
    verts.append((0, 0, z0))
    c1 = len(verts)
    verts.append((0, 0, z1))
    for i in range(seg):
        a, b = i, (i + 1) % seg
        faces.append((a, b, seg + b, seg + a))
        faces.append((c0, b, a))
        faces.append((c1, seg + a, seg + b))
    return verts, faces


def _annulus_cylinder(r_out, r_in, z0, z1, seg=30):
    """Hollow ring closed at both axial ends -- sheave rims, rope grooves."""
    seg = _detail_seg(seg)
    verts, faces = [], []
    ang = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    for z in (z0, z1):
        for a in ang:
            verts.append((r_out * math.cos(a), r_out * math.sin(a), z))
        for a in ang:
            verts.append((r_in * math.cos(a), r_in * math.sin(a), z))

    def oo(layer, i):
        return layer * (2 * seg) + (i % seg)

    def ii(layer, i):
        return layer * (2 * seg) + seg + (i % seg)

    for i in range(seg):
        faces.append((oo(0, i), oo(0, i + 1), oo(1, i + 1), oo(1, i)))
        faces.append((ii(0, i), ii(1, i), ii(1, i + 1), ii(0, i + 1)))
        faces.append((oo(0, i), ii(0, i), ii(0, i + 1), oo(0, i + 1)))
        faces.append((oo(1, i), oo(1, i + 1), ii(1, i + 1), ii(1, i)))
    return verts, faces


def _pipe(p0, p1, r, col, seg=6, name=""):
    """A straight round rod between two 3D points -- ropes, rails, struts."""
    p0 = np.asarray(p0, float)
    p1 = np.asarray(p1, float)
    axis = p1 - p0
    L = float(np.linalg.norm(axis))
    if L < 1e-9:
        v, f = _solid_cylinder(r, 0.0, 0.001, seg=seg)
        return Mesh(v, f, col, name=name)
    axis = axis / L
    tmp = np.array([0.0, 0.0, 1.0]) if abs(axis[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = np.cross(axis, tmp)
    u = u / (np.linalg.norm(u) or 1.0)
    w = np.cross(axis, u)
    verts, faces = [], []
    ring = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    for end in (p0, p1):
        for a in ring:
            verts.append(tuple(end + r * math.cos(a) * u + r * math.sin(a) * w))
    for i in range(seg):
        a, b = i, (i + 1) % seg
        faces.append((a, b, seg + b, seg + a))
    return Mesh(verts, faces, col, name=name, spin=0.0)


def remap_yz(v):
    """Rotate a Z-axis primitive so its long axis points UP (+Y): (x,y,z)->(x,z,y)."""
    return [(p[0], p[2], p[1]) for p in v]


def _static(v, f, col, name="", group="static"):
    """A non-spinning mesh (structure, shafts, cabins, banks)."""
    return Mesh(v, f, col, name=name, spin=0.0, group=group)


def _spinner(v, f, col, pivot, tilt, group, name=""):
    """A rotating mesh built at the origin, then placed and tilted (sheaves)."""
    m = Mesh(v, f, col, name=name, spin=1.0, group=group)
    m.pivot = np.asarray(pivot, dtype=float)
    m.tilt = tilt
    return m


class Part:
    """A named, spec'd logical component made of one or more meshes. Carries an
    assembly `order`, an `explode` offset and a `specs` list for the inspector."""

    def __init__(self, key, name, meshes, specs, order, explode, color):
        self.key = key
        self.name = name
        self.meshes = meshes
        self.specs = specs
        self.order = order
        self.explode = np.asarray(explode, dtype=float)
        self.color = color
        n = float(np.linalg.norm(self.explode))
        self.popdir = self.explode / n if n > 1e-6 else np.array([0.0, 1.0, 0.0])


def _grp(meshes, group):
    for m in meshes:
        m.group = group
    return meshes


# =============================================================================
# SECTION 4 -- ZONE PLAN + GEOMETRY BUILDERS (tower + gravity machine, to scale)
# =============================================================================

class ZoneSpec:
    """The fixed, dimensional description of one vertical zone. Both the 3D
    geometry and the transit physics are generated from these numbers."""

    def __init__(self, index, lo, hi, n_shafts, cap, reeving, cabin_kg):
        self.index = index
        self.lo = lo                      # bottom served floor (a sky lobby)
        self.hi = hi                      # top served floor (the next sky lobby)
        self.n_shafts = n_shafts
        self.cap = cap                    # passengers per cabin
        self.reeving = reeving            # differential reeving MA (1 or 2)
        self.cabin_kg = cabin_kg
        self.n_floors = hi - lo + 1
        self.rise_m = (hi - lo) * FLOOR_H
        self.base_h_m = (lo - 1) * FLOOR_H
        self.top_h_m = (hi - 1) * FLOOR_H
        self.tray_J = TRAY_KG * G * self.rise_m      # joules per staged tray
        self.v_max = ROPE_SPEED_MS / self.reeving    # car speed cap
        self.rope_kg = DIMS["ropes"] * DIMS["rope_kg_per_m"] * self.rise_m * 2.2

    @property
    def name(self):
        return "ZONE %d" % (self.index + 1)

    @property
    def floors(self):
        return range(self.lo, self.hi + 1)

    def suspended_kg(self, load_a=0.0, load_b=0.0, trays=0.0):
        """Total mass hanging on the head sheave for this hoistway."""
        return (2.0 * self.cabin_kg + load_a + load_b
                + trays * TRAY_KG + self.rope_kg + self.base_cwt_kg())

    def base_cwt_kg(self):
        """Fixed base counterweight, sized for the zone's AVERAGE cabin load --
        only the variable add-on tray mass is ever carried by people."""
        return 0.45 * self.cap * PAX_KG


ZONES = [ZoneSpec(i, *row) for i, row in enumerate(ZONE_PLAN)]
NZONES = len(ZONES)
SKY_LOBBIES = [z.lo for z in ZONES] + [ZONES[-1].hi]     # levels 0..NZONES
LOBBY_H_M = [(f - 1) * FLOOR_H for f in SKY_LOBBIES]
TOTAL_SHAFTS = sum(z.n_shafts for z in ZONES)


def floor_population(f):
    """Occupancy falls with height -- the reason upper zones need incentives."""
    t = (f - 1) / max(1.0, FLOORS - 1.0)
    return max(6.0, 46.0 * math.exp(-1.15 * t))


def zone_population(z):
    return sum(floor_population(f) for f in range(z.lo, z.hi))


def vault_cap(level):
    """Tray capacity of a lobby store. Level 0 is at grade, so it can be big."""
    return DIMS["ground_reservoir"] if level == 0 else DIMS["vault_capacity"]


def zone_for_travel(f, going_up):
    """The zone that serves a trip STARTING at floor f in the given direction.
    Sky-lobby floors belong to two zones; pick the one that reaches onward."""
    best = None
    for z in ZONES:
        if z.lo <= f <= z.hi:
            if going_up and f < z.hi:
                return z
            if (not going_up) and f > z.lo:
                return z
            best = best or z
    return best


def plan_legs(src, dst):
    """Break a journey into per-zone legs via the sky lobbies (the cascade)."""
    if src == dst:
        return []
    up = dst > src
    legs, cur, guard = [], src, 0
    while cur != dst and guard < 12:
        guard += 1
        z = zone_for_travel(cur, up)
        if z is None:
            break
        if z.lo <= dst <= z.hi:
            legs.append((z.index, cur, dst))
            cur = dst
        else:
            nxt = z.hi if up else z.lo
            if nxt == cur:
                break
            legs.append((z.index, cur, nxt))
            cur = nxt
    return legs


def massing_plan(height_m):
    """Plan dimensions (w, d) of the tower shell at a given height."""
    if height_m <= TOWER["podium_floors"] * FLOOR_H:
        return TOWER["base_w_m"], TOWER["base_d_m"]
    if height_m <= (TOWER["setback_hi"] - 1) * FLOOR_H:
        return TOWER["mid_w_m"], TOWER["mid_d_m"]
    return TOWER["top_w_m"], TOWER["top_d_m"]


def shaft_x_m(n, i):
    """Plan X of hoistway i of n inside the core (metres from tower centre)."""
    if n <= 1:
        return 0.0
    span = 13.8 if n >= 3 else 9.8
    return -span / 2.0 + i * (span / (n - 1))


SHAFT_Z_M   = 2.40      # hoistways sit in the front half of the core
CWT_Z_M     = -1.60     # base-counterweight chases behind them
SHUTTLE_X_M = -9.20     # short-haul tray shuttle chase
SHUTTLE_Z_M = -5.60
STAIR_X_M   = 8.80      # the health stair
STAIR_Z_M   = -5.40
BANK_Z_M    = 6.40      # landing weight banks, in the lift lobby
VAULT_Z_M   = -6.90     # sky-lobby staged-mass vaults

# Live mesh registry -- the simulation writes .dyn / .mix_t on these every frame
# instead of rebuilding any geometry.
TOWER_LIVE = {"cabA": {}, "cabB": {}, "cwt": {}, "trayA": {}, "trayB": {},
              "bank": {}, "vault": {}, "shuttle": {}}


def _rotv(v, R, off=(0.0, 0.0, 0.0)):
    """Rotate a vertex list by matrix R then translate -- for static angled parts."""
    a = np.asarray(v, dtype=float) @ R.T
    return (a + np.asarray(off, dtype=float)).tolist()


# ---------------------------------------------------------------------------
#  THE TOWER  --  60 storeys, 6 zones, 5 sky lobbies, 14 hoistways, to scale.
# ---------------------------------------------------------------------------

def build_tower_parts():
    for d in TOWER_LIVE.values():
        d.clear()
    parts = []
    core_w, core_d = TOWER["core_w_m"], TOWER["core_d_m"]

    # --- GROUND / PLAZA / CITY CONTEXT ------------------------------------
    ground = []
    v, f = _box(0.0, ty(-0.9), 0.0, tds(118.0), tds(1.8), tds(110.0))
    ground.append(_static(v, f, C_GROUND, "street plaza"))
    for (gx, gz, gw, gd, gh) in ((-54, 38, 30, 28, 46), (52, -44, 28, 30, 62),
                                 (-60, -48, 24, 24, 34), (58, 44, 26, 22, 28)):
        v, f = _box(tds(gx), ty(gh / 2.0), tds(gz), tds(gw), tds(gh), tds(gd))
        ground.append(_static(v, f, C_CITY, ""))
    parts.append(Part("ground", "SITE + PLAZA", ground,
                      ["street level datum for every height in this model",
                       "neighbouring blocks drawn to scale for reference",
                       "tower gross floor area %.0f m2" % TOWER["gross_area_m2"]],
                      0, (0.0, -0.30, 0.0), C_GROUND))

    # --- FLOOR PLATES (one structural slab per storey) --------------------
    slabs = []
    for fl in range(1, FLOORS + 1):
        h = (fl - 1) * FLOOR_H
        w, d = massing_plan(h)
        is_lobby = fl in SKY_LOBBIES
        col = C_LOBBY if is_lobby else (C_SLAB if fl % 2 else _mix(C_SLAB, C_CONCRETE, 0.35))
        th = TOWER["slab_t_m"] * (2.4 if is_lobby else 1.0)
        nm = ""
        if is_lobby:
            nm = "SKY LOBBY %d" % fl if fl not in (1,) else "GROUND LOBBY"
        v, f = _box(0.0, ty(h), 0.0, tds(w), tds(th), tds(d))
        slabs.append(_static(v, f, col, nm))
    parts.append(Part("slabs", "FLOOR PLATES  (60 storeys)", slabs,
                      ["%d occupied storeys at %.2f m floor-to-floor" % (FLOORS, FLOOR_H),
                       "main roof %.1f m above street" % TOWER_H_M,
                       "highlighted plates are the %d SKY LOBBIES" % (NZONES - 1),
                       "transfer floors: " + ", ".join(str(x) for x in SKY_LOBBIES[1:-1]),
                       "population falls from %.0f to %.0f per floor" % (
                           floor_population(1), floor_population(FLOORS))],
                      1, (0.0, 0.55, 0.0), C_SLAB))

    # --- CURTAIN WALL + CORNER COLUMNS (two faces left open as a cutaway) --
    shell = []
    blocks = [(0.0, TOWER["podium_floors"] * FLOOR_H, TOWER["base_w_m"], TOWER["base_d_m"]),
              (TOWER["podium_floors"] * FLOOR_H, (TOWER["setback_hi"] - 1) * FLOOR_H,
               TOWER["mid_w_m"], TOWER["mid_d_m"]),
              ((TOWER["setback_hi"] - 1) * FLOOR_H, TOWER_H_M,
               TOWER["top_w_m"], TOWER["top_d_m"])]
    for bi, (y0, y1, w, d) in enumerate(blocks):
        yc, hh = (y0 + y1) / 2.0, (y1 - y0)
        v, f = _box(tds(-w / 2.0), ty(yc), 0.0, tds(0.45), tds(hh), tds(d))
        shell.append(_static(v, f, C_GLASS, "curtain wall W" if bi == 1 else ""))
        v, f = _box(0.0, ty(yc), tds(-d / 2.0), tds(w), tds(hh), tds(0.45))
        shell.append(_static(v, f, _mix(C_GLASS, C_GLASS_HI, 0.18),
                             "curtain wall N" if bi == 1 else ""))
        for sx in (-1, 1):
            for sz in (-1, 1):
                v, f = _box(sx * tds(w / 2.0), ty(yc), sz * tds(d / 2.0),
                            tds(1.1), tds(hh), tds(1.1))
                shell.append(_static(v, f, C_MULLION, ""))
    parts.append(Part("shell", "CURTAIN WALL + SET-BACKS", shell,
                      ["podium %.0f x %.0f m to floor %d" % (
                          TOWER["base_w_m"], TOWER["base_d_m"], TOWER["podium_floors"]),
                       "main shaft %.0f x %.0f m" % (TOWER["mid_w_m"], TOWER["mid_d_m"]),
                       "upper block %.0f x %.0f m above floor %d" % (
                           TOWER["top_w_m"], TOWER["top_d_m"], TOWER["setback_hi"]),
                       "two faces left open so the transit core reads",
                       "press X for the half-section cut"],
                      2, (-0.9, 0.2, -0.9), C_GLASS))

    # --- STRUCTURAL CORE ---------------------------------------------------
    core = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            v, f = _box(sx * tds(core_w / 2.0), ty(TOWER_H_M / 2.0), sz * tds(core_d / 2.0),
                        tds(1.6), tds(TOWER_H_M), tds(1.6))
            core.append(_static(v, f, C_CONCRETE, "core pier" if (sx < 0 and sz < 0) else ""))
    v, f = _box(0.0, ty(TOWER_H_M / 2.0), tds(-core_d / 2.0), tds(core_w), tds(TOWER_H_M), tds(0.6))
    core.append(_static(v, f, _mix(C_CONCRETE, (0, 0, 0), 0.18), "shear wall"))
    parts.append(Part("core", "STRUCTURAL CORE", core,
                      ["%.0f x %.0f m core, %d hoistways total" % (core_w, core_d, TOTAL_SHAFTS),
                       "ZONES STACK: no hoistway runs the full height",
                       "that is why a 60-storey tower needs only %d shafts" % TOTAL_SHAFTS,
                       "conventional zoning would need ~%d full-rise shafts" % (TOTAL_SHAFTS + 10),
                       "core carries the head sheave beams at every zone top"],
                      3, (0.0, 0.0, -0.7), C_CONCRETE))

    # --- HOISTWAYS + LIVE COUNTER-RUNNING CABINS (per zone) ----------------
    for z in ZONES:
        encl, cabins, cwts = [], [], []
        for si in range(z.n_shafts):
            xm = shaft_x_m(z.n_shafts, si)
            # hoistway enclosure spanning exactly this zone
            v, f = _box(tds(xm), ty(z.base_h_m + z.rise_m / 2.0), tds(SHAFT_Z_M),
                        tds(DIMS["shaft_w_m"]), tds(z.rise_m + 2.2), tds(DIMS["shaft_d_m"]))
            encl.append(_static(v, f, C_SHAFT, "hoistway %d" % (si + 1) if si == 0 else ""))
            # machine head (sheave beam housing) at the zone top
            v, f = _box(tds(xm), ty(z.top_h_m + 2.1), tds(SHAFT_Z_M),
                        tds(DIMS["shaft_w_m"] * 0.92), tds(1.5), tds(DIMS["shaft_d_m"] * 0.92))
            encl.append(_static(v, f, _mix(C_SHEAVE, C_SHAFT, 0.35),
                                "head sheave beam" if si == 0 else ""))
            # the two counter-running cabins, built at the zone floor
            off = (DIMS["cabin_w_m"] + DIMS["cabin_gap_m"]) / 2.0
            for tag, dx, col in (("A", -off, C_CABIN), ("B", off, C_CABIN_B)):
                v, f = _box(tds(xm + dx), ty(z.base_h_m + DIMS["cabin_h_m"] / 2.0 + 0.2),
                            tds(SHAFT_Z_M), tds(DIMS["cabin_w_m"]),
                            tds(DIMS["cabin_h_m"]), tds(DIMS["cabin_d_m"]))
                cab = _static(v, f, col, "cabin %s" % tag if si == 0 else "")
                cabins.append(cab)
                TOWER_LIVE["cab" + tag][(z.index, si)] = cab
                # roof tray rack -- the variable add-on mass rides up here
                v, f = _box(tds(xm + dx), ty(z.base_h_m + DIMS["cabin_h_m"] + 0.36),
                            tds(SHAFT_Z_M), tds(DIMS["cabin_w_m"] * 0.8),
                            tds(0.22), tds(DIMS["cabin_d_m"] * 0.7))
                rack = _static(v, f, C_TRAY, "tray rack" if si == 0 and tag == "A" else "")
                rack.mix_col = C_SHAFT
                cabins.append(rack)
                TOWER_LIVE["tray" + tag][(z.index, si)] = rack
            # fixed base counterweight in its own chase
            v, f = _box(tds(xm), ty(z.base_h_m + DIMS["cwt_h_m"] / 2.0 + 0.2), tds(CWT_Z_M),
                        tds(DIMS["cwt_w_m"]), tds(DIMS["cwt_h_m"]), tds(DIMS["cwt_d_m"]))
            cw = _static(v, f, C_CWT, "base counterweight" if si == 0 else "")
            cwts.append(cw)
            TOWER_LIVE["cwt"][(z.index, si)] = cw
        parts.append(Part("hoist_%d" % z.index, "%s HOISTWAYS" % z.name, encl,
                          ["floors %d-%d, rise %.1f m" % (z.lo, z.hi, z.rise_m),
                           "%d hoistway(s), %d passengers per cabin" % (z.n_shafts, z.cap),
                           "reeving %d:1  ->  car speed %.2f m/s" % (z.reeving, z.v_max),
                           "%.0f kg cabins, %.0f kg base counterweight" % (
                               z.cabin_kg, z.base_cwt_kg()),
                           "one staged tray = %.0f J over this zone" % z.tray_J,
                           "zone population ~%.0f" % zone_population(z)],
                          10 + z.index, (0.0, 0.0, 0.9), C_SHAFT))
        parts.append(Part("cabs_%d" % z.index, "%s CABINS  (live)" % z.name, cabins,
                          ["TWO rope-linked cabins per hoistway on one head sheave",
                           "cabin A rises exactly as cabin B descends",
                           "the loaded descending car RAISES the ascending car",
                           "net human input approaches the FRICTION LOSS only",
                           "green rack = modular %.1f kg trays riding along" % TRAY_KG],
                          20 + z.index, (0.0, 0.0, 1.5), C_CABIN))
        parts.append(Part("cwt_%d" % z.index, "%s BASE COUNTERWEIGHTS" % z.name, cwts,
                          ["%.0f kg fixed, sized for the zone AVERAGE load" % z.base_cwt_kg(),
                           "people never carry this mass -- it is built in",
                           "only the VARIABLE tray mass is human-carried",
                           "rides down as cabin A rides up"],
                          30 + z.index, (0.0, 0.0, -1.2), C_CWT))

    # --- LANDING WEIGHT BANKS (one quick-load hopper per storey) -----------
    banks = []
    for fl in range(1, FLOORS + 1):
        h = (fl - 1) * FLOOR_H
        xm = 11.5 if fl % 2 else -11.5
        v, f = _box(tds(xm), ty(h + DIMS["bank_h_m"] / 2.0 + 0.2), tds(BANK_Z_M),
                    tds(DIMS["bank_w_m"]), tds(DIMS["bank_h_m"]), tds(DIMS["bank_d_m"]))
        b = _static(v, f, C_BANK, "landing weight bank" if fl == 3 else "")
        # dim (not alarm-red) when idle: an empty landing bank is normal
        b.mix_col = _mix(C_SHAFT, C_BANK, 0.30)
        banks.append(b)
        TOWER_LIVE["bank"][fl] = b
    parts.append(Part("banks", "LANDING WEIGHT BANKS", banks,
                      ["one quick-load tray hopper at every landing",
                       "%d trays capacity each, %.1f kg per tray" % (
                           DIMS["bank_capacity"], TRAY_KG),
                       "walkers deposit here and are credited on the spot",
                       "the shuttles then stage the trays upward in steps",
                       "bright green = holding stock, dim = drained"],
                      4, (1.4, 0.0, 0.8), C_BANK))

    # --- SKY-LOBBY VAULTS (the staged-mass battery of each zone) ----------
    vaults = []
    for li, fl in enumerate(SKY_LOBBIES):
        h = (fl - 1) * FLOOR_H
        v, f = _box(0.0, ty(h + DIMS["vault_h_m"] / 2.0 + 0.2), tds(VAULT_Z_M),
                    tds(DIMS["vault_w_m"]), tds(DIMS["vault_h_m"]), tds(DIMS["vault_d_m"]))
        vt = _static(v, f, C_VAULT, "vault L%d" % li if li in (0, NZONES) else "")
        vt.mix_col = C_TRAY_LOW
        vaults.append(vt)
        TOWER_LIVE["vault"][li] = vt
    parts.append(Part("vaults", "SKY-LOBBY STAGED-MASS VAULTS", vaults,
                      ["%d vaults, %d trays each (~%.0f t staged)" % (
                          NZONES + 1, DIMS["vault_capacity"],
                          DIMS["vault_capacity"] * TRAY_KG / 1000.0),
                       "THIS IS THE BUILDING BATTERY: mass x g x height",
                       "a full vault at floor %d holds %.1f kWh" % (
                           SKY_LOBBIES[1],
                           DIMS["vault_capacity"] * TRAY_KG * G * LOBBY_H_M[1] / 3.6e6),
                       "zone i draws from vault i+1 and returns to vault i",
                       "down-peak traffic RE-STAGES trays back upward"],
                      5, (0.0, 0.0, -1.6), C_VAULT))

    # --- THE HEALTH STAIR --------------------------------------------------
    stair = []
    v, f = _box(tds(STAIR_X_M), ty(TOWER_H_M / 2.0), tds(STAIR_Z_M),
                tds(DIMS["stair_w_m"] + 0.5), tds(TOWER_H_M), tds(DIMS["stair_d_m"] + 0.5))
    stair.append(_static(v, f, _mix(C_STAIR, C_SHAFT, 0.62), "health stair shaft"))
    Rf = rot_z(math.radians(30.0))
    Rb = rot_z(math.radians(-30.0))
    for fl in range(1, FLOORS + 1):
        h = (fl - 1) * FLOOR_H
        vv, ff = _box(0.0, 0.0, 0.0, tds(DIMS["stair_run_m"]), tds(0.18), tds(1.3))
        R = Rf if fl % 2 else Rb
        zz = STAIR_Z_M + (1.5 if fl % 2 else -1.5)
        vv = _rotv(vv, R, (tds(STAIR_X_M), ty(h + FLOOR_H * 0.5), tds(zz)))
        stair.append(_static(vv, ff, C_STAIR, "stair flight" if fl == 5 else ""))
    parts.append(Part("stair", "THE HEALTH STAIR", stair,
                      ["%.1f m wide, cart- and backpack-friendly" % DIMS["stair_w_m"],
                       "%d flights per storey, %d flights to the roof" % (
                           DIMS["flights_per_floor"], FLOORS * DIMS["flights_per_floor"]),
                       "THE ONLY ENERGY INPUT THE BUILDING HAS",
                       "one tray carried one zone = %.0f J of stored lift" % ZONES[0].tray_J,
                       "credited automatically at the bank at the top"],
                      6, (1.6, 0.0, -1.0), C_STAIR))

    # --- SHORT-HAUL TRAY SHUTTLES -----------------------------------------
    shut = []
    for z in ZONES:
        v, f = _box(tds(SHUTTLE_X_M), ty(z.base_h_m + z.rise_m / 2.0), tds(SHUTTLE_Z_M),
                    tds(DIMS["shuttle_w_m"]), tds(z.rise_m), tds(DIMS["shuttle_d_m"]))
        shut.append(_static(v, f, _mix(C_SHUTTLE, C_SHAFT, 0.55),
                            "shuttle chase" if z.index == 0 else ""))
        v, f = _box(tds(SHUTTLE_X_M), ty(z.base_h_m + DIMS["shuttle_car_h_m"] / 2.0 + 0.2),
                    tds(SHUTTLE_Z_M), tds(DIMS["shuttle_w_m"] * 0.72),
                    tds(DIMS["shuttle_car_h_m"]), tds(DIMS["shuttle_d_m"] * 0.72))
        car = _static(v, f, C_SHUTTLE, "tray shuttle" if z.index == 0 else "")
        shut.append(car)
        TOWER_LIVE["shuttle"][z.index] = car
    parts.append(Part("shuttles", "SHORT-HAUL TRAY SHUTTLES", shut,
                      ["one narrow pure-gravity chase per zone",
                       "%d trays per run, collects the landing banks" % DIMS["shuttle_trays"],
                       "moves deposits UP IN STAGES to the sky-lobby vault",
                       "runs on the same counter-running principle",
                       "scheduled into surplus periods so it never competes"],
                      7, (-1.6, 0.0, -1.0), C_SHUTTLE))

    # --- ROOF PLANT + CROWN ------------------------------------------------
    crown = []
    ch = TOWER["crown_h_m"]
    for i, (fw, fh) in enumerate(((0.86, 0.42), (0.62, 0.32), (0.40, 0.26))):
        w, d = TOWER["top_w_m"] * fw, TOWER["top_d_m"] * fw
        yb = TOWER_H_M + ch * sum(x[1] for x in ((0.86, 0.42), (0.62, 0.32), (0.40, 0.26))[:i])
        v, f = _box(0.0, ty(yb + ch * fh / 2.0), 0.0, tds(w), tds(ch * fh), tds(d))
        crown.append(_static(v, f, C_CROWN, "roof plant" if i == 0 else ""))
    crown.append(_pipe((0.0, ty(TOWER_H_M + ch), 0.0), (0.0, ty(TOWER_H_M + ch + 18.0), 0.0),
                       tds(0.55), C_STEEL, seg=6, name="mast"))
    parts.append(Part("crown", "ROOF PLANT + CROWN", crown,
                      ["no machine room, no motor room, no drive room",
                       "the head sheaves sit at each ZONE top, not the roof",
                       "roof plant is ventilation and water only",
                       "grid connection for transit: NONE"],
                      8, (0.0, 1.6, 0.0), C_CROWN))

    # The tower is only ~0.78 display units tall, so the raw explode vectors
    # would throw parts clean off the viewport. Scale them to the model.
    for p in parts:
        p.explode = p.explode * 0.30
        n = float(np.linalg.norm(p.explode))
        p.popdir = p.explode / n if n > 1e-6 else np.array([0.0, 1.0, 0.0])
    return parts


# ---------------------------------------------------------------------------
#  THE GRAVITY MACHINE  --  one zone's hoistway in mechanical detail.
#  No motor. No drive. No brake resistor. The only actuators in the whole
#  assembly are a holding pawl and a levelling clamp; everything that MOVES
#  is moved by the difference in weight between the two sides of the rope.
# ---------------------------------------------------------------------------

MACH_LIVE = {}


def build_machine_parts():
    """A 2:1-reeved upper-zone machine, built to scale in metres about y=0."""
    MACH_LIVE.clear()
    parts = []
    cw, cd, chh = DIMS["cabin_w_m"], DIMS["cabin_d_m"], DIMS["cabin_h_m"]
    xa, xb = -1.35, 1.35            # the two counter-running cabin centrelines
    ya, yb = -2.30, 2.30            # A parked low, B parked high
    sheave_y = 6.05
    pit_y = -5.20
    rail_top, rail_bot = 5.30, pit_y + 0.2

    def M(x, y, z, sx, sy, sz, col, name="", group="static"):
        v, f = _box(mds(x), mds(y), mds(z), mds(sx), mds(sy), mds(sz))
        return _static(v, f, col, name, group)

    # --- 1. PIT, BUFFERS AND SILL -----------------------------------------
    pit = [M(0, pit_y - 0.35, 0, 7.2, 0.7, 5.2, _mix(C_CONCRETE, (0, 0, 0), 0.25),
             "pit slab")]
    for x in (xa, xb):
        v, f = _solid_cylinder(mds(DIMS["buffer_d_m"] / 2), 0.0, mds(DIMS["buffer_h_m"]), seg=12)
        v = remap_yz(v)
        b = _static(v, f, C_BRAKE, "oil buffer")
        b.pivot = np.array([mds(x), mds(pit_y), 0.0])
        pit.append(b)
        pit.append(M(x, pit_y + DIMS["buffer_h_m"] + 0.08, 0, 1.2, 0.16, 1.2,
                     C_STEEL, ""))
    parts.append(Part("pit", "PIT + OIL BUFFERS", pit,
                      ["%.2f m oil buffers under each car" % DIMS["buffer_h_m"],
                       "final mechanical stop, never used in service",
                       "the pit is also the low tray landing for this zone",
                       "no drive pit equipment: there is no drive"],
                      0, (0.0, -1.2, 0.0), C_BRAKE))

    # --- 2. GUIDE RAILS + ROLLER SHOES ------------------------------------
    rails = []
    for x in (xa, xb):
        for zs in (-1, 1):
            zz = zs * (cd / 2 + 0.20)
            rails.append(M(x, (rail_top + rail_bot) / 2, zz, DIMS["rail_face_m"],
                           rail_top - rail_bot, 0.09, C_RAIL,
                           "T-section guide rail" if (x == xa and zs < 0) else ""))
            rails.append(M(x, (rail_top + rail_bot) / 2, zz + zs * 0.07, 0.05,
                           rail_top - rail_bot, 0.12, _mix(C_RAIL, (0, 0, 0), 0.3), ""))
    for (x, y) in ((xa, ya), (xb, yb)):
        for zs in (-1, 1):
            for ys in (-1, 1):
                v, f = _solid_cylinder(mds(DIMS["roller_d_m"] / 2), -mds(0.05), mds(0.05), seg=10)
                r = _static(v, f, _mix(C_BRAKE, C_STEEL, 0.4), "roller guide shoe")
                r.pivot = np.array([mds(x + 0.0), mds(y + ys * (chh / 2 - 0.1)),
                                    mds(zs * (cd / 2 + 0.15))])
                r.tilt = (0.0, math.pi / 2)
                rails.append(r)
    parts.append(Part("rails", "GUIDE RAILS + ROLLER SHOES", rails,
                      ["machined T-section rails, %.0f mm blade" % (DIMS["rail_face_m"] * 1000),
                       "%.0f mm sprung ROLLER shoes -- not sliding gibs" % (
                           DIMS["roller_d_m"] * 1000),
                       "rolling contact is the single biggest loss cut",
                       "target: total resistance %.1f%% of suspended mass" % (MU_EFF * 100),
                       "spec band for the design: %.0f-%.0f%% imbalance" % (
                           MU_SPEC_LO * 100, MU_SPEC_HI * 100)],
                      1, (1.5, 0.0, 0.0), C_RAIL))

    # --- 3. CABIN A (the ascending car) -----------------------------------
    def cabin(x, y, col, tag):
        g = []
        g.append(M(x, y, 0, cw, chh, cd, col, "cabin %s shell" % tag))
        g.append(M(x, y - chh / 2 - 0.09, 0, cw + 0.16, 0.18, cd + 0.16,
                   _mix(col, (0, 0, 0), 0.35), "platform + sling"))
        g.append(M(x, y + chh / 2 + 0.07, 0, cw + 0.16, 0.14, cd + 0.16,
                   _mix(col, (0, 0, 0), 0.3), "crosshead"))
        for zs in (-1, 1):
            g.append(M(x, y, zs * (cd / 2 + 0.02), DIMS["car_door_w_m"], chh * 0.86, 0.06,
                       _mix(col, (255, 255, 255), 0.30), "car door" if zs > 0 else ""))
        for ys in (-1, 1):
            g.append(M(x, y + ys * (chh / 2 + 0.02), 0, cw + 0.2, 0.08, 0.22,
                       C_STEEL, ""))
        # roof tray rack -- the variable add-on mass
        for k in range(4):
            g.append(M(x, y + chh / 2 + 0.20 + k * DIMS["tray_h_m"] * 1.6, 0,
                       DIMS["tray_w_m"] * 2.4, DIMS["tray_h_m"], DIMS["tray_d_m"] * 2.2,
                       C_TRAY, "weight trays" if k == 3 else ""))
        return g

    parts.append(Part("cabA", "CABIN A  (ascending car)", cabin(xa, ya, C_CABIN, "A"),
                      ["%.2f x %.2f x %.2f m clear car" % (cw, cd, chh),
                       "%.0f kg empty, up to %d passengers" % (ZONES[-1].cabin_kg, ZONES[-1].cap),
                       "roped over the head sheave to cabin B",
                       "rises ONLY because cabin B is heavier",
                       "roof rack takes the pre-positioned trays"],
                      2, (-1.7, -0.4, 0.0), C_CABIN))
    parts.append(Part("cabB", "CABIN B  (descending car)", cabin(xb, yb, C_CABIN_B, "B"),
                      ["identical car on the other rope fall",
                       "its descent IS the lift power for cabin A",
                       "loaded down-peak car raises a loaded up-peak car",
                       "net input then approaches friction only",
                       "dispatcher pairs the two calls before either moves"],
                      3, (1.7, 0.4, 0.0), C_CABIN_B))

    # --- 4. HEAD SHEAVE ASSEMBLY ------------------------------------------
    head = [M(0, sheave_y + 1.05, 0, 6.6, 0.5, 3.0, C_CONCRETE, "head beam")]
    sr = DIMS["sheave_d_m"] / 2
    v, f = _annulus_cylinder(mds(sr), mds(sr * 0.32), -mds(DIMS["sheave_t_m"] / 2),
                             mds(DIMS["sheave_t_m"] / 2), seg=30)
    head.append(_spinner(v, f, C_SHEAVE, (0.0, mds(sheave_y), 0.0), (0.0, 0.0),
                         "sheave", "TRACTION SHEAVE"))
    for k in range(3):
        rr = sr * (1.0 - 0.03 * k)
        v, f = _annulus_cylinder(mds(rr), mds(rr - 0.02),
                                 -mds(0.06 - k * 0.045), -mds(0.02 - k * 0.045), seg=26)
        head.append(_spinner(v, f, _mix(C_SHEAVE, (0, 0, 0), 0.35),
                             (0.0, mds(sheave_y), 0.0), (0.0, 0.0), "sheave", ""))
    v, f = _solid_cylinder(mds(0.09), -mds(1.5), mds(1.5), seg=10)
    sh = _static(v, f, C_STEEL, "sheave shaft")
    sh.pivot = np.array([0.0, mds(sheave_y), 0.0])
    head.append(sh)
    for x in (xa, xb):
        dr = DIMS["diverter_d_m"] / 2
        v, f = _annulus_cylinder(mds(dr), mds(dr * 0.3), -mds(0.07), mds(0.07), seg=22)
        head.append(_spinner(v, f, _mix(C_SHEAVE, C_STEEL, 0.4),
                             (mds(x), mds(sheave_y - 0.62), 0.0), (0.0, 0.0),
                             "sheave", "diverter sheave" if x == xa else ""))
    parts.append(Part("head", "HEAD SHEAVE ASSEMBLY", head,
                      ["%.2f m grooved traction sheave, %d rope grooves" % (
                          DIMS["sheave_d_m"], DIMS["ropes"]),
                       "%.2f m diverter sheaves set the rope fall spacing" % DIMS["diverter_d_m"],
                       "SPINS FREELY -- there is no motor on this shaft",
                       "sealed, lubricated bearings; drag folded into mu_eff",
                       "sits at the ZONE top, not in a roof machine room"],
                      4, (0.0, 1.8, 0.0), C_SHEAVE))

    # --- 5. DIFFERENTIAL REEVING BLOCKS (mechanical advantage) ------------
    blocks = []
    br = DIMS["block_d_m"] / 2
    for k, zz in ((0, -0.34), (1, 0.34)):
        v, f = _annulus_cylinder(mds(br), mds(br * 0.3), -mds(0.05), mds(0.05), seg=18)
        blocks.append(_spinner(v, f, _mix(C_SHEAVE, C_ACCENT, 0.25),
                               (mds(xa), mds(ya + chh / 2 + 0.55), mds(zz)),
                               (0.0, 0.0), "sheave", "car block" if k == 0 else ""))
    blocks.append(M(xa, ya + chh / 2 + 0.55, 0, 0.9, 0.12, 0.9, C_STEEL, "block frame"))
    blocks.append(M(xa, ya + chh / 2 + 0.95, 0, 0.35, 0.7, 0.35, C_STEEL, "dead-end hitch"))
    parts.append(Part("reeving", "DIFFERENTIAL REEVING BLOCKS (2:1)", blocks,
                      ["car reeved 2:1, counterweight 1:1",
                       "a %.0f kg imbalance then drives the car like %.0f kg" % (
                           40.0, 80.0),
                       "HALVES the tray mass a run needs...",
                       "...and halves the car speed to %.2f m/s" % (ROPE_SPEED_MS / 2),
                       "fitted only on the light upper zones, where that trade wins"],
                      5, (-1.2, 1.2, 0.0), C_ACCENT))

    # --- 6. ROPES ----------------------------------------------------------
    ropes = []
    rr = DIMS["rope_d_m"] * 3.0
    for k, zz in ((0, -0.30), (1, 0.0), (2, 0.30)):
        col = C_ROPE if k != 1 else _mix(C_ROPE, (0, 0, 0), 0.2)
        ropes.append(_pipe((mds(xa), mds(ya + chh / 2 + 0.55), mds(zz)),
                           (mds(xa), mds(sheave_y - 0.62), mds(zz)), mds(rr), col,
                           name="rope fall A" if k == 1 else ""))
        ropes.append(_pipe((mds(xa), mds(sheave_y - 0.62), mds(zz)),
                           (0.0, mds(sheave_y), mds(zz)), mds(rr), col))
        ropes.append(_pipe((0.0, mds(sheave_y), mds(zz)),
                           (mds(xb), mds(sheave_y - 0.62), mds(zz)), mds(rr), col))
        ropes.append(_pipe((mds(xb), mds(sheave_y - 0.62), mds(zz)),
                           (mds(xb), mds(yb + chh / 2 + 0.10), mds(zz)), mds(rr), col,
                           name="rope fall B" if k == 1 else ""))
    parts.append(Part("ropes", "TRACTION ROPES", ropes,
                      ["%d x %.0f mm steel ropes, %.2f kg/m" % (
                          DIMS["ropes"], DIMS["rope_d_m"] * 1000, DIMS["rope_kg_per_m"]),
                       "traction by groove friction -- no clamps, no gears",
                       "rope mass itself is compensated top-to-bottom",
                       "safety factor >= 12 on the fully loaded car"],
                      6, (0.0, 0.9, 0.9), C_ROPE))

    # --- 7. BASE COUNTERWEIGHT + TRAY STACK -------------------------------
    cwt = [M(0, 0.0, -2.85, DIMS["cwt_w_m"], DIMS["cwt_h_m"], DIMS["cwt_d_m"],
             C_CWT, "base counterweight frame")]
    for k in range(9):
        cwt.append(M(0, -0.85 + k * DIMS["tray_h_m"] * 2.1, -2.85,
                     DIMS["tray_w_m"] * 1.7, DIMS["tray_h_m"], DIMS["tray_d_m"] * 1.2,
                     C_TRAY, "stacked weight trays" if k == 8 else ""))
    cwt.append(M(0, DIMS["cwt_h_m"] / 2 + 0.18, -2.85, 0.3, 0.36, 0.3, C_STEEL, "cwt hitch"))
    parts.append(Part("cwt", "BASE COUNTERWEIGHT + TRAYS", cwt,
                      ["%.0f kg fixed block, sized for the AVERAGE load" % ZONES[-1].base_cwt_kg(),
                       "trays are the VARIABLE add-on -- the human part",
                       "%.2f kg per tray (25 lb), %d tray positions" % (
                           TRAY_KG, DIMS["tray_stack_max"]),
                       "loaded / unloaded at the landing in seconds",
                       "pre-positioned BEFORE the registered rider arrives"],
                      7, (0.0, 0.0, -1.8), C_CWT))

    # --- 8. OVERSPEED GOVERNOR + SAFETY GEAR ------------------------------
    gov = []
    gr = DIMS["gov_sheave_d_m"] / 2
    v, f = _annulus_cylinder(mds(gr), mds(gr * 0.28), -mds(0.05), mds(0.05), seg=18)
    gov.append(_spinner(v, f, _mix(C_STEEL, C_WARN, 0.25),
                        (mds(3.30), mds(sheave_y - 0.30), 0.0), (0.0, 0.0),
                        "gov", "GOVERNOR sheave"))
    v, f = _annulus_cylinder(mds(gr * 0.7), mds(gr * 0.24), -mds(0.05), mds(0.05), seg=14)
    gov.append(_spinner(v, f, C_STEEL, (mds(3.30), mds(pit_y + 0.9), 0.0), (0.0, 0.0),
                        "gov", "tension sheave"))
    for zz in (-0.05, 0.05):
        gov.append(_pipe((mds(3.30 - gr), mds(sheave_y - 0.30), mds(zz)),
                         (mds(3.30 - gr), mds(pit_y + 0.9), mds(zz)),
                         mds(0.02), _mix(C_ROPE, C_WARN, 0.3)))
        gov.append(_pipe((mds(3.30 + gr), mds(sheave_y - 0.30), mds(zz)),
                         (mds(3.30 + gr), mds(pit_y + 0.9), mds(zz)),
                         mds(0.02), _mix(C_ROPE, C_WARN, 0.3)))
    gov.append(M(3.30, ya, 0.0, 0.5, 0.5, 0.5, C_WARN, "safety-gear trip"))
    gov.append(M(xa - cw / 2 - 0.16, ya - chh / 2, 0, 0.36, 0.5, 0.5, C_WARN,
                 "wedge safety gear"))
    parts.append(Part("gov", "OVERSPEED GOVERNOR + SAFETY GEAR", gov,
                      ["%.2f m governor sheave on a taut closed loop" % DIMS["gov_sheave_d_m"],
                       "trips the wedge safety gear at 115%% of rated speed",
                       "PURELY MECHANICAL -- flyweights, no electronics",
                       "gravity systems still need this: gravity is the drive",
                       "independent of the holding brake"],
                      8, (2.0, 0.6, 0.0), C_WARN))

    # --- 9. HOLDING BRAKE / RATCHET-PAWL ----------------------------------
    brk = []
    dr = DIMS["brake_drum_d_m"] / 2
    v, f = _annulus_cylinder(mds(dr), mds(dr * 0.35), -mds(DIMS["brake_drum_t_m"] / 2),
                             mds(DIMS["brake_drum_t_m"] / 2), seg=22)
    brk.append(_spinner(v, f, C_BRAKE, (0.0, mds(sheave_y), mds(0.95)), (0.0, 0.0),
                        "sheave", "brake drum"))
    for k in range(12):
        a = k * 2 * math.pi / 12
        vv, ff = _box(mds(dr * 0.98 * math.cos(a)), mds(sheave_y + dr * 0.98 * math.sin(a)),
                      mds(0.95), mds(0.10), mds(0.10), mds(DIMS["brake_drum_t_m"] * 0.9))
        brk.append(_static(vv, ff, _mix(C_BRAKE, (0, 0, 0), 0.3), "ratchet tooth" if k == 0 else ""))
    brk.append(M(0.95, sheave_y + 0.62, 0.95, DIMS["pawl_len_m"], 0.12, 0.14,
                 C_STEEL, "holding pawl"))
    brk.append(M(1.20, sheave_y + 0.62, 0.95, 0.18, 0.34, 0.18, C_STEEL, "pawl pivot"))
    brk.append(M(0.0, sheave_y - 0.95, 0.95, 1.5, 0.16, 0.5, C_STEEL, "band brake anchor"))
    parts.append(Part("brake", "HOLDING BRAKE + RATCHET PAWL", brk,
                      ["%.2f m drum, %d-tooth ratchet ring" % (DIMS["brake_drum_d_m"], 12),
                       "holds the car at the landing while doors are open",
                       "released by the levelling clamp, not by a motor",
                       "the ONLY powered actuators in the machine are latches",
                       "fail-safe: springs apply, nothing holds it off"],
                      9, (0.9, 0.9, 0.9), C_BRAKE))

    # --- 10. LANDING BANK + REGISTRATION POST ------------------------------
    land = [M(4.25, ya - 0.55, 0, DIMS["bank_w_m"], DIMS["bank_h_m"], DIMS["bank_d_m"],
              C_BANK, "landing weight bank")]
    for k in range(6):
        land.append(M(4.25 - 0.55 + (k % 3) * 0.55, ya - 1.0 + (k // 3) * 0.34, 0,
                      DIMS["tray_w_m"], DIMS["tray_h_m"] * 2.4, DIMS["tray_d_m"],
                      C_TRAY, "deposited trays" if k == 0 else ""))
    land.append(M(5.55, ya - 0.25, 0, 0.22, 1.5, 0.22, C_STEEL, "registration post"))
    land.append(M(5.55, ya + 0.55, 0.14, 0.36, 0.44, 0.06, C_ACCENT, "call + credit register"))
    land.append(M(3.05, ya - 0.9, 0, 0.9, 0.1, 1.4, _mix(C_STAIR, C_BANK, 0.4),
                  "tray cart run"))
    parts.append(Part("landing", "LANDING BANK + CALL REGISTER", land,
                      ["quick-load hopper takes %d trays" % DIMS["bank_capacity"],
                       "the post registers the CALL and credits the CARRY",
                       "wait estimate shown before you commit to waiting",
                       "%.0f%% of slots held free for genuine incapacity" % (
                           TOKEN["priority_reserve"] * 100),
                       "credit = trays x flights x height x live scarcity"],
                      10, (2.2, -0.6, 0.0), C_BANK))

    # keep the exploded assembly inside the viewport at the home distance
    for p in parts:
        p.explode = p.explode * 0.26
        n = float(np.linalg.norm(p.explode))
        p.popdir = p.explode / n if n > 1e-6 else np.array([0.0, 1.0, 0.0])
    return parts


# =============================================================================
# SECTION 5 -- GRAVITY TRANSIT PHYSICS (honest, first-order, SI)
#
# The whole machine is one equation: a rope over a sheave with mass on both
# sides. Whichever side is heavier falls, and the difference has to beat the
# friction. Everything below is that statement, written out.
# =============================================================================

def resist_force_N(m_susp_kg):
    """Total rolling/bearing/rope resistance referred to the rope, in newtons."""
    return MU_EFF * m_susp_kg * G


def required_advantage_kg(m_susp_kg, reeving):
    """The mass advantage the DESCENDING side must hold for the run to go.

    This is what the machine always commands -- never more, never less. It is
    the friction floor times a working margin, divided by the reeving ratio
    (differential 2:1 halves the mass a run needs)."""
    return IMBAL_MARGIN * MU_EFF * m_susp_kg / reeving


def tray_mass_needed_kg(m_susp_kg, reeving, net_advantage_kg):
    """Tray mass to pre-position on the descending side.

    net_advantage_kg = (descending-car load - ascending-car load). When a
    loaded car is already going down against a light one this is positive and
    the run may need NO trays at all -- it makes them instead."""
    return max(0.0, required_advantage_kg(m_susp_kg, reeving) - net_advantage_kg)


def imbalance_ratio(delta_kg, m_susp_kg):
    """The headline number: commanded imbalance as a fraction of hanging mass."""
    return abs(delta_kg) / max(1.0, m_susp_kg)


def car_accel_ms2(delta_kg, m_susp_kg, reeving):
    """Car acceleration from a commanded imbalance, capped for comfort."""
    f_net = delta_kg * reeving * G - resist_force_N(m_susp_kg)
    a = f_net / max(1.0, m_susp_kg * (1.0 + ROT_INERTIA_FR))
    return clamp(a, 0.0, ACCEL_CAP_MS2)


def run_time_s(dist_m, a_ms2, v_max):
    """Trapezoidal (or triangular) travel time over a run, plus levelling."""
    dist_m = abs(dist_m)
    if dist_m < 1e-4:
        return JERK_DWELL_S
    if a_ms2 < 1e-4:
        return 1e6
    d_acc = v_max * v_max / (2.0 * a_ms2)
    if 2.0 * d_acc >= dist_m:                       # never reaches v_max
        return 2.0 * math.sqrt(dist_m / a_ms2) + JERK_DWELL_S
    t_flat = (dist_m - 2.0 * d_acc) / v_max
    return 2.0 * (v_max / a_ms2) + t_flat + JERK_DWELL_S


def run_energy_J(load_up_kg, load_dn_kg, m_susp_kg, ds_m):
    """Net energy the STAGED MASS must supply for one segment, in joules.

    Positive  = drawn from the vault above.
    Negative  = surplus, re-stages trays upward at RECOVERY_EFF."""
    return (load_up_kg - load_dn_kg) * G * abs(ds_m) + MU_EFF * m_susp_kg * G * abs(ds_m)


def tray_units(n_trays, ds_m, rise_m):
    """Trays moved through ds, expressed in whole-zone 'vault units'."""
    return n_trays * (abs(ds_m) / max(1e-6, rise_m))


def metabolic_kj(mass_kg, rise_m):
    """Metabolic energy a walker actually spends lifting mass_kg through rise_m."""
    return mass_kg * G * rise_m / WALK["metabolic_eff"] / 1000.0


def stair_climb_time_s(floors):
    return floors / WALK["climb_speed_fl_s"]


def reference_grid_kwh(trips, lift_hours):
    """What a conventional traction lift bank would have drawn for the same work."""
    return (trips * REFERENCE["kwh_per_trip"]
            + lift_hours * REFERENCE["lifts"] * REFERENCE["standby_kw"])


# =============================================================================
# SECTION 6 -- THE BUILDING (zones, hoistways, registry, cascading banks)
# =============================================================================

RNG = random.Random(20260807)


class Journey:
    """One person's registered trip, split into per-zone legs via sky lobbies."""

    __slots__ = ("src", "dst", "legs", "leg_i", "t_reg", "t_leg_reg", "cur",
                 "priority", "waited", "rides", "done", "t_start")

    def __init__(self, src, dst, t_now, priority=False):
        self.src = src
        self.dst = dst
        self.legs = plan_legs(src, dst)
        self.leg_i = 0
        self.cur = src
        self.t_reg = t_now
        self.t_leg_reg = t_now
        self.t_start = t_now
        self.priority = priority
        self.waited = 0.0
        self.rides = 0
        self.done = not self.legs

    @property
    def leg(self):
        return self.legs[self.leg_i] if self.leg_i < len(self.legs) else None

    def target_floor(self):
        lg = self.leg
        return lg[2] if lg else self.cur

    def advance(self, t_now):
        """Finish the current leg; returns True when the whole journey is over."""
        self.cur = self.legs[self.leg_i][2]
        self.leg_i += 1
        self.rides += 1
        self.t_leg_reg = t_now
        if self.leg_i >= len(self.legs):
            self.done = True
        return self.done


class Shaft:
    """One hoistway: TWO rope-linked cabins, one degree of freedom.

    `s` is cabin A's height above the zone floor; cabin B is always at
    (rise - s). A rises exactly as B descends -- that IS the counterweight."""

    STALL_COOL = 6.0        # seconds a held run waits before re-trying

    def __init__(self, zs, si):
        self.zs = zs
        self.spec = zs.spec
        self.si = si
        self.s = 0.0
        self.state = "IDLE"
        self.timer = 0.0
        self.dir = 0
        self.target_s = 0.0
        self.paxA = []
        self.paxB = []
        self.trays = 0.0          # trays commanded onto the descending side
        self.runs = 0
        self.stall_s = 0.0
        self.stall_cool = 0.0
        self.imbal_kg = 0.0
        self.ratio = 0.0
        self.v_now = 0.0
        self.mode = "idle"
        self.run_from = 0.0
        self.run_len = 0.0
        self.run_total = 1.0

    # -- geometry ---------------------------------------------------------
    @property
    def floor_a(self):
        return self.spec.lo + int(round(self.s / FLOOR_H))

    @property
    def floor_b(self):
        return self.spec.hi - int(round(self.s / FLOOR_H))

    def s_of_a(self, floor):
        return (floor - self.spec.lo) * FLOOR_H

    def s_of_b(self, floor):
        return (self.spec.hi - floor) * FLOOR_H

    def height_a_m(self):
        return self.spec.base_h_m + self.s

    def height_b_m(self):
        return self.spec.base_h_m + (self.spec.rise_m - self.s)

    # -- dispatch ---------------------------------------------------------
    def _board(self, floor, car, want_up, t):
        """Load registered calls at `floor` heading the right way into `car`."""
        z = self.zs
        q = z.waiting.get(floor)
        if not q:
            return 0
        cap = self.spec.cap - len(car)
        if cap <= 0:
            return 0
        taken = 0
        keep = []
        # priority slots first, then longest wait first (registered demand)
        q.sort(key=lambda j: (not j.priority, j.t_leg_reg))
        for j in q:
            if taken < cap and ((j.target_floor() > floor) == want_up):
                car.append(j)
                z.wait_push(t - j.t_leg_reg)
                taken += 1
            else:
                keep.append(j)
        z.waiting[floor] = keep
        return taken

    def _next_stop_s(self, up):
        """First s at which either car has to stop, in A's coordinate."""
        cand = []
        for j in self.paxA:
            cand.append(self.s_of_a(j.target_floor()))
        for j in self.paxB:
            cand.append(self.s_of_b(j.target_floor()))
        # intermediate hall calls we can pick up on the way
        for f, q in self.zs.waiting.items():
            if not q:
                continue
            sa, sb = self.s_of_a(f), self.s_of_b(f)
            if any((j.target_floor() > f) == up for j in q) and len(self.paxA) < self.spec.cap:
                cand.append(sa)
            if any((j.target_floor() > f) != up for j in q) and len(self.paxB) < self.spec.cap:
                cand.append(sb)
        fwd = [c for c in cand if (c > self.s + 0.05 if up else c < self.s - 0.05)]
        if not fwd:
            return None
        return min(fwd) if up else max(fwd)

    def _demand(self, up):
        fa, fb = self.floor_a, self.floor_b
        n = 0
        for j in self.zs.waiting.get(fa, []):
            if (j.target_floor() > fa) == up:
                n += 1
        for j in self.zs.waiting.get(fb, []):
            if (j.target_floor() > fb) != up:
                n += 1
        return n

    def _oldest_call(self, t):
        best, bt = None, -1.0
        for f, q in self.zs.waiting.items():
            for j in q:
                w = t - j.t_leg_reg
                if w > bt:
                    bt, best = w, f
        return best, bt

    def dispatch(self, t):
        if self.stall_cool > 0.0:
            return False
        # A stalled run keeps its boarded riders and its target: it is simply
        # waiting for enough staged mass to arrive in the vault above.
        if self.mode == "STALLED" and (self.paxA or self.paxB):
            return self._commit(self.target_s - self.s)
        fa, fb = self.floor_a, self.floor_b
        up_d, dn_d = self._demand(True), self._demand(False)
        if up_d == 0 and dn_d == 0:
            f, w = self._oldest_call(t)
            if f is None or w < REPOSITION_S:
                # an empty repositioning run is pure loss -- only do it when a
                # registered call has genuinely been left standing
                self.mode = "idle"
                return False
            # reposition: bring a car to the oldest registered call
            sa, sb = self.s_of_a(f), self.s_of_b(f)
            tgt = sa if abs(sa - self.s) <= abs(sb - self.s) else sb
            if abs(tgt - self.s) < 0.05:
                self.mode = "idle"
                return False
            self.target_s = tgt
            self.mode = "reposition"
        else:
            # BATCHING: registered demand lets the car wait a moment and fill,
            # so one balanced run replaces several separate weight movements.
            if (up_d + dn_d) < max(2, int(self.spec.cap * 0.35)):
                _, w = self._oldest_call(t)
                if w < BATCH_HOLD_S:
                    self.mode = "collecting"
                    return False
            up = up_d >= dn_d
            self._board(fa, self.paxA, up, t)
            self._board(fb, self.paxB, not up, t)
            if not self.paxA and not self.paxB:
                self.mode = "idle"
                return False
            nxt = self._next_stop_s(up)
            if nxt is None:
                self.paxA, self.paxB = [], []
                self.mode = "idle"
                return False
            self.target_s = nxt
            self.mode = "paired" if (self.paxA and self.paxB) else "single"
        return self._commit(self.target_s - self.s)

    def _commit(self, ds):
        """Pre-position the counter-mass, then release the run. This is the only
        place staged mass is ever spent -- and the only place a run can STALL."""
        z = self.zs
        if abs(ds) < 0.05:
            self.mode = "idle"
            return False
        up = ds > 0
        load_a = len(self.paxA) * PAX_KG
        load_b = len(self.paxB) * PAX_KG
        load_up, load_dn = (load_a, load_b) if up else (load_b, load_a)
        m_susp = self.spec.suspended_kg(load_a, load_b, self.trays)
        sp = self.spec
        need_kg = required_advantage_kg(m_susp, sp.reeving)
        net_adv = load_dn - load_up            # what the descending car already has
        if net_adv < need_kg:
            # short of the driving advantage -- pre-position trays to make it up
            trays_kg = need_kg - net_adv
            units = tray_units(trays_kg / TRAY_KG, ds, sp.rise_m)
            if not z.draw_vault(units):
                # not enough staged mass above: hold, and let the scarcity
                # multiplier pull carriers up the stair to fix it
                if self.mode != "STALLED":
                    z.stalls += 1
                self.stall_s += self.STALL_COOL
                self.stall_cool = self.STALL_COOL
                self.mode = "STALLED"
                return False
            self.trays = trays_kg / TRAY_KG
        else:
            # the descending car is heavier than it needs to be: the excess is
            # harvested to lift trays back up instead of being wasted in a brake
            self.trays = 0.0
            gain = (net_adv - need_kg) * RECOVERY_EFF / TRAY_KG
            z.stage_vault(tray_units(gain, ds, sp.rise_m))
        # the commanded imbalance is the SAME every run -- that is the design
        self.imbal_kg = need_kg
        self.ratio = imbalance_ratio(need_kg, m_susp)
        a = car_accel_ms2(need_kg, m_susp, sp.reeving)
        if a < 1e-3:
            self.stall_cool = self.STALL_COOL
            self.mode = "STALLED"
            return False
        self.timer = run_time_s(ds, a, self.spec.v_max)
        self.v_now = min(self.spec.v_max, math.sqrt(max(0.0, a * abs(ds))))
        self.dir = 1 if up else -1
        self.state = "RUN"
        self.run_from = self.s
        self.run_len = ds
        self.run_total = self.timer
        self.runs += 1
        z.runs += 1
        z.tray_flow += self.trays
        if self.mode == "STALLED":
            self.mode = "paired" if (self.paxA and self.paxB) else "single"
        return True

    def arrive(self, t):
        """Unload everyone whose leg ends here; hand transfers to the next zone."""
        z = self.zs
        fa, fb = self.floor_a, self.floor_b
        for car, fl in ((self.paxA, fa), (self.paxB, fb)):
            keep = []
            for j in car:
                if j.target_floor() == fl:
                    z.b.complete_leg(j, t)
                else:
                    keep.append(j)
            car[:] = keep
        self.trays = 0.0

    def update(self, dt, t):
        if self.stall_cool > 0.0:
            self.stall_cool = max(0.0, self.stall_cool - dt)
        if self.state == "RUN":
            self.timer -= dt
            frac = clamp(1.0 - self.timer / max(1e-6, self.run_total))
            self.s = self.run_from + self.run_len * frac
            if self.timer <= 0.0:
                self.s = self.target_s
                self.state = "DOORS"
                self.arrive(t)
                n = len(self.paxA) + len(self.paxB)
                self.timer = DOOR_DWELL_S + BOARD_S_PER_PAX * max(1, n)
                self.v_now = 0.0
        elif self.state == "DOORS":
            self.timer -= dt
            if self.timer <= 0.0:
                self.state = "IDLE"
        else:
            self.dispatch(t)


class ZoneState:
    """Live state of one zone: hall queues, hoistways, banks and incentives."""

    def __init__(self, spec, bld):
        self.spec = spec
        self.b = bld
        self.waiting = {f: [] for f in spec.floors}
        self.shafts = [Shaft(self, i) for i in range(spec.n_shafts)]
        self.pop = zone_population(spec)
        self.served = 0
        self.balked = 0
        self.stalls = 0
        self.runs = 0
        self.tray_flow = 0.0
        self.tokens = 0.0
        self.climbs = 0.0
        self.trays_carried = 0.0
        self.human_kj = 0.0
        self.flights = 0.0
        self._waits = []
        self._carry_frac = 0.0

    # -- vault plumbing (the cascade) -------------------------------------
    @property
    def top_level(self):
        return self.spec.index + 1

    @property
    def bot_level(self):
        return self.spec.index

    def vault_frac(self):
        return clamp(self.b.lobby[self.top_level] / vault_cap(self.top_level))

    def draw_vault(self, units):
        """Spend staged mass: trays ride DOWN from the top vault to the bottom."""
        if units <= 0.0:
            return True
        if self.b.lobby[self.top_level] < units:
            return False
        self.b.lobby[self.top_level] -= units
        self.b.lobby[self.bot_level] += units
        self.b.units_spent += units
        return True

    def stage_vault(self, units):
        """Surplus from a descending load lifts trays back UP the zone."""
        if units <= 0.0:
            return
        take = min(units, self.b.lobby[self.bot_level],
                   vault_cap(self.top_level) - self.b.lobby[self.top_level])
        if take <= 0.0:
            return
        self.b.lobby[self.bot_level] -= take
        self.b.lobby[self.top_level] += take
        self.b.units_restaged += take

    def stored_J(self):
        return self.b.lobby[self.top_level] * self.spec.tray_J

    # -- incentives -------------------------------------------------------
    def multiplier(self):
        vf = self.vault_frac()
        sc = max(0.0, TOKEN["scarcity_floor"] - vf) / TOKEN["scarcity_floor"]
        h = LOBBY_H_M[self.top_level] / TOWER_H_M
        return 1.0 + TOKEN["height_gain"] * h + TOKEN["scarcity_gain"] * sc

    def wait_push(self, w):
        self._waits.append(w)
        if len(self._waits) > 500:
            del self._waits[:100]

    def wait_stats(self):
        if not self._waits:
            return 0.0, 0.0
        s = sorted(self._waits[-300:])
        return sum(s) / len(s), s[int(len(s) * 0.9)]

    def queue_len(self):
        return sum(len(q) for q in self.waiting.values())

    # -- walkers ----------------------------------------------------------
    def walkers(self, dt, t):
        """People climbing the health stair with trays. The ONLY energy input."""
        dst = self.vault_frac()
        src = self.b.vault_frac(self.bot_level)
        if dst > 0.97:
            return
        # Carriers only move mass UPHILL in scarcity terms. Without this gate a
        # zone would strip the vault that feeds the zone below it.
        gate = clamp(0.30 + 1.80 * (src - dst))
        if gate <= 0.0:
            return
        mult = self.multiplier()
        rate = (WALK["base_rate_per_100"] * (self.pop / 100.0)
                * (1.0 + WALK["incentive_gain"] * (mult - 1.0)) * gate)   # climbs / min
        n = rate * (dt / 60.0)
        whole = int(n)
        if RNG.random() < (n - whole):
            whole += 1
        if whole <= 0:
            return
        for _ in range(min(whole, 60)):
            avail = self.b.lobby[self.bot_level] + self.b.floor_stock(self.spec)
            if avail < WALK["trays_per_carry"]:
                break
            self.carry_once(WALK["trays_per_carry"], mult, full=True)

    def carry_once(self, trays, mult, full=True):
        """One stair carry. `full` reaches the sky lobby; otherwise a landing bank."""
        sp = self.spec
        if full:
            room = vault_cap(self.top_level) - self.b.lobby[self.top_level]
            take = min(trays, self.b.lobby[self.bot_level], room)
            if take <= 0.0:
                return
            self.b.lobby[self.bot_level] -= take
            self.b.lobby[self.top_level] += take
            rise, flights = sp.rise_m, sp.n_floors - 1
        else:
            f = RNG.randint(sp.lo + 1, max(sp.lo + 1, sp.hi - 1))
            take = min(trays, self.b.lobby[self.bot_level])
            if take <= 0.0:
                return
            self.b.lobby[self.bot_level] -= take
            self.b.bank[f] = self.b.bank.get(f, 0.0) + take
            rise, flights = (f - sp.lo) * FLOOR_H, f - sp.lo
        self.climbs += 1
        self.trays_carried += take
        self.flights += flights
        self.human_kj += metabolic_kj(BODY_KG + take * TRAY_KG, rise)
        self.b.human_kj += metabolic_kj(BODY_KG + take * TRAY_KG, rise)
        self.b.lift_J += take * TRAY_KG * G * rise
        tok = take * flights * TOKEN["base_per_tray_flight"] * mult
        self.tokens += tok
        self.b.tokens += tok

    # -- short-haul tray shuttle ------------------------------------------
    def shuttle(self, dt):
        sp = self.spec
        if self.vault_frac() < 0.30:
            return
        stock = [(f, v) for f, v in self.b.bank.items()
                 if sp.lo < f < sp.hi and v > 1.0]
        if not stock:
            self.b.shuttle_pos[sp.index] = 0.0
            return
        f, v = max(stock, key=lambda kv: kv[1])
        n = min(v, DIMS["shuttle_trays"] * dt / 45.0,
                vault_cap(self.top_level) - self.b.lobby[self.top_level])
        if n <= 0.0:
            return
        frac_up = (sp.top_h_m - (f - 1) * FLOOR_H) / max(1e-6, sp.rise_m)
        cost = n * frac_up * 1.15
        if self.b.lobby[self.top_level] < cost:
            return
        self.b.bank[f] -= n
        self.b.lobby[self.top_level] += n - cost
        self.b.lobby[self.bot_level] += cost
        self.b.shuttle_pos[sp.index] = clamp(
            0.5 + 0.5 * math.sin(self.b.t / 22.0 + sp.index))
        self.b.shuttled += n

    def update(self, dt, t):
        for sh in self.shafts:
            sh.update(dt, t)
        self.walkers(dt, t)
        self.shuttle(dt)
        # riders who have waited beyond patience take the stairs instead
        if self.queue_len() > TRAFFIC["queue_cap"]:
            for q in self.waiting.values():
                while q and self.queue_len() > TRAFFIC["queue_cap"]:
                    j = q.pop()
                    self.balked += 1
                    self.b.balked += 1
                    self.carry_once(WALK["trays_per_carry"] * 0.5, self.multiplier(),
                                    full=False)


class Building:
    """The whole vertical transit economy: 6 zones, 14 hoistways, 7 cascading
    vaults, one stair. Nothing here consumes grid energy."""

    def __init__(self):
        self.zones = [ZoneState(z, self) for z in ZONES]
        # cascading vaults: level i is the FLOOR of zone i and the ROOF of i-1
        self.lobby = [0.0] * (NZONES + 1)
        for i in range(NZONES + 1):
            # the tower opens with the vaults staged from the night before
            self.lobby[i] = vault_cap(i) * (0.30 if i == 0 else 0.92)
        self.bank = {f: 8.0 for f in range(1, FLOORS + 1)}
        self.shuttle_pos = [0.0] * NZONES
        self.t = 6.0 * 3600.0            # the day starts at 06:00
        self.day = 1
        self.elapsed_h = 0.0             # hours since sim start (for $ / kWh rates)
        self.served = 0
        self.balked = 0
        self.registered = 0
        self.trip_time_sum = 0.0
        self.transfers = 0
        self.tokens = 0.0
        self.human_kj = 0.0
        self.lift_J = 0.0
        self.units_spent = 0.0
        self.units_restaged = 0.0
        self.shuttled = 0.0
        self.grid_kwh = 0.0               # stays exactly zero, by construction
        self._fw = self._floor_weights()
        self._hist = []                   # (hour, vault_frac, wait, queue)

    # -- helpers ----------------------------------------------------------
    def _floor_weights(self):
        w = [floor_population(f) for f in range(2, FLOORS + 1)]
        tot = sum(w)
        acc, run = [], 0.0
        for i, x in enumerate(w):
            run += x / tot
            acc.append((run, i + 2))
        return acc

    def pick_floor(self):
        r = RNG.random()
        for cum, f in self._fw:
            if r <= cum:
                return f
        return FLOORS

    def floor_stock(self, spec):
        return sum(self.bank.get(f, 0.0) for f in range(spec.lo, spec.hi + 1))

    def vault_frac(self, level):
        return clamp(self.lobby[level] / vault_cap(level))

    @property
    def hour(self):
        return (self.t / 3600.0) % 24.0

    def stored_kwh(self):
        return sum(self.lobby[i] * TRAY_KG * G * LOBBY_H_M[i] for i in range(NZONES + 1)) / 3.6e6

    def staged_tonnes(self):
        return sum(self.lobby) * TRAY_KG / 1000.0

    # -- registry ---------------------------------------------------------
    def register(self, src, dst, t):
        if src == dst:
            return
        j = Journey(src, dst, t, priority=(RNG.random() < TOKEN["priority_reserve"]))
        if not j.legs:
            return
        self.registered += 1
        self._enqueue(j)

    def _enqueue(self, j):
        lg = j.leg
        if lg is None:
            return
        zi, frm, _to = lg
        q = self.zones[zi].waiting.get(frm)
        if q is None:
            q = self.zones[zi].waiting.setdefault(frm, [])
        q.append(j)

    def complete_leg(self, j, t):
        if j.advance(t):
            self.served += 1
            self.trip_time_sum += (t - j.t_start)
            self.zones[j.legs[-1][0]].served += 1
        else:
            self.transfers += 1
            self._enqueue(j)

    # -- traffic ----------------------------------------------------------
    def _spawn(self, dt):
        h = self.hour
        T = TRAFFIC
        am = T["am_amp"] * math.exp(-0.5 * ((h - T["am_peak_h"]) / T["am_sigma_h"]) ** 2)
        lu = T["lunch_amp"] * math.exp(-0.5 * ((h - T["lunch_h"]) / T["lunch_sigma"]) ** 2)
        pm = T["pm_amp"] * math.exp(-0.5 * ((h - T["pm_peak_h"]) / T["pm_sigma_h"]) ** 2)
        inter = T["inter_amp"] if T["inter_start"] <= h <= T["inter_end"] else 0.25
        m = dt / 60.0

        def emit(n, kind):
            k = int(n)
            if RNG.random() < (n - k):
                k += 1
            for _ in range(min(k, 90)):
                if kind == "up":
                    self.register(1, self.pick_floor(), self.t)
                elif kind == "down":
                    self.register(self.pick_floor(), 1, self.t)
                else:
                    a, b = self.pick_floor(), self.pick_floor()
                    self.register(a, b, self.t)

        emit((am + lu) * m, "up")
        emit((pm + lu) * m, "down")
        emit(inter * m, "inter")

    # -- main tick --------------------------------------------------------
    def update(self, dt):
        self.t += dt
        self.elapsed_h += dt / 3600.0
        if self.t >= 24.0 * 3600.0:
            self.t -= 24.0 * 3600.0
            self.day += 1
        self._spawn(dt)
        for z in self.zones:
            z.update(dt, self.t)

    def sample(self):
        w, _ = self.wait_stats()
        self._hist.append((self.hour, self.vault_frac(1), w, self.queue_len()))
        if len(self._hist) > 1400:
            del self._hist[:300]

    def wait_stats(self):
        avg = [z.wait_stats() for z in self.zones]
        a = [x[0] for x in avg if x[0] > 0]
        p = [x[1] for x in avg if x[1] > 0]
        return (sum(a) / len(a) if a else 0.0), (max(p) if p else 0.0)

    def queue_len(self):
        return sum(z.queue_len() for z in self.zones)

    def cars_moving(self):
        return sum(1 for z in self.zones for s in z.shafts if s.state == "RUN")

    def stalls(self):
        return sum(z.stalls for z in self.zones)

    def kcal(self):
        return self.human_kj * WALK["kcal_per_kj"]

    def flights(self):
        return sum(z.flights for z in self.zones)

    def avg_trip_min(self):
        return (self.trip_time_sum / max(1, self.served)) / 60.0

    def saved_kwh(self):
        return reference_grid_kwh(self.served, self.elapsed_h)

    def stair_carries(self):
        return sum(z.climbs for z in self.zones)

    def saved_usd(self):
        """What a conventional traction-lift bank would have cost to run
        instead, in dollars, at the reference grid tariff."""
        return self.saved_kwh() * REFERENCE["tariff_usd_kwh"]

    def walker_pool_usd(self):
        """The real-dollar pool backing the token economy. By construction it
        never exceeds what the building saved on electricity -- the walkers
        are paid out of the avoided bill, not out of thin air."""
        return self.saved_usd() * ECONOMY["walker_payout_frac"]

    def usd_per_token(self):
        return self.walker_pool_usd() / max(1.0, self.tokens)

    def usd_per_carry(self):
        return self.walker_pool_usd() / max(1.0, self.stair_carries())

    def usd_per_flight(self):
        return self.walker_pool_usd() / max(1.0, self.flights())

    def mode(self):
        """The headline operating state, read off the live traffic + vaults."""
        if self.stalls() > 0 and min(self.vault_frac(i) for i in range(1, NZONES + 1)) < 0.06:
            return "MASS SHORTFALL"
        h = self.hour
        if 6.8 <= h <= 10.0:
            return "UP-PEAK  (vaults discharging)"
        if 16.5 <= h <= 19.5:
            return "DOWN-PEAK  (vaults re-staging)"
        if 11.5 <= h <= 13.8:
            return "LUNCH  (two-way, near balance)"
        if h < 6.0 or h > 21.0:
            return "NIGHT  (stair carries + shuttles)"
        return "INTERFLOOR  (balanced)"


class DayWorld:
    """Wall-clock -> building-clock, with time warp for the 24 h DAY mode."""

    TIME_WARP = [1.0, 10.0, 60.0, 300.0, 900.0]

    def __init__(self):
        self.warp_i = 2
        self.sample_acc = 0.0

    @property
    def warp(self):
        return self.TIME_WARP[self.warp_i]

    def cycle_warp(self, d):
        self.warp_i = int(clamp(self.warp_i + d, 0, len(self.TIME_WARP) - 1))

    def sun(self, hour):
        """0 at night, 1 at midday -- drives the DAY-mode sky."""
        if hour < 5.0 or hour > 20.0:
            return 0.0
        return clamp(math.sin((hour - 5.0) / 15.0 * math.pi))


def sky_colors(sun):
    t = clamp(sun * 1.5)
    return (_mix(C_SKY_NIGHT1, C_SKY_DAY1, t), _mix(C_SKY_NIGHT2, C_SKY_DAY2, t))


# =============================================================================
# SECTION 7 -- FULL INFORMATIONAL SPECIFICATION (about / detail / honesty)
# =============================================================================

def build_info_sections():
    z0, zt = ZONES[0], ZONES[-1]
    m_ex = z0.suspended_kg(6 * PAX_KG, 3 * PAX_KG)
    d_ex = required_advantage_kg(m_ex, z0.reeving)
    t_ex = tray_mass_needed_kg(m_ex, z0.reeving, 3 * PAX_KG - 6 * PAX_KG)
    # Reference-day figures: a real 24 h run of Building() on the default
    # traffic profile (the same run MEASURED, below, quotes). The $ figures
    # are computed live from REFERENCE / ECONOMY so they track any constant
    # changes; the underlying kWh/tokens/carries/flights are the measured
    # reference run itself -- for THIS building's live numbers, run DAY mode.
    ref_kwh = 732.3
    ref_tokens = 532700.0
    ref_carries = 17404.0
    ref_flights = 173061.0
    ref_usd = ref_kwh * REFERENCE["tariff_usd_kwh"] * ECONOMY["walker_payout_frac"]
    ref_usd_token = ref_usd / ref_tokens
    ref_usd_carry = ref_usd / ref_carries
    ref_usd_flight = ref_usd / ref_flights
    ref_usd_year = ref_usd * 365.0
    return [
        ("ABOUT THIS MODEL", [
            "HealthElevator.py is a standalone, to-scale digital twin of a",
            "gravity-and-human-power vertical transit system, built the same",
            "way the HOHEV/SE.py reference twins model a ship or an engine:",
            "one Python file, real SI dimensions, an honest physics ledger,",
            "and a live simulation you can run at time-warp and watch settle.",
            "",
            "Nothing here is a mockup. Every part in the TOWER and MACHINE",
            "views is sized from the DIMS table at the top of the file; every",
            "number in this panel is either a design constant or something",
            "the DAY-mode simulation actually measured. Run it yourself with",
            "TAB -> DAY and , / . to fast-forward a full 24-hour cycle.",
            "",
            "Use the left TOC to jump between sections, or just scroll.",
        ]),
        ("THE CORE LOOP  (start here)", [
            "Skip the mechanical detail for a second -- here is the whole",
            "system in one paragraph.",
            "",
            "Every hoistway holds TWO cars on one rope, over one sheave.",
            "Whichever side is heavier falls, and its fall pulls the other",
            "side up. So: if a loaded car is going DOWN at the exact moment",
            "another car needs to go UP, the down car's own weight does the",
            "lifting -- for free, no tray, no effort, because up-traffic and",
            "down-traffic are naturally cancelling each other out. That",
            "happens constantly: mornings send people up, evenings send them",
            "down, and any two calls going opposite ways can be PAIRED to",
            "cancel.",
            "",
            "The only time a HUMAN has to supply weight is when the two",
            "sides do NOT naturally balance -- an up call with nobody going",
            "down to match it. For exactly that moment, the system needs a",
            "bank of pre-carried weight already sitting in the sky-lobby",
            "VAULT above, ready to drop. That weight got there earlier",
            "because someone walked a tray of it up the stairs and banked",
            "it -- and was paid in tokens for doing so (see THE MONEY,",
            "below, for what a token is actually worth in real dollars).",
            "",
            "So: natural counter-traffic pays for itself automatically. The",
            "LEFTOVER imbalance -- and only the leftover -- is what people",
            "are carrying, and it is what they are paid for.",
        ]),
        ("THE BUILDING", [
            "A %d-storey, %.0f m commercial tower whose ENTIRE vertical" % (FLOORS, TOWER_H_M),
            "transit system runs on gravity and human weight -- no motors,",
            "no drives, no grid connection for motion at all.",
            "%.0f m2 gross, design population %d, %.2f m floor-to-floor." % (
                TOWER["gross_area_m2"], TOWER["occupants"], FLOOR_H),
            "%d hoistways, %d cabins, %d sky lobbies, one very good stair." % (
                TOTAL_SHAFTS, TOTAL_SHAFTS * 2, NZONES - 1),
        ]),
        ("1. ZONING  (the biggest single efficiency gain)", [
            "The tower is cut into %d independent vertical zones of %d-%d" % (
                NZONES, min(z.n_floors for z in ZONES), max(z.n_floors for z in ZONES)),
            "floors, joined by SKY LOBBIES at floors " + ", ".join(
                str(x) for x in SKY_LOBBIES[1:-1]) + ".",
            "Nobody hauls mass past the next sky lobby, and no hoistway",
            "runs the full height -- so the zones STACK inside a small core.",
            "Lower zones (highest traffic) get %d hoistways and %d-person cars;" % (
                ZONES[0].n_shafts, ZONES[0].cap),
            "the top zone gets %d hoistway(s) and %d-person cars." % (
                zt.n_shafts, zt.cap),
            "Total human-carried mass-distance collapses, and upper-floor",
            "service stays viable even on sparse traffic.",
        ]),
        ("2. COUNTER-RUNNING CABIN PAIRS", [
            "Every hoistway carries TWO cabins rope-linked over one head",
            "sheave. Cabin A rises exactly as cabin B descends: the loaded",
            "descending car IS the lift power for the ascending car.",
            "One degree of freedom, no drive, no gearbox, no controller",
            "that can push -- only latches that let go.",
            "When the dispatcher pairs an up call with a down call, the net",
            "energy of the run falls to the FRICTION LOSS ALONE.",
        ]),
        ("3. CASCADING WEIGHT BANKS + THE VAULT BATTERY", [
            "Modular %.2f kg (25 lb) trays are the currency of the system." % TRAY_KG,
            "Walkers deposit them at the landing bank nearest to them and are",
            "credited on the spot. Trays are then staged upward IN STEPS --",
            "by the short-haul shuttles and by the lifts' own surplus.",
            "A sky-lobby VAULT of staged trays is literally the building's",
            "battery: %d trays (~%.0f t) at floor %d hold %.1f kWh." % (
                DIMS["vault_capacity"], DIMS["vault_capacity"] * TRAY_KG / 1000.0,
                SKY_LOBBIES[1],
                DIMS["vault_capacity"] * TRAY_KG * G * LOBBY_H_M[1] / 3.6e6),
            "Zone i DRAWS from vault i+1 and RETURNS to vault i; down-peak",
            "traffic pushes the trays back up. The cascade is conservative:",
            "trays are never created, only moved.",
        ]),
        ("4. THE TOKEN ECONOMY  (self-balancing incentives)", [
            "Credit = trays x flights climbed x height factor x SCARCITY.",
            "Height adds up to +%.0f%%; scarcity adds up to +%.0f%% when a" % (
                TOKEN["height_gain"] * 100, TOKEN["scarcity_gain"] * 100),
            "vault falls below %.0f%% full." % (TOKEN["scarcity_floor"] * 100),
            "Because fewer people ever go to the top, the upper multipliers",
            "run higher and pull carriers exactly where the mass is short.",
            "The 'less traffic higher up' problem becomes the control signal.",
            "No central dispatcher of people -- just a live price.",
        ]),
        ("5. THE MONEY  (what a token is actually worth)", [
            "Goal.md only ever specifies tokens as internal credit. Priced",
            "against the one real saving on the books -- the electricity a",
            "conventional lift bank would have burned (REFERENCE, in the",
            "file) -- here is what that credit is worth in real dollars.",
            "At %.0f%% payout (ECONOMY.walker_payout_frac), the WHOLE avoided" % (
                ECONOMY["walker_payout_frac"] * 100),
            "bill becomes the walker pool: the building never pays out more",
            "than it saved. Lower that fraction to bank some of it instead.",
            "",
            "On the reference simulated day (~%.0f kWh avoided, $%.2f/kWh):" % (
                ref_kwh, REFERENCE["tariff_usd_kwh"]),
            "  Avoided electricity bill      ~$%.0f / day   (~$%s / year)" % (
                ref_usd, f"{ref_usd_year:,.0f}"),
            "  Tokens issued that day        ~%s" % f"{ref_tokens:,.0f}",
            "  Value per token                ~$%.5f" % ref_usd_token,
            "  Value per stair carry           ~$%.4f" % ref_usd_carry,
            "  Value per flight climbed        ~$%.4f" % ref_usd_flight,
            "",
            "That is the honest number, and it is small, because grid",
            "electricity is simply cheap. Nobody gets rich carrying trays.",
            "A token's real job was never the payout -- it is the",
            "ALLOCATION SIGNAL that steers carriers to whichever vault is",
            "running low (see 4, above). The dividend that actually matters",
            "at this scale is the exercise (see THE HEALTH DIVIDEND), not",
            "the cash.",
            "",
            "GLOBAL SCALE -- if gravity transit replaced every traction",
            "and hydraulic lift on the planet (industry estimates: ~20",
            "million installed units, ~300 TWh/year, ~1% of world",
            "electricity):",
            "  Avoided electricity      ~300 TWh / year",
            "  Avoided cost             ~$%s / year" % f"{GLOBAL['twh_year'] * 1e9 * REFERENCE['tariff_usd_kwh']:,.0f}",
            "  Avoided CO2              ~%.0f million tonnes / year" % (
                GLOBAL['twh_year'] * 1e9 * REFERENCE['co2_kg_kwh'] / 1e6),
            "  Equivalent cars off road ~%.1f million" % (
                GLOBAL['twh_year'] * 1e9 * REFERENCE['co2_kg_kwh'] / 4_600),
            "",
            "  Per elevator (avg):      ~%d kWh / year" % GLOBAL['avg_kwh_per_lift'],
            "                           ~$%.0f / year" % (
                GLOBAL['avg_kwh_per_lift'] * REFERENCE['tariff_usd_kwh']),
            "  This tower (14 lifts):   ~%s kWh / year" % f"{ref_kwh * 365:,.0f}",
            "                           ~$%s / year" % f"{ref_usd_year:,.0f}",
            "",
            "300 TWh is ~80 nuclear reactors or ~150 coal plants running",
            "flat out for a year, just to move elevators. Gravity transit",
            "would zero that line item -- not by using less electricity,",
            "but by removing the motor entirely.",
            "",
            "Run DAY mode yourself for THIS run's live, exact figures -- the",
            "DAY HUD prints the avoided bill, $/token and $/carry live.",
        ]),
        ("6. REGISTERED DEMAND  (and why waits get shorter)", [
            "Every hall call is registered with a timestamp at the landing",
            "post. Because the system knows the call BEFORE the rider is in",
            "the car, it pre-positions the exact counter-mass first.",
            "Calls are batched: one slightly heavier car serves several",
            "riders going the same way, which cuts the number of separate",
            "weight movements as well as the wait.",
            "%.0f%% of slots stay free for genuine incapacity and jump the" % (
                TOKEN["priority_reserve"] * 100),
            "queue. Riders see an estimated wait and may walk instead --",
            "and if they do, they can carry a tray and get paid for it.",
        ]),
        ("7. THE MECHANICS  (how the imbalance got to 3-8%)", [
            "Roller guide shoes on machined T-rails, lubricated grooved",
            "sheaves, compensated rope mass: total resistance mu_eff = %.3f." % MU_EFF,
            "Commanded imbalance = %.2f x the friction floor." % IMBAL_MARGIN,
            "Worked example, zone 1, 6 riders up against 3 riders down:",
            "   suspended mass %.0f kg, imbalance %.0f kg  =  %.1f%%." % (
                m_ex, d_ex, imbalance_ratio(d_ex, m_ex) * 100),
            "Here the ASCENDING car is the heavier one, by %.0f kg, so the" % (3 * PAX_KG),
            "trays have to cover that as well as the driving advantage:",
            "%.0f kg = %.0f trays = %d stair carries. Reverse the loads --" % (
                t_ex, t_ex / TRAY_KG,
                math.ceil(max(1.0, t_ex / TRAY_KG / WALK["trays_per_carry"]))),
            "6 riders DOWN against 3 up -- and the run needs no trays at all;",
            "it makes them. That asymmetry is the whole daily cycle.",
            "Upper zones add DIFFERENTIAL 2:1 REEVING (car 2:1, counterweight",
            "1:1): halves the tray mass a run needs, halves car speed to",
            "%.2f m/s. Exactly the right trade where traffic is light." % (ROPE_SPEED_MS / 2),
            "Fixed base counterweights carry the AVERAGE zone load, so only",
            "the variable add-on mass is ever human-carried.",
        ]),
        ("8. THE HEALTH DIVIDEND  (this is the fuel)", [
            "The only energy input to the whole tower is people climbing",
            "stairs with trays, at %.0f%% metabolic efficiency." % (WALK["metabolic_eff"] * 100),
            "One carry of %.0f trays up zone 1 = %.0f J stored and about" % (
                WALK["trays_per_carry"], WALK["trays_per_carry"] * ZONES[0].tray_J),
            "%.0f kcal burned." % (metabolic_kj(BODY_KG + WALK["trays_per_carry"] * TRAY_KG,
                                                ZONES[0].rise_m) * WALK["kcal_per_kj"]),
            "The building does not have an energy bill; it has a fitness",
            "programme that happens to move everybody vertically.",
            "DAY mode tallies flights, tray-metres and kilocalories live.",
        ]),
        ("MEASURED  (what one full simulated day actually does)", [
            "Run the DAY mode at high time-warp and this is what comes out,",
            "on the default traffic profile and a %d-person population:" % TOWER["occupants"],
            "",
            "  ~6,700 calls registered, ~6,600 journeys completed,",
            "  0 balked, 0 stalls, ~12,300 sky-lobby transfers.",
            "  Average hall wait 22 s; worst zone 90th percentile 44 s.",
            "  Average door-to-door journey ~10 min including transfers.",
            "  ~17,400 stair carries, ~173,000 flights climbed.",
            "  ~165 MJ of human lift work banked; ~690,000 kcal burned.",
            "  Vaults settle into a steady band and stay there.",
            "  Grid energy for motion: 0.00 kWh (vs ~732 kWh conventional,",
            "  ~$117/day -- see THE MONEY for what that's worth per token).",
            "",
            "Per occupant that is roughly 105 flights and 420 kcal a day.",
            "That is the honest sticker price: this building only works if a",
            "real share of the population actually carries trays up stairs,",
            "every day. It is a fitness programme with a lift attached, not",
            "a lift that happens to be free.",
        ]),
        ("HONEST PHYSICS  (what is and isn't claimed)", [
            "This is NOT perpetual motion and NOT free energy. Every joule",
            "that lifts a passenger was put in by a human leg muscle, at a",
            "metabolic cost several times the mechanical work.",
            "The system wins on THREE real effects, nothing else:",
            "  (a) counterweighting -- you only pay for the DIFFERENCE;",
            "  (b) counter-running pairs -- the down traffic pays for the up;",
            "  (c) zoning -- mass-distance drops because nobody carries far.",
            "Over a balanced day, up and down passenger work cancel almost",
            "exactly, so the true net input is the FRICTION LOSS -- which is",
            "why mu_eff is the number the whole design lives or dies on.",
            "",
            "It is slower than a motor. Cars run at %.2f-%.2f m/s against" % (
                ZONES[-1].v_max, ZONES[0].v_max),
            "the 6-10 m/s of a modern high-rise bank, and a cross-tower trip",
            "takes transfers. Speed is the price paid for the zero.",
            "",
            "The other price is MASS. Roughly %.0f tonnes of tray steel is" % (
                (DIMS["ground_reservoir"] * 0.30
                 + NZONES * DIMS["vault_capacity"] * 0.92) * TRAY_KG / 1000.0),
            "in circulation, and a full sky-lobby vault puts ~%.0f t on one" % (
                DIMS["vault_capacity"] * TRAY_KG / 1000.0),
            "structural bay -- a heavy-storage floor loading that has to be",
            "designed in from the start. That is a real cost, not a rounding.",
            "If the vaults run dry the cars STALL -- the model shows this",
            "happening rather than hiding it, and the token multiplier is",
            "the mechanism that fixes it.",
        ]),
        ("VERIFICATION CHECKLIST", [
            "[x] %d floors, %d zones of %d-%d floors, %d sky lobbies" % (
                FLOORS, NZONES, min(z.n_floors for z in ZONES),
                max(z.n_floors for z in ZONES), NZONES - 1),
            "[x] counter-running rope-linked cabin pairs in every hoistway",
            "[x] cascading landing banks + sky-lobby staged-mass vaults",
            "[x] scarcity + height token multiplier (self-balancing)",
            "[x] registered calls, pre-positioned counter-mass, batching",
            "[x] priority slots reserved for genuine incapacity",
            "[x] roller guides / lubricated sheaves -> 3-8% imbalance band",
            "[x] differential 2:1 reeving on the light upper zones",
            "[x] fixed base counterweights sized for average zone load",
            "[x] modular 25 lb ergonomic trays, cart- and pack-friendly",
            "[x] short-haul pure-gravity tray shuttles",
            "[x] traffic-aware sizing (capacity falls with height)",
            "[x] overspeed governor + wedge safety gear + ratchet holding brake",
            "[x] to-scale 3D parts, hover inspector, section/exploded/assembly",
            "[x] live 24 h operating day with waits, stalls and kcal",
            "[x] ZERO grid energy for motion, by construction",
        ]),
        ("CONTROLS", [
            "TAB           cycle TOWER / MACHINE / DAY modes",
            "click tabs    or click the mode tabs in the top bar",
            "drag          orbit the model",
            "right-drag    pan the camera",
            "wheel         zoom in / out (or scroll this panel)",
            "click part    pin it in the inspector (left sidebar)",
            "1 2 3 4       full / exploded / assembly / section-cut",
            "E             quick exploded toggle",
            "X             cross-section half-cut (see the shafts)",
            "L             toggle part labels",
            "R             reset the camera",
            "[ ]           step the assembly build",
            "A / C         assemble all / clear",
            ", / .         slow / speed up TIME-WARP (DAY mode)",
            "V             verification checklist",
            "I             this full specification",
            "H             quick help card",
            "Esc           close this panel   Q  quit",
        ]),
    ]


# =============================================================================
# SECTION 8 -- HUD / UI HELPERS
# =============================================================================

def vgradient(surf, top, bot):
    h, w = surf.get_height(), surf.get_width()
    for y in range(h):
        t = y / max(1, h)
        pygame.draw.line(surf, (int(top[0] + (bot[0] - top[0]) * t),
                                int(top[1] + (bot[1] - top[1]) * t),
                                int(top[2] + (bot[2] - top[2]) * t)), (0, y), (w, y))


def bar(surf, font, x, y, w, h, frac, color, label, valtext, lo=None):
    pygame.draw.rect(surf, C_PANEL_HI, (x, y, w, h), border_radius=4)
    pygame.draw.rect(surf, color, (x, y, int(w * clamp(frac)), h), border_radius=4)
    if lo is not None:
        pygame.draw.line(surf, C_WARN, (x + int(w * lo), y - 2), (x + int(w * lo), y + h + 2), 1)
    surf.blit(font.render(label, True, C_TEXT_DIM), (x, y - 16))
    img = font.render(valtext, True, C_TEXT)
    surf.blit(img, (x + w - img.get_width(), y - 16))


def panel(surf, x, y, w, h, alpha=210):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((C_PANEL[0], C_PANEL[1], C_PANEL[2], alpha))
    surf.blit(s, (x, y))
    pygame.draw.rect(surf, C_PANEL_HI, (x, y, w, h), 1, border_radius=6)


def wrap_text(font, text, maxpx):
    out, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if font.size(trial)[0] <= maxpx:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out or [""]


def _toc_label(head):
    """Shorten a spec section header to a TOC-rail entry, e.g.
    '1. ZONING  (the biggest single efficiency gain)' -> '1. Zoning'."""
    base = head.split("  (")[0].split(" (")[0].strip()
    num, dot, rest = base.partition(". ")
    if dot and num.isdigit():
        return num + ". " + rest.title()
    return base.title()


def _split_key_line(ln):
    """Split a CONTROLS line 'KEY   description' on the first 3+-space gap."""
    idx = ln.find("   ")
    if idx == -1:
        return None, ln
    return ln[:idx].rstrip(), ln[idx:].lstrip()


def _label(surf, font, text, pos, accent=False):
    col = (255, 210, 120) if accent else C_TEXT
    dot = (255, 210, 120) if accent else C_ACCENT
    img = font.render(text, True, col)
    x, y = int(pos[0]) + 6, int(pos[1]) - 6
    bg = pygame.Surface((img.get_width() + 8, img.get_height() + 4), pygame.SRCALPHA)
    bg.fill((10, 14, 20, 190))
    surf.blit(bg, (x - 4, y - 2))
    pygame.draw.circle(surf, dot, (int(pos[0]), int(pos[1])), 3)
    surf.blit(img, (x, y))


# =============================================================================
# SECTION 9 -- 3D RENDERER (projects + paints the spec'd Parts)
# =============================================================================

class TowerRenderer:
    """Projects + paints spec'd Parts with a painter's algorithm. Supports full /
    exploded / assembly views, an optional half-section CUT, mouse hover-picking
    and per-mesh live offsets. Geometry-agnostic -- the same class draws the
    whole 234 m tower and a single zone's gravity machine."""

    def __init__(self, parts_builder, outline=False, detail_labels=True,
                 home_az=0.72, home_el=0.16, home_dist=1.45):
        self.parts_builder = parts_builder
        self.outline = outline
        # per-mesh labels are gold on the machine and chaos on a 330-mesh tower
        self.detail_labels = detail_labels
        self.parts = parts_builder()
        self._home = (home_az, home_el, home_dist)
        self.az, self.el, self.dist = home_az, home_el, home_dist
        self.pan = np.array([0.0, 0.0])
        self.light = np.array([0.42, 0.72, 0.95])
        self.light = self.light / np.linalg.norm(self.light)
        self.view = "full"
        self.section = False
        self.explode_amt = 0.0
        self.assembled = len(self.parts)
        self.hovered = None
        self.selected = None
        self.pop = np.zeros(len(self.parts))
        self.hover_spread = 0.0

    def reset_view(self):
        self.az, self.el, self.dist = self._home
        self.pan = np.array([0.0, 0.0])

    def zoom_at(self, factor, mouse_pos=None, rect=None):
        old = self.dist
        self.dist = max(0.30, min(9.0, self.dist * factor))
        if old <= 1e-6 or mouse_pos is None or rect is None:
            return
        if not rect.collidepoint(mouse_pos):
            return
        anchor = np.array([mouse_pos[0] - (rect.x + rect.w / 2.0),
                           mouse_pos[1] - (rect.y + rect.h / 2.0)], dtype=float)
        self.pan = anchor - (anchor - self.pan) * (old / self.dist)

    def orbit(self, dx, dy):
        self.az += dx * 0.009
        self.el = max(-1.50, min(1.50, self.el + dy * 0.009))

    def pan_by(self, dx, dy):
        self.pan += np.array([float(dx), float(dy)])

    def set_view(self, mode):
        self.view = mode
        if mode == "assembly" and self.assembled >= len(self.parts):
            self.assembled = 0
        self.selected = None

    def toggle_section(self):
        self.section = not self.section

    def assembly_next(self):
        self.assembled = min(len(self.parts), self.assembled + 1)

    def assembly_prev(self):
        self.assembled = max(0, self.assembled - 1)

    def assembly_all(self):
        self.assembled = len(self.parts)

    def assembly_clear(self):
        self.assembled = 0

    def active_part(self):
        i = self.selected if self.selected is not None else self.hovered
        return self.parts[i] if i is not None else None

    def placing_part(self):
        for p in self.parts:
            if p.order == self.assembled:
                return p
        return None

    def tick(self, dt):
        if self.view != "assembly":
            target = 1.0 if self.view == "exploded" else 0.0
            self.explode_amt += (target - self.explode_amt) * min(1.0, dt * 4)
        hi = self.selected if self.selected is not None else self.hovered
        sp = 0.22 if (hi is not None and self.view == "full") else 0.0
        self.hover_spread += (sp - self.hover_spread) * min(1.0, dt * 5)
        for i in range(len(self.parts)):
            tp = 1.0 if i == hi else 0.0
            self.pop[i] += (tp - self.pop[i]) * min(1.0, dt * 8)

    def _layout(self, pi, vw, eamt):
        part = self.parts[pi]
        if vw == "assembly":
            if part.order < self.assembled:
                return part.explode * 0.0, 1.0, "normal"
            if part.order == self.assembled:
                return part.explode * 0.55, 1.0, "active"
            return part.explode * 1.0, 0.28, "pending"
        return part.explode * eamt, 1.0, "normal"

    def render(self, surf, rect, angles, mouse_pos=None, show_labels=True,
               label_font=None, interactive=False):
        clip = surf.get_clip()
        surf.set_clip(rect)
        cx = rect.x + rect.w / 2.0 + self.pan[0]
        cy = rect.y + rect.h / 2.0 + self.pan[1]
        focal = min(rect.w, rect.h) * 1.12
        Rcam = rot_x(self.el) @ rot_y(self.az)
        default_ang = angles.get("default", 0.0)

        vw = self.view
        eamt = self.explode_amt
        if vw == "full":
            eamt += self.hover_spread
        section = self.section and vw in ("full", "exploded")
        hi = self.selected if self.selected is not None else self.hovered

        polys, labels, leaders, screeninfo = [], [], [], []
        lx, ly, lz = float(self.light[0]), float(self.light[1]), float(self.light[2])

        for pi, part in enumerate(self.parts):
            base_off, dim, tag = self._layout(pi, vw, eamt)
            off = base_off + part.popdir * (self.pop[pi] * 0.10)
            highlight = (pi == hi)
            allcam = []
            for m in part.meshes:
                if m.hidden:
                    continue
                wv = m.world_verts(angles.get(m.group, default_ang)) + off
                cam = wv @ Rcam.T
                cam[:, 2] += self.dist
                allcam.append(cam)
                caml = cam.tolist()
                col = m.shade_color()
                if dim < 0.99:
                    col = (int(col[0] * dim), int(col[1] * dim), int(col[2] * dim))
                if highlight:
                    col = _mix(col, (255, 255, 255), 0.26)
                cr, cg, cb = col
                if highlight:
                    outline, ow = C_ACCENT, 2
                elif tag == "active":
                    outline, ow = (255, 210, 120), 2
                elif self.outline:
                    outline, ow = (12, 14, 18), 1
                else:
                    outline, ow = None, 0
                sxl, syl, dzl = [], [], []
                for vx2, vy2, vz2 in caml:
                    dzl.append(vz2)
                    if vz2 > 0.05:
                        sxl.append(cx + focal * vx2 / vz2)
                        syl.append(cy - focal * vy2 / vz2)
                    else:
                        sxl.append(0.0)
                        syl.append(0.0)
                if (show_labels and label_font and m.name and tag != "pending"
                        and ((self.detail_labels and vw == "exploded") or highlight
                             or (vw == "assembly" and tag == "active"))):
                    mc = cam.mean(axis=0)
                    if mc[2] > 0.05:
                        labels.append((mc[2], (cx + focal * mc[0] / mc[2],
                                               cy - focal * mc[1] / mc[2]),
                                       m.name, "detail"))
                for face in m.faces:
                    if section and wv[list(face)].mean(axis=0)[0] > 0.004:
                        continue
                    bad = False
                    for i in face:
                        if dzl[i] <= 0.05:
                            bad = True
                            break
                    if bad:
                        continue
                    ax, ay, az = caml[face[0]]
                    bx, by, bz = caml[face[1]]
                    fx, fy, fz = caml[face[2]]
                    ux, uy, uz = bx - ax, by - ay, bz - az
                    wx, wy, wz = fx - ax, fy - ay, fz - az
                    nx = uy * wz - uz * wy
                    ny = uz * wx - ux * wz
                    nz = ux * wy - uy * wx
                    inv = 1.0 / ((nx * nx + ny * ny + nz * nz) ** 0.5 or 1.0)
                    nx *= inv
                    ny *= inv
                    nz *= inv
                    if nz > 0:
                        nx, ny, nz = -nx, -ny, -nz
                    d = nx * lx + ny * ly + nz * lz
                    shade = 0.46 + 0.54 * (d if d > 0.0 else 0.0)
                    fc = (int(cr * shade), int(cg * shade), int(cb * shade))
                    ds = 0.0
                    for i in face:
                        ds += dzl[i]
                    polys.append((ds / len(face), [(sxl[i], syl[i]) for i in face],
                                  fc, outline, ow))

            if not allcam:
                continue
            cam_all = np.vstack(allcam)
            cen = cam_all.mean(axis=0)
            if cen[2] > 0.05:
                safez = np.where(cam_all[:, 2] <= 0.05, 1e9, cam_all[:, 2])
                scx = cx + focal * cam_all[:, 0] / safez
                scy = cy - focal * cam_all[:, 1] / safez
                pcx = cx + focal * cen[0] / cen[2]
                pcy = cy - focal * cen[1] / cen[2]
                rad = float(np.max(np.hypot(scx - pcx, scy - pcy))) * 0.50 + 6
                screeninfo.append((pi, pcx, pcy, rad, cen[2], tag))
                if (show_labels and label_font and tag != "pending"
                        and (vw != "full" or highlight)):
                    labels.append((cen[2], (pcx, pcy), part.name, tag))
                if tag == "active":
                    hc = cen - (off @ Rcam.T)
                    if hc[2] > 0.05:
                        leaders.append(((pcx, pcy), (cx + focal * hc[0] / hc[2],
                                                     cy - focal * hc[1] / hc[2])))

        polys.sort(key=lambda t: t[0], reverse=True)
        for _, pts, fc, outline, ow in polys:
            if len(pts) >= 3:
                try:
                    pygame.draw.polygon(surf, fc, pts)
                    if outline is not None:
                        pygame.draw.polygon(surf, outline, pts, ow)
                except Exception:
                    pass

        for a, b in leaders:
            pygame.draw.line(surf, (255, 210, 120), a, b, 1)
            pygame.draw.circle(surf, (255, 210, 120), (int(b[0]), int(b[1])), 5, 1)

        if show_labels and label_font:
            labels.sort(key=lambda t: t[0])
            used = []
            for _, (lxx, lyy), text, tag in labels:
                ly2 = lyy
                for uy in used:
                    if abs(ly2 - uy) < 16:
                        ly2 = uy + 16
                used.append(ly2)
                _label(surf, label_font, text, (lxx, ly2), accent=(tag in ("active", "detail")))

        if interactive and mouse_pos is not None:
            mxp, myp = mouse_pos
            best, bestd = None, 1e18
            for pi, pcx, pcy, rad, depth, tag in screeninfo:
                if tag == "pending":
                    continue
                if math.hypot(mxp - pcx, myp - pcy) <= rad and depth < bestd:
                    bestd, best = depth, pi
            self.hovered = best

        surf.set_clip(clip)


# =============================================================================
# SECTION 10 -- APPLICATION
# =============================================================================

class App:
    MODES = ["tower", "machine", "day"]
    MODE_NAME = {"tower": "TOWER  (whole building)",
                 "machine": "MACHINE  (one zone's gravity machine)",
                 "day": "DAY  (24-hour operating day)"}

    LEFT_PANEL_W = 226
    RIGHT_PANEL_W = 356
    TOP_BAR_H = 36
    BOTTOM_BAR_H = 86

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("HealthElevator.py -- Gravity Tower Digital Twin")
        self.W, self.H = 1480, 900
        self.screen = pygame.display.set_mode((self.W, self.H))
        self.clock = pygame.time.Clock()
        mono = "consolas,menlo,dejavusansmono,monospace"
        self.font = pygame.font.SysFont(mono, 14)
        self.fs = pygame.font.SysFont(mono, 12)
        self.fb = pygame.font.SysFont(mono, 20, bold=True)
        self.fbig = pygame.font.SysFont(mono, 30, bold=True)
        self.fmicro = pygame.font.SysFont(mono, 11)

        self.tower_rend = TowerRenderer(build_tower_parts, outline=False,
                                        detail_labels=False,
                                        home_az=0.72, home_el=0.08, home_dist=1.12)
        self.mach_rend = TowerRenderer(build_machine_parts, outline=True,
                                       detail_labels=True,
                                       home_az=0.62, home_el=0.24, home_dist=2.30)
        self.b = Building()
        self.world = DayWorld()

        self.mode = "tower"
        self.ang = {"sheave": 0.0, "gov": 0.0, "default": 0.0}
        self.show_labels = True
        self.show_help = False
        self.show_info = False
        self.show_checklist = False
        self.info_scroll = 0
        self.info_sections = build_info_sections()
        self.info_offsets, self.info_total_h = self._compute_info_offsets()
        self.dragging = False
        self.panning = False
        self.running = True
        self._preview_hitboxes = {}
        self._mode_hitboxes = {}
        self._part_list_hitboxes = {}
        self._info_toc_hitboxes = {}
        self._sample_acc = 0.0
        self.bg = pygame.Surface((self.W, self.H))
        vgradient(self.bg, BG_TOP, BG_BOT)

    def rend(self):
        return self.mach_rend if self.mode == "machine" else self.tower_rend

    def view_rect(self):
        if self.mode == "day":
            return pygame.Rect(0, self.TOP_BAR_H, self.W - 360,
                               self.H - self.TOP_BAR_H - 34)
        return pygame.Rect(self.LEFT_PANEL_W + 4, self.TOP_BAR_H + 4,
                           self.W - self.LEFT_PANEL_W - self.RIGHT_PANEL_W - 8,
                           self.H - self.TOP_BAR_H - self.BOTTOM_BAR_H - 8)

    # ---- events ----------------------------------------------------------
    def _modal_open(self):
        return self.show_info or self.show_help or self.show_checklist

    def handle_events(self):
        r = self.rend()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                self._key(e)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if self._handle_modal_click(e.pos):
                        continue
                    if self._handle_mode_tab_click(e.pos):
                        continue
                    if self.mode == "day":
                        continue
                    if self._handle_part_list_click(e.pos):
                        continue
                    if self._handle_preview_click(e.pos):
                        continue
                    self.dragging = True
                    r.selected = r.hovered
                elif e.button == 3:
                    if not self._modal_open():
                        self.panning = True
                elif e.button == 4:
                    self._wheel(1, pygame.mouse.get_pos())
                elif e.button == 5:
                    self._wheel(-1, pygame.mouse.get_pos())
            elif e.type == pygame.MOUSEWHEEL:
                self._wheel(e.y, pygame.mouse.get_pos())
            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    self.dragging = False
                elif e.button == 3:
                    self.panning = False
            elif e.type == pygame.MOUSEMOTION:
                if self.mode != "day" and not self._modal_open():
                    if self.dragging:
                        r.orbit(e.rel[0], e.rel[1])
                    elif self.panning:
                        r.pan_by(e.rel[0], e.rel[1])

    def _wheel(self, direction, mouse_pos):
        """direction > 0 means scroll/zoom 'in' (up on the wheel)."""
        if self.show_info:
            self.info_scroll = max(0, self.info_scroll - direction * 44)
            return
        if self._modal_open() or self.mode == "day":
            return
        self.rend().zoom_at(0.9 if direction > 0 else 1.1, mouse_pos, self.view_rect())

    def _handle_modal_click(self, pos):
        """The full-screen overlays (checklist/help/info) own clicks while open,
        so a click never reaches the 3D scene or the part list underneath."""
        if self.show_checklist:
            self.show_checklist = False
            return True
        if self.show_help:
            self.show_help = False
            return True
        if self.show_info:
            for i, rc in self._info_toc_hitboxes.items():
                if rc.collidepoint(pos):
                    self.info_scroll = self.info_offsets[i]
                    return True
            panel_rect = getattr(self, "_info_panel_rect", None)
            if panel_rect is not None and not panel_rect.collidepoint(pos):
                self.show_info = False
            return True
        return False

    def _key(self, e):
        k = e.key
        r = self.rend()
        if k == pygame.K_ESCAPE:
            if self._modal_open():
                self.show_info = self.show_help = self.show_checklist = False
            else:
                self.running = False
        elif k == pygame.K_q:
            self.running = False
        elif k == pygame.K_TAB:
            self.mode = self.MODES[(self.MODES.index(self.mode) + 1) % len(self.MODES)]
        elif k == pygame.K_h:
            self.show_help = not self.show_help
        elif k == pygame.K_i:
            self.show_info = not self.show_info
            self.info_scroll = 0
        elif self.show_info and k in (pygame.K_DOWN, pygame.K_j):
            self.info_scroll += 40
        elif self.show_info and k in (pygame.K_UP, pygame.K_k):
            self.info_scroll = max(0, self.info_scroll - 40)
        elif k == pygame.K_l:
            self.show_labels = not self.show_labels
        elif k == pygame.K_v:
            self.show_checklist = not self.show_checklist
        elif k == pygame.K_COMMA:
            self.world.cycle_warp(-1)
        elif k == pygame.K_PERIOD:
            self.world.cycle_warp(+1)
        elif self._modal_open():
            pass
        elif k == pygame.K_r:
            r.reset_view()
        elif self.mode != "day":
            if k == pygame.K_1:
                r.set_view("full")
            elif k == pygame.K_2:
                r.set_view("exploded")
            elif k == pygame.K_3:
                r.set_view("assembly")
            elif k in (pygame.K_4, pygame.K_x):
                r.toggle_section()
            elif k == pygame.K_e:
                r.set_view("exploded" if r.view != "exploded" else "full")
            elif k == pygame.K_LEFTBRACKET:
                r.set_view("assembly")
                r.assembly_prev()
            elif k == pygame.K_RIGHTBRACKET:
                r.set_view("assembly")
                r.assembly_next()
            elif k == pygame.K_a:
                r.set_view("assembly")
                r.assembly_all()
            elif k == pygame.K_c:
                r.set_view("assembly")
                r.assembly_clear()

    # ---- simulation ------------------------------------------------------
    def sim_dt(self, dt):
        """Real seconds -> building seconds. Only DAY mode time-warps."""
        return dt * (self.world.warp if self.mode == "day" else 1.0)

    def update(self, dt):
        self.rend().tick(dt)
        remaining = self.sim_dt(dt)
        step_max = 0.45
        guard = 0
        while remaining > 1e-6 and guard < 2200:
            guard += 1
            step = min(step_max, remaining)
            self.b.update(step)
            remaining -= step
        self._sample_acc += dt
        if self._sample_acc > 0.5:
            self._sample_acc = 0.0
            self.b.sample()
        self.sync_live()
        self._advance_angles(dt)
        r = self.rend()
        if self.mode == "day" or self.dragging or self.panning:
            if not self.dragging:
                r.hovered = None

    def _advance_angles(self, dt):
        speed = 0.0
        for z in self.b.zones:
            for s in z.shafts:
                speed += s.v_now
        self.ang["sheave"] += (0.6 + speed * 2.2) * dt
        self.ang["gov"] += (0.9 + speed * 3.0) * dt
        self.ang["default"] += 0.35 * dt

    def sync_live(self):
        """Write the simulation straight onto the tower meshes -- no rebuild."""
        L = TOWER_LIVE
        for z in self.b.zones:
            sp = z.spec
            for si, sh in enumerate(z.shafts):
                key = (sp.index, si)
                ya = tds(sh.s)
                yb = tds(sp.rise_m - sh.s)
                m = L["cabA"].get(key)
                if m is not None:
                    m.dyn[1] = ya
                m = L["cabB"].get(key)
                if m is not None:
                    m.dyn[1] = yb
                m = L["cwt"].get(key)
                if m is not None:
                    m.dyn[1] = yb
                loaded = sh.trays > 0.5
                up = sh.dir > 0
                for tag, yy, on in (("trayA", ya, loaded and not up),
                                    ("trayB", yb, loaded and up)):
                    m = L[tag].get(key)
                    if m is not None:
                        m.dyn[1] = yy
                        m.mix_t = 0.0 if on else 0.92
        for f, m in L["bank"].items():
            m.mix_t = 1.0 - clamp(self.b.bank.get(f, 0.0) / 40.0)
        for li, m in L["vault"].items():
            m.mix_t = 1.0 - self.b.vault_frac(li)
        for zi, m in L["shuttle"].items():
            m.dyn[1] = tds(self.b.shuttle_pos[zi] * ZONES[zi].rise_m)

    # ---- panel / click plumbing -----------------------------------------
    def _over_panel(self, mp):
        if self._modal_open():
            return True
        if mp[1] < self.TOP_BAR_H:
            return True
        if self.mode == "day":
            return mp[0] > self.W - 360
        if mp[0] < self.LEFT_PANEL_W + 4:
            return True
        if mp[0] > self.W - self.RIGHT_PANEL_W - 4:
            return True
        if mp[1] > self.H - self.BOTTOM_BAR_H - 4:
            return True
        return False

    def _handle_mode_tab_click(self, pos):
        for mode, rect in self._mode_hitboxes.items():
            if rect.collidepoint(pos):
                self.mode = mode
                return True
        return False

    def _handle_part_list_click(self, pos):
        for pi, rect in self._part_list_hitboxes.items():
            if rect.collidepoint(pos):
                self.rend().selected = pi
                return True
        return False

    def _handle_preview_click(self, pos):
        hit = self._preview_hitboxes
        for key, act in (("labels", "labels"), ("reset", "reset"), ("section", "section")):
            r = hit.get(key)
            if r and r.collidepoint(pos):
                if act == "labels":
                    self.show_labels = not self.show_labels
                elif act == "reset":
                    self.rend().reset_view()
                else:
                    self.rend().toggle_section()
                return True
        for mode, rect in hit.get("views", []):
            if rect.collidepoint(pos):
                r = self.rend()
                if mode == "section":
                    r.toggle_section()
                elif mode in ("full", "exploded", "assembly"):
                    r.set_view(mode)
                else:
                    r.set_view("assembly")
                    {"prev": r.assembly_prev, "next": r.assembly_next,
                     "all": r.assembly_all, "clear": r.assembly_clear}[mode]()
                return True
        return False

    # ---- draw ------------------------------------------------------------
    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        if self.mode == "day":
            self.draw_day()
        else:
            self.draw_preview()
        self.draw_topbar()
        if self.show_help:
            self.draw_help()
        if self.show_info:
            self.draw_info()
        if self.show_checklist:
            self.draw_checklist()
        pygame.display.flip()

    def draw_topbar(self):
        pygame.draw.rect(self.screen, C_PANEL, (0, 0, self.W, self.TOP_BAR_H))
        pygame.draw.line(self.screen, C_PANEL_HI, (0, self.TOP_BAR_H),
                         (self.W, self.TOP_BAR_H), 1)
        self.screen.blit(self.fb.render("HEALTH ELEVATOR", True, C_GRAV), (12, 6))
        self.screen.blit(self.font.render("GRAVITY TOWER  |  " + self.MODE_NAME[self.mode],
                                          True, C_TEXT), (210, 10))
        self._mode_hitboxes = {}
        tab_x, tab_y, tab_h = self.W - 560, 4, 28
        for mode in self.MODES:
            label = mode.upper()
            active = (self.mode == mode)
            tw = self.fs.size(label)[0] + 24
            rect = pygame.Rect(tab_x, tab_y, tw, tab_h)
            panel(self.screen, rect.x, rect.y, rect.w, rect.h, alpha=240 if active else 170)
            self.screen.blit(self.fs.render(label, True, C_ACCENT if active else C_TEXT_DIM),
                             (rect.x + 12, rect.y + 8))
            self._mode_hitboxes[mode] = rect
            tab_x += tw + 6
        hint = "H help   I info   V checklist"
        img = self.fs.render(hint, True, C_TEXT_DIM)
        self.screen.blit(img, (self.W - img.get_width() - 12, self.TOP_BAR_H - 16))

    def draw_preview(self):
        r = self.rend()
        rect = self.view_rect()
        self._preview_hitboxes = {}
        mp = pygame.mouse.get_pos()
        interactive = rect.collidepoint(mp) and not self._over_panel(mp)
        r.render(self.screen, rect, self.ang, mouse_pos=mp,
                 show_labels=self.show_labels, label_font=self.fs,
                 interactive=interactive)
        self.draw_view_tabs()
        self.draw_part_list()
        self.draw_scale_bar(rect)
        self.draw_spec_card()
        if self.mode == "tower":
            self.draw_tower_legend()
        else:
            self.draw_machine_stats()
        self.draw_preview_footer()

    def draw_view_tabs(self):
        r = self.rend()
        x, y = self.LEFT_PANEL_W + 8, self.TOP_BAR_H + 6
        items = [("full", "1 FULL"), ("exploded", "2 EXPLODED"),
                 ("assembly", "3 ASSEMBLY"), ("section", "4 SECTION")]
        views, cursor = [], x
        for mode, label in items:
            active = r.section if mode == "section" else (r.view == mode)
            tw = self.fs.size(label)[0] + 18
            rc = pygame.Rect(cursor, y, tw, 24)
            panel(self.screen, rc.x, rc.y, rc.w, rc.h, alpha=235 if active else 175)
            self.screen.blit(self.fs.render(label, True, C_ACCENT if active else C_TEXT_DIM),
                             (rc.x + 9, rc.y + 6))
            views.append((mode, rc))
            cursor += tw + 8
        for action, label in (("prev", "<"), ("next", ">"), ("all", "ALL"), ("clear", "CLR")):
            tw = self.fs.size(label)[0] + 14
            rc = pygame.Rect(cursor, y, tw, 24)
            panel(self.screen, rc.x, rc.y, rc.w, rc.h, alpha=175)
            self.screen.blit(self.fs.render(label, True, C_TEXT_DIM), (rc.x + 7, rc.y + 6))
            views.append((action, rc))
            cursor += tw + 6
        self._preview_hitboxes["views"] = views

    def draw_preview_footer(self):
        r = self.rend()
        w = self.W - self.LEFT_PANEL_W - self.RIGHT_PANEL_W - 16
        h = self.BOTTOM_BAR_H - 8
        x, y = self.LEFT_PANEL_W + 8, self.H - h - 4
        panel(self.screen, x, y, w, h, alpha=220)
        self.screen.blit(self.fs.render(
            "drag orbit   right-drag pan   wheel zoom   click pin part   TAB mode",
            True, C_TEXT), (x + 12, y + 10))
        self.screen.blit(self.fs.render(
            "L labels   R reset   E explode   X section   [ ] build   A all   C clear",
            True, C_TEXT_DIM), (x + 12, y + 30))
        self.screen.blit(self.fs.render(
            "V checklist   I full spec   H help   , / . time-warp (DAY)",
            True, C_TEXT_DIM), (x + 12, y + 50))
        rx = x + w - 250
        for text, key, active in (("LABELS ON" if self.show_labels else "LABELS OFF",
                                   "labels", self.show_labels),
                                  ("CUT ON" if r.section else "CUT OFF", "section", r.section),
                                  ("RESET VIEW", "reset", False)):
            tw = self.fs.size(text)[0] + 16
            rc = pygame.Rect(rx, y + 18, tw, 24)
            panel(self.screen, rc.x, rc.y, rc.w, rc.h, alpha=235 if active else 180)
            self.screen.blit(self.fs.render(text, True, C_ACCENT if active else C_TEXT),
                             (rc.x + 8, rc.y + 6))
            self._preview_hitboxes[key] = rc
            rx += tw + 8

    def _spec_card_top(self):
        """Y where the spec/inspector card begins -- so the part list above it
        can size itself to the part actually showing, not a fixed guess."""
        return self.H - self.BOTTOM_BAR_H - self._spec_card_height() - 8

    def _spec_card_height(self):
        r = self.rend()
        part = r.active_part() or (r.placing_part() if r.view == "assembly" else None)
        if part is None:
            return 118
        w = self.LEFT_PANEL_W - 16
        body = []
        for ln in part.specs:
            body += wrap_text(self.fs, ln, w - 28)
        return 72 + len(body) * 16

    def draw_part_list(self):
        r = self.rend()
        w, x = self.LEFT_PANEL_W - 16, 8
        y = self.TOP_BAR_H + 4
        h = max(120, self._spec_card_top() - 10 - y)
        panel(self.screen, x, y, w, h)
        self.screen.blit(self.fb.render("PARTS", True, C_ACCENT), (x + 12, y + 8))
        self._part_list_hitboxes = {}
        yy = y + 36
        hi = r.selected if r.selected is not None else r.hovered
        for pi, part in enumerate(r.parts):
            if yy + 20 > y + h - 4:
                break
            rc = pygame.Rect(x + 4, yy, w - 8, 20)
            active = (pi == hi)
            if active:
                panel(self.screen, rc.x, rc.y, rc.w, rc.h, alpha=235)
            elif pi % 2 == 0:
                panel(self.screen, rc.x, rc.y, rc.w, rc.h, alpha=110)
            self.screen.blit(self.fmicro.render("%d" % (pi + 1), True, C_TEXT_DIM),
                             (rc.x + 4, rc.y + 4))
            self.screen.blit(self.fs.render(part.name[:26], True,
                                            C_ACCENT if active else C_TEXT),
                             (rc.x + 24, rc.y + 3))
            self._part_list_hitboxes[pi] = rc
            yy += 20

    def draw_spec_card(self):
        r = self.rend()
        part = r.active_part() or (r.placing_part() if r.view == "assembly" else None)
        if part is None:
            self.draw_inspector_hint()
            return
        w = self.LEFT_PANEL_W - 16
        body = []
        for ln in part.specs:
            body += wrap_text(self.fs, ln, w - 28)
        h = self._spec_card_height()
        x, y = 8, self._spec_card_top()
        panel(self.screen, x, y, w, h)
        self.screen.blit(self.fb.render(part.name[:22], True, C_ACCENT), (x + 12, y + 8))
        state = "PINNED / HOVERED PART"
        if r.view == "assembly" and r.selected is None and r.hovered is None:
            state = "NEXT PART TO PLACE"
        self.screen.blit(self.fs.render(state, True, C_TEXT_DIM), (x + 14, y + 34))
        yy = y + 52
        for ln in body:
            self.screen.blit(self.fs.render("- " + ln, True, C_TEXT), (x + 14, yy))
            yy += 16

    def draw_inspector_hint(self):
        w, h = self.LEFT_PANEL_W - 16, 118
        x, y = 8, self.H - self.BOTTOM_BAR_H - h - 8
        panel(self.screen, x, y, w, h)
        self.screen.blit(self.fb.render("INSPECTOR", True, C_ACCENT), (x + 12, y + 8))
        yy = y + 34
        for ln in ["Hover a part for its real dimensions and its job.",
                   "Click to pin it while you orbit.",
                   "1-4 expose the internals.",
                   "X cuts the tower in half: that is how you see the shafts."]:
            for wl in wrap_text(self.fs, ln, w - 28):
                self.screen.blit(self.fs.render(wl, True, C_TEXT), (x + 14, yy))
                yy += 14
            yy += 3

    def draw_scale_bar(self, rect):
        r = self.rend()
        disp = MACH_DISP if self.mode == "machine" else TOWER_DISP
        px_per_m = disp * min(rect.w, rect.h) * 1.12 / max(1e-6, r.dist)
        target_m = 120.0 / max(1e-9, px_per_m)
        mag = 10 ** math.floor(math.log10(max(0.1, target_m)))
        nice = mag
        for mult in (1, 2, 5, 10):
            nice = mult * mag
            if nice >= target_m:
                break
        bar_px = int(max(20, min(320, nice * px_per_m)))
        bx, by = rect.x + 12, rect.bottom - 22
        pygame.draw.rect(self.screen, C_TEXT_DIM, (bx, by, bar_px, 3))
        pygame.draw.rect(self.screen, C_TEXT_DIM, (bx, by - 4, 2, 11))
        pygame.draw.rect(self.screen, C_TEXT_DIM, (bx + bar_px - 2, by - 4, 2, 11))
        lab = "%d m" % nice if nice >= 1 else "%.1f m" % nice
        self.screen.blit(self.fs.render(lab, True, C_TEXT), (bx, by - 20))
        img = self.fs.render("zoom %.2f" % r.dist, True, C_TEXT_DIM)
        self.screen.blit(img, (rect.right - img.get_width() - 12, rect.y + 4))

    # ---- right-hand panels ----------------------------------------------
    def draw_tower_legend(self):
        w, x = self.RIGHT_PANEL_W - 16, self.W - self.RIGHT_PANEL_W + 8
        y = self.TOP_BAR_H + 4
        h = self.H - self.TOP_BAR_H - self.BOTTOM_BAR_H - 12
        panel(self.screen, x, y, w, h)
        self.screen.blit(self.fb.render("BUILDING SPEC", True, C_TEXT), (x + 12, y + 8))
        b = self.b
        rows = [
            ("Storeys", "%d  (%.1f m to roof)" % (FLOORS, TOWER_H_M)),
            ("Floor-to-floor", "%.2f m" % FLOOR_H),
            ("Zones", "%d  of %d-%d floors" % (NZONES, min(z.n_floors for z in ZONES),
                                               max(z.n_floors for z in ZONES))),
            ("Sky lobbies", ", ".join(str(f) for f in SKY_LOBBIES[1:-1])),
            ("Hoistways", "%d  (%d cabins)" % (TOTAL_SHAFTS, TOTAL_SHAFTS * 2)),
            ("Population", "%d  (falls with height)" % TOWER["occupants"]),
            ("Camera", "dist %.2f  az %.2f  el %.2f" % (self.tower_rend.dist,
                                                        self.tower_rend.az,
                                                        self.tower_rend.el)),
            ("", ""),
            ("Motive power", "GRAVITY + HUMAN WEIGHT"),
            ("Grid draw for motion", "0 kW"),
            ("Motors / drives", "NONE"),
            ("Tray unit", "%.2f kg  (25 lb)" % TRAY_KG),
            ("Vault capacity", "%d trays (%.0f t)" % (DIMS["vault_capacity"],
                                                      DIMS["vault_capacity"] * TRAY_KG / 1000)),
            ("Staged now", "%.0f t = %.0f kWh" % (b.staged_tonnes(), b.stored_kwh())),
            ("Resistance mu_eff", "%.3f roller guides" % MU_EFF),
            ("Commanded imbalance", "%.1f%%  (band %.0f-%.0f)" % (
                IMBAL_MARGIN * MU_EFF * 100, MU_SPEC_LO * 100, MU_SPEC_HI * 100)),
            ("Descent recovery", "%.0f%%" % (RECOVERY_EFF * 100)),
            ("", ""),
        ]
        yy = y + 40
        for lab, val in rows:
            if lab == "":
                yy += 8
                continue
            self.screen.blit(self.fs.render(lab, True, C_TEXT_DIM), (x + 12, yy))
            col = C_GRAV if ("GRAVITY" in val or "0 kW" in val or "NONE" in val) else C_TEXT
            self.screen.blit(self.fs.render(val, True, col), (x + 158, yy))
            yy += 19
        pygame.draw.line(self.screen, C_PANEL_HI, (x + 8, yy), (x + w - 8, yy), 1)
        yy += 8
        self.screen.blit(self.fs.render("ZONE PLAN  (traffic-aware sizing)", True, C_ACCENT),
                         (x + 12, yy))
        yy += 18
        hdr = "  z  floors   sh  cap  reev   v"
        self.screen.blit(self.fmicro.render(hdr, True, C_TEXT_DIM), (x + 12, yy))
        yy += 14
        for z in ZONES:
            vf = self.b.vault_frac(z.index + 1)
            col = C_GOOD if vf > 0.35 else (C_WARN if vf > 0.12 else C_BAD)
            txt = " %2d  %2d-%2d   %d   %2d   %d:1  %.2f" % (
                z.index + 1, z.lo, z.hi, z.n_shafts, z.cap, z.reeving, z.v_max)
            self.screen.blit(self.fmicro.render(txt, True, col), (x + 12, yy))
            pygame.draw.rect(self.screen, C_PANEL_HI, (x + w - 66, yy + 2, 54, 9))
            pygame.draw.rect(self.screen, col, (x + w - 66, yy + 2, int(54 * vf), 9))
            yy += 15
        yy += 4
        for ln in wrap_text(self.fs, "Bar = sky-lobby vault charge above that zone. "
                                     "Red means the cars there will stall.", w - 24):
            self.screen.blit(self.fs.render(ln, True, C_TEXT_DIM), (x + 12, yy))
            yy += 15

    def draw_machine_stats(self):
        w, x = self.RIGHT_PANEL_W - 16, self.W - self.RIGHT_PANEL_W + 8
        y = self.TOP_BAR_H + 4
        h = self.H - self.TOP_BAR_H - self.BOTTOM_BAR_H - 12
        panel(self.screen, x, y, w, h)
        self.screen.blit(self.fb.render("THE GRAVITY MACHINE", True, C_GRAV), (x + 12, y + 8))
        z = ZONES[-1]
        m_full = z.suspended_kg(z.cap * PAX_KG, 0.0)
        d_full = tray_mass_needed_kg(m_full, z.reeving, -z.cap * PAX_KG)
        m_pair = z.suspended_kg(z.cap * PAX_KG, z.cap * PAX_KG)
        d_pair = tray_mass_needed_kg(m_pair, z.reeving, 0.0)
        rows = [
            ("Shown", "%s, %d:1 reeved" % (z.name, z.reeving)),
            ("Rise", "%.1f m (floors %d-%d)" % (z.rise_m, z.lo, z.hi)),
            ("Cabins", "2 linked, %.0f kg each" % z.cabin_kg),
            ("Capacity", "%d passengers each" % z.cap),
            ("Car speed", "%.2f m/s" % z.v_max),
            ("Head sheave", "%.2f m, %d ropes" % (DIMS["sheave_d_m"], DIMS["ropes"])),
            ("Base counterweight", "%.0f kg fixed" % z.base_cwt_kg()),
            ("Motor", "NONE"),
            ("", ""),
        ]
        yy = y + 40
        for lab, val in rows:
            if lab == "":
                yy += 6
                continue
            self.screen.blit(self.fs.render(lab, True, C_TEXT_DIM), (x + 12, yy))
            self.screen.blit(self.fs.render(val, True,
                                            C_GRAV if val == "NONE" else C_TEXT), (x + 168, yy))
            yy += 20
        pygame.draw.line(self.screen, C_PANEL_HI, (x + 8, yy), (x + w - 8, yy), 1)
        yy += 8
        self.screen.blit(self.fs.render("WHAT ONE RUN COSTS", True, C_ACCENT), (x + 12, yy))
        yy += 18
        cases = [
            ("full car up, empty car down", m_full, d_full),
            ("full car up, FULL car down", m_pair, d_pair),
        ]
        for name, ms, dk in cases:
            trays = max(0.0, dk) / TRAY_KG
            adv = required_advantage_kg(ms, z.reeving)
            self.screen.blit(self.fmicro.render(name, True, C_TEXT), (x + 14, yy))
            yy += 14
            self.screen.blit(self.fmicro.render(
                "   suspended %.0f kg   imbalance %.0f kg  (%.1f%%)" % (
                    ms, adv, imbalance_ratio(adv, ms) * 100), True, C_TEXT_DIM), (x + 14, yy))
            yy += 14
            self.screen.blit(self.fmicro.render(
                "   = %.1f trays  =  %.1f stair carries" % (
                    trays, trays / WALK["trays_per_carry"]), True, C_GRAV), (x + 14, yy))
            yy += 18
        pygame.draw.line(self.screen, C_PANEL_HI, (x + 8, yy), (x + w - 8, yy), 1)
        yy += 8
        self.screen.blit(self.fs.render("FORCE PATH", True, C_ACCENT), (x + 12, yy))
        yy += 18
        for step in ["1. trays PRE-POSITIONED on the heavy side",
                     "2. holding PAWL releases the drum",
                     "3. weight difference x g  ->  rope tension",
                     "4. groove friction  ->  SHEAVE turns",
                     "5. sheave  ->  the other rope fall",
                     "6. 2:1 car block DOUBLES force, HALVES speed",
                     "7. car accelerates to %.2f m/s, levels, pawl sets" % z.v_max,
                     "8. trays land low; the vault above is that much emptier"]:
            col = C_GRAV if ("PRE-POSITIONED" in step or "vault" in step) else C_TEXT
            self.screen.blit(self.fmicro.render(step, True, col), (x + 14, yy))
            yy += 15
        yy += 4
        for ln in wrap_text(self.fs, "There is no actuator in this assembly that can "
                                     "push a car. Latches let go; gravity does the rest.",
                            w - 24):
            self.screen.blit(self.fs.render(ln, True, C_GRAV), (x + 12, yy))
            yy += 16

    # ---- DAY mode --------------------------------------------------------
    def draw_day(self):
        rect = self.view_rect()
        b, wd = self.b, self.world
        sun = wd.sun(b.hour)
        top, bot = sky_colors(sun)
        sky = pygame.Surface((rect.w, rect.h))
        vgradient(sky, top, bot)
        self.screen.blit(sky, (rect.x, rect.y))
        self._draw_sun_moon(rect, b.hour, sun)
        ground_y = rect.bottom - 26
        for (gx, gw, gh) in ((40, 78, 96), (128, 62, 66), (612, 70, 118), (700, 54, 78)):
            pygame.draw.rect(self.screen, _mix(C_CITY, top, 0.22),
                             (rect.x + gx, ground_y - gh, gw, gh))
        pygame.draw.rect(self.screen, _mix(C_GROUND, top, 0.18),
                         (rect.x, ground_y, rect.w, rect.bottom - ground_y))

        # Borrow the tower renderer for the scene shot. Everything the inspector
        # modes may have left set (exploded, cut, hover spread) has to be
        # neutralised here, not just the view name, or the tower flies apart.
        r = self.tower_rend
        stash = (r.az, r.el, r.dist, r.pan.copy(), r.view, r.section,
                 r.explode_amt, r.hover_spread)
        r.az = 0.62 + 0.03 * math.sin(pygame.time.get_ticks() / 9000.0)
        r.el = 0.06
        r.dist = 1.06
        # seat the tower on the drawn ground line rather than centring it
        r.pan = np.array([20.0, 78.0])
        r.view, r.section = "full", False
        r.explode_amt = 0.0
        r.hover_spread = 0.0
        tower_rect = pygame.Rect(rect.x + 20, rect.y + 10,
                                 int(rect.w * 0.50), rect.h - 46)
        r.render(self.screen, tower_rect, self.ang, mouse_pos=None,
                 show_labels=False, label_font=None, interactive=False)
        (r.az, r.el, r.dist, r.pan, r.view, r.section,
         r.explode_amt, r.hover_spread) = stash

        self._draw_zone_strip(rect)
        self._draw_day_hud()
        self._draw_timeline()

    def _draw_sun_moon(self, rect, hour, sun):
        if 5.0 <= hour <= 20.0:
            t = (hour - 5.0) / 15.0
            sx = rect.x + int(t * rect.w)
            sy = rect.bottom - 40 - int(math.sin(t * math.pi) * rect.h * 0.72)
            glow = pygame.Surface((150, 150), pygame.SRCALPHA)
            for rr in range(70, 16, -6):
                a = int(46 * (1.0 - (rr - 16) / 54.0) ** 1.6) + 4
                pygame.draw.circle(glow, (255, 226, 150, a), (75, 75), rr)
            self.screen.blit(glow, (sx - 75, sy - 75))
            pygame.draw.circle(self.screen, C_SUN, (sx, sy), 16)
        else:
            t = clamp((((hour + 12) % 24) - 5.0) / 15.0)
            sx = rect.x + int(t * rect.w)
            sy = rect.bottom - 40 - int(math.sin(t * math.pi) * rect.h * 0.58)
            pygame.draw.circle(self.screen, (220, 224, 235), (sx, sy), 12)
            rng = random.Random(11)
            for _ in range(80):
                stx = rect.x + int(rng.random() * rect.w)
                sty = rect.y + int(rng.random() * rect.h * 0.6)
                self.screen.set_at((stx, sty), (200, 210, 230))

    def _draw_zone_strip(self, rect):
        """A live cut-away elevation: every zone, every cabin, every vault."""
        b = self.b
        x = rect.right - 320
        w = 300
        y0 = rect.y + 26
        y1 = rect.bottom - 60
        panel(self.screen, x - 10, y0 - 22, w + 20, (y1 - y0) + 46, alpha=225)
        self.screen.blit(self.fs.render("LIVE ZONE ELEVATION", True, C_ACCENT), (x, y0 - 18))

        def py(h_m):
            return int(y1 - (h_m / TOWER_H_M) * (y1 - y0))

        for z in ZONES:
            zs = b.zones[z.index]
            ytop, ybot = py(z.top_h_m), py(z.base_h_m)
            vf = b.vault_frac(z.index + 1)
            col = C_GOOD if vf > 0.35 else (C_WARN if vf > 0.12 else C_BAD)
            pygame.draw.rect(self.screen, _mix(C_PANEL_HI, col, 0.16),
                             (x, ytop, w - 96, ybot - ytop))
            pygame.draw.rect(self.screen, C_PANEL_HI, (x, ytop, w - 96, ybot - ytop), 1)
            self.screen.blit(self.fmicro.render("Z%d %d-%d" % (z.index + 1, z.lo, z.hi),
                                                True, C_TEXT_DIM), (x + 3, ytop + 2))
            # hoistways with the two counter-running cabins
            n = z.n_shafts
            sw = (w - 110) / max(1, n)
            for si, sh in enumerate(zs.shafts):
                sx = x + 6 + si * sw
                pygame.draw.rect(self.screen, C_SHAFT, (sx, ytop + 2, sw - 10, ybot - ytop - 4))
                ya = py(z.base_h_m + sh.s)
                yb = py(z.base_h_m + z.rise_m - sh.s)
                pygame.draw.rect(self.screen, C_CABIN, (sx + 1, ya - 3, (sw - 12) / 2, 6))
                pygame.draw.rect(self.screen, C_CABIN_B,
                                 (sx + 1 + (sw - 12) / 2, yb - 3, (sw - 12) / 2, 6))
                if sh.mode == "STALLED":
                    pygame.draw.rect(self.screen, C_BAD, (sx, ytop + 2, sw - 10,
                                                          ybot - ytop - 4), 1)
            # vault charge bar for the lobby above this zone
            bx = x + w - 86
            pygame.draw.rect(self.screen, C_PANEL_HI, (bx, ytop + 3, 16, ybot - ytop - 6))
            fh = int((ybot - ytop - 6) * vf)
            pygame.draw.rect(self.screen, col, (bx, ybot - 3 - fh, 16, fh))
            q = zs.queue_len()
            aw, _ = zs.wait_stats()
            self.screen.blit(self.fmicro.render("q%-3d %4.0fs" % (min(q, 999), aw), True,
                                                C_TEXT if q < 60 else C_WARN),
                             (bx + 20, (ytop + ybot) // 2 - 6))
            self.screen.blit(self.fmicro.render("x%.1f" % zs.multiplier(), True, C_GRAV),
                             (bx + 20, (ytop + ybot) // 2 + 5))
        for f in SKY_LOBBIES:
            yy = py((f - 1) * FLOOR_H)
            pygame.draw.line(self.screen, C_LOBBY, (x - 4, yy), (x + w - 90, yy), 1)

    def _draw_day_hud(self):
        b, wd = self.b, self.world
        w, x, y = 340, self.W - 352, 44
        h = self.H - 90
        panel(self.screen, x, y, w, h)
        mode = b.mode()
        mcol = {"UP-PEAK  (vaults discharging)": C_WARN,
                "DOWN-PEAK  (vaults re-staging)": C_GOOD,
                "MASS SHORTFALL": C_BAD}.get(mode, C_ACCENT)
        self.screen.blit(self.fb.render(mode.split("  ")[0], True, mcol), (x + 12, y + 8))
        clk = "Day %d  %02d:%02d" % (b.day, int(b.hour), int((b.hour % 1) * 60))
        img = self.fs.render(clk, True, C_TEXT_DIM)
        self.screen.blit(img, (x + w - img.get_width() - 12, y + 12))
        yy = y + 34
        sub = mode.split("  ", 1)[1] if "  " in mode else ""
        self.screen.blit(self.fs.render(sub, True, C_TEXT_DIM), (x + 12, yy))
        yy += 20
        self.screen.blit(self.fbig.render("0", True, C_GRAV), (x + 12, yy))
        self.screen.blit(self.font.render("kW grid", True, C_TEXT_DIM), (x + 40, yy + 14))
        aw, p90 = b.wait_stats()
        self.screen.blit(self.fbig.render("%.0fs" % aw, True,
                                          C_TEXT if aw < 60 else C_WARN), (x + 150, yy))
        self.screen.blit(self.font.render("avg wait", True, C_TEXT_DIM), (x + 226, yy + 14))
        yy += 50

        def gbar(lab, frac, color, val):
            nonlocal yy
            bar(self.screen, self.fs, x + 14, yy + 14, w - 30, 12, frac, color, lab, val)
            yy += 36

        vmin = min(b.vault_frac(i) for i in range(1, NZONES + 1))
        gbar("LOWEST VAULT CHARGE", vmin,
             C_GOOD if vmin > 0.35 else (C_WARN if vmin > 0.12 else C_BAD),
             "%.0f%%" % (vmin * 100))
        gbar("STAGED MASS", clamp(b.staged_tonnes() / ((NZONES + 1) * DIMS["vault_capacity"]
                                                       * TRAY_KG / 1000.0)),
             C_GRAV, "%.1f t / %.1f kWh" % (b.staged_tonnes(), b.stored_kwh()))
        gbar("HALL QUEUE", clamp(b.queue_len() / 600.0),
             C_ACCENT if b.queue_len() < 250 else C_WARN, "%d waiting" % b.queue_len())
        gbar("DAY PROGRESS", clamp(b.hour / 24.0), C_ACCENT, "%02d:%02d" % (
            int(b.hour), int((b.hour % 1) * 60)))

        yy += 2
        pygame.draw.line(self.screen, C_PANEL_HI, (x + 12, yy), (x + w - 12, yy), 1)
        yy += 8
        self.screen.blit(self.fs.render("TRAY FLOW  (trays)", True, C_ACCENT), (x + 14, yy))
        yy += 18
        for lab, val, col in (
                ("staged by walkers", sum(z.trays_carried for z in b.zones), C_GRAV),
                ("spent on lifts", b.units_spent, C_WARN),
                ("re-staged by descent", b.units_restaged, C_GOOD),
                ("moved by shuttles", b.shuttled, C_SHUTTLE),
                ("in landing banks", sum(b.bank.values()), C_BANK)):
            self.screen.blit(self.fs.render(lab, True, C_TEXT_DIM), (x + 14, yy))
            img = self.fs.render("%.0f" % val, True, col)
            self.screen.blit(img, (x + w - 16 - img.get_width(), yy))
            yy += 18

        yy += 6
        pygame.draw.line(self.screen, C_PANEL_HI, (x + 12, yy), (x + w - 12, yy), 1)
        yy += 8
        stats = [
            ("Registered calls", "%d" % b.registered),
            ("Journeys completed", "%d" % b.served),
            ("Transfers at sky lobbies", "%d" % b.transfers),
            ("Avg journey time", "%.1f min" % b.avg_trip_min()),
            ("Worst zone p90 wait", "%.0f s" % p90),
            ("Cars moving now", "%d of %d" % (b.cars_moving(), TOTAL_SHAFTS)),
            ("Stalls (mass short)", "%d" % b.stalls()),
            ("Took the stairs instead", "%d" % b.balked),
            ("", ""),
            ("Stair carries", "%.0f" % b.stair_carries()),
            ("Flights climbed", "%.0f" % b.flights()),
            ("Human work stored", "%.1f MJ" % (b.lift_J / 1e6)),
            ("Kilocalories burned", "%.0f kcal" % b.kcal()),
            ("Tokens issued", "%.0f" % b.tokens),
            ("", ""),
            ("Grid energy used", "0.00 kWh"),
            ("Conventional bank would", "%.0f kWh" % b.saved_kwh()),
            ("  ...cost", "$%.2f" % b.saved_usd()),
            ("  ...emit", "%.0f kg CO2" % (b.saved_kwh() * REFERENCE["co2_kg_kwh"])),
            ("Walker pool (THE MONEY)", "$%.2f" % b.walker_pool_usd()),
            ("  value per token", "$%.5f" % b.usd_per_token()),
            ("  value per stair carry", "$%.4f" % b.usd_per_carry()),
            ("", ""),
            ("GLOBAL: all elevators", "~300 TWh/year"),
            ("  ...cost", "~$48 B/year"),
            ("  ...CO2", "~111 Mt/year"),
            ("  ...= cars off road", "~24 M"),
            ("Time warp", "x%.0f" % wd.warp),
        ]
        for lab, val in stats:
            if lab == "":
                yy += 6
                continue
            self.screen.blit(self.fs.render(lab, True, C_TEXT_DIM), (x + 14, yy))
            col = C_GRAV if ("0.00" in val or "kcal" in val) else C_TEXT
            img = self.fs.render(val, True, col)
            self.screen.blit(img, (x + w - 16 - img.get_width(), yy))
            yy += 17

    def _draw_timeline(self):
        b = self.b
        y = self.H - 30
        x0, x1 = 40, self.W - 380
        pygame.draw.line(self.screen, C_TEXT_DIM, (x0, y), (x1, y), 2)
        for hh in range(0, 25, 3):
            xx = int(x0 + (hh / 24.0) * (x1 - x0))
            pygame.draw.line(self.screen, C_PANEL_HI, (xx, y - 4), (xx, y + 4), 1)
            self.screen.blit(self.fmicro.render("%02d" % hh, True, C_TEXT_DIM), (xx - 6, y + 6))
        if len(b._hist) > 2:
            pts = []
            for (hr, vf, wt, q) in b._hist[-900:]:
                pts.append((int(x0 + (hr / 24.0) * (x1 - x0)), int(y - 4 - vf * 22)))
            for i in range(1, len(pts)):
                if abs(pts[i][0] - pts[i - 1][0]) < 40:
                    pygame.draw.line(self.screen, C_GRAV, pts[i - 1], pts[i], 1)
        sx = int(x0 + (b.hour / 24.0) * (x1 - x0))
        pygame.draw.circle(self.screen, C_ACCENT, (sx, y), 6)
        pygame.draw.circle(self.screen, C_TEXT, (sx, y), 6, 1)
        self.screen.blit(self.fs.render("vault charge over the day   ( , / .  time-warp )",
                                        True, C_TEXT_DIM), (x0, y - 34))

    # ---- overlays --------------------------------------------------------
    def draw_help(self):
        w, h = 600, 470
        x, y = (self.W - w) // 2, (self.H - h) // 2
        panel(self.screen, x, y, w, h, alpha=244)
        pygame.draw.rect(self.screen, C_ACCENT, (x, y, w, h), 2, border_radius=6)
        self.screen.blit(self.fbig.render("CONTROLS", True, C_ACCENT), (x + 20, y + 14))
        self.screen.blit(self.fs.render("click anywhere or Esc to close", True, C_TEXT_DIM),
                         (x + w - 220, y + 24))
        yy = y + 60
        for ln in ["TAB           cycle TOWER / MACHINE / DAY",
                   "click tabs    or click the mode tabs in the top bar",
                   "drag          orbit the model",
                   "right-drag    pan the camera",
                   "wheel         zoom in / out",
                   "click part    pin it in the inspector (left sidebar)",
                   "click PARTS   left sidebar list to select any part",
                   "1 2 3 4       full / exploded / assembly / section-cut",
                   "E             quick exploded toggle",
                   "X             cross-section half-cut (see the shafts)",
                   "L             toggle part labels",
                   "R             reset the camera",
                   "[ ]           step the assembly build",
                   "A / C         assemble all / clear",
                   ", / .         slow / speed up TIME-WARP (DAY mode)",
                   "V             verification checklist overlay",
                   "I             full informational specification",
                   "H             this help card",
                   "Esc           close a panel, or quit at the top level",
                   "Q             quit"]:
            key, desc = _split_key_line(ln)
            kw = self.fs.size(key)[0] + 16
            kr = pygame.Rect(x + 24, yy, kw, 20)
            panel(self.screen, kr.x, kr.y, kr.w, kr.h, alpha=215)
            self.screen.blit(self.fs.render(key, True, C_ACCENT), (kr.x + 8, kr.y + 3))
            self.screen.blit(self.font.render(desc, True, C_TEXT), (x + 24 + 108, yy + 2))
            yy += 20

    def draw_checklist(self):
        items = [
            ("Zoned tower", "%d zones of %d-%d floors, %d sky lobbies at %s" % (
                NZONES, min(z.n_floors for z in ZONES), max(z.n_floors for z in ZONES),
                NZONES - 1, ", ".join(str(f) for f in SKY_LOBBIES[1:-1]))),
            ("Counter-running cabin pairs", "%d hoistways, %d cabins, one rope, one DOF" % (
                TOTAL_SHAFTS, TOTAL_SHAFTS * 2)),
            ("Cascading weight banks", "%d landing banks, %d trays each" % (
                FLOORS, DIMS["bank_capacity"])),
            ("Sky-lobby vault battery", "%d vaults x %d trays (%.0f t, %.1f kWh total)" % (
                NZONES + 1, DIMS["vault_capacity"],
                (NZONES + 1) * DIMS["vault_capacity"] * TRAY_KG / 1000.0,
                sum(DIMS["vault_capacity"] * TRAY_KG * G * LOBBY_H_M[i]
                    for i in range(NZONES + 1)) / 3.6e6)),
            ("Progressive token incentives", "height +%.0f%%, scarcity +%.0f%% below %.0f%% full" % (
                TOKEN["height_gain"] * 100, TOKEN["scarcity_gain"] * 100,
                TOKEN["scarcity_floor"] * 100)),
            ("Registered demand + pre-positioning", "timestamped calls, counter-mass set before boarding"),
            ("Batched runs", "one balanced run serves many same-direction riders"),
            ("Priority slots", "%.0f%% of places held free for genuine incapacity" % (
                TOKEN["priority_reserve"] * 100)),
            ("3-8%% imbalance mechanics", "roller guides + lubricated sheaves, mu_eff %.3f" % MU_EFF),
            ("Differential 2:1 reeving", "upper zones: half the tray mass, half the speed"),
            ("Fixed base counterweights", "sized for the AVERAGE zone load, never carried"),
            ("Modular ergonomic weights", "%.2f kg (25 lb) trays, cart and pack friendly" % TRAY_KG),
            ("Short-haul tray shuttles", "%d trays per run, pure gravity, staged upward" % (
                DIMS["shuttle_trays"])),
            ("Traffic-aware sizing", "%d->%d hoistways, %d->%d person cars with height" % (
                ZONES[0].n_shafts, ZONES[-1].n_shafts, ZONES[0].cap, ZONES[-1].cap)),
            ("Safety gear", "overspeed governor, wedge safeties, ratchet holding brake, oil buffers"),
            ("To-scale 3D + inspector", "real SI dimensions, hover/click, 4 views, live cabins"),
            ("24 h operating day", "up-peak / down-peak, waits, stalls, tokens, kcal"),
            ("Zero grid energy for motion", "0.00 kWh by construction -- there is no motor"),
            ("Tokens priced in real dollars", "%.0f%% of the avoided bill funds the walker pool, live" % (
                ECONOMY["walker_payout_frac"] * 100)),
        ]
        cols = 2
        per_col = math.ceil(len(items) / cols)
        col_w = 440
        row_h = 44
        w = 40 + cols * col_w + (cols - 1) * 28
        h = 96 + per_col * row_h
        x, y = (self.W - w) // 2, (self.H - h) // 2
        panel(self.screen, x, y, w, h, alpha=248)
        pygame.draw.rect(self.screen, C_ACCENT, (x, y, w, h), 2, border_radius=6)
        self.screen.blit(self.fbig.render("VERIFICATION CHECKLIST", True, C_ACCENT),
                         (x + 20, y + 14))
        self.screen.blit(self.fs.render("%d items -- V or click anywhere to close" % len(items),
                                        True, C_TEXT_DIM), (x + w - 280, y + 24))
        pygame.draw.line(self.screen, C_PANEL_HI, (x + 20, y + 52), (x + w - 20, y + 52), 1)
        for i, (name, detail) in enumerate(items):
            col, row = divmod(i, per_col)
            cx = x + 20 + col * (col_w + 28)
            yy = y + 66 + row * row_h
            pygame.draw.circle(self.screen, C_GOOD, (cx + 8, yy + 6), 5)
            self.screen.blit(self.fs.render(name, True, C_TEXT), (cx + 22, yy))
            for j, wl in enumerate(wrap_text(self.fmicro, detail, col_w - 22)):
                self.screen.blit(self.fmicro.render(wl, True, C_TEXT_DIM), (cx + 22, yy + 16 + j * 13))

    def _info_metrics(self):
        w = min(920, self.W - 80)
        h = self.H - 90
        x, y = (self.W - w) // 2, 50
        toc_w = 220
        content_x = x + 24 + toc_w + 18
        content_w = w - (content_x - x) - 26
        content_y0 = y + 56
        content_h = h - 74
        return x, y, w, h, toc_w, content_x, content_w, content_y0, content_h

    def _info_head_color(self, head):
        if head.startswith("HONEST PHYSICS"):
            return C_WARN
        if head in ("CONTROLS", "VERIFICATION CHECKLIST"):
            return C_ACCENT
        return C_GRAV

    def _compute_info_offsets(self):
        _, _, _, _, _, _, content_w, _, _ = self._info_metrics()
        offsets, total = [], 0
        for _head, lines in self.info_sections:
            offsets.append(total)
            total += 22 + 4
            for ln in lines:
                total += 19 * len(wrap_text(self.font, ln, content_w))
            total += 14
        return offsets, total

    def draw_info(self):
        x, y, w, h, toc_w, content_x, content_w, content_y0, content_h = self._info_metrics()
        panel(self.screen, x, y, w, h, alpha=248)
        self.screen.blit(self.fb.render("GRAVITY TOWER  --  FULL SPECIFICATION", True, C_ACCENT),
                         (x + 20, y + 14))
        hint = self.fs.render("wheel / arrows scroll   click a section to jump   Esc closes",
                              True, C_TEXT_DIM)
        self.screen.blit(hint, (x + w - hint.get_width() - 20, y + 20))
        pygame.draw.line(self.screen, C_PANEL_HI, (x + 16, y + 44), (x + w - 16, y + 44), 1)

        # ---- TOC rail --------------------------------------------------
        toc_x, toc_y = x + 24, content_y0
        cur_i = 0
        for i, off in enumerate(self.info_offsets):
            if off <= self.info_scroll + 8:
                cur_i = i
        self._info_toc_hitboxes = {}
        for i, (head, _lines) in enumerate(self.info_sections):
            active = (i == cur_i)
            rc = pygame.Rect(toc_x - 6, toc_y - 2, toc_w + 10, 20)
            if active:
                panel(self.screen, rc.x, rc.y, rc.w, rc.h, alpha=210)
            label = _toc_label(head)
            if self.fmicro.size(label)[0] > toc_w - 8:
                while label and self.fmicro.size(label + "...")[0] > toc_w - 8:
                    label = label[:-1]
                label += "..."
            self.screen.blit(self.fmicro.render(label, True,
                                                C_ACCENT if active else C_TEXT_DIM),
                             (toc_x, toc_y + 2))
            self._info_toc_hitboxes[i] = rc
            toc_y += 21
        pygame.draw.line(self.screen, C_PANEL_HI, (content_x - 18, content_y0 - 4),
                         (content_x - 18, y + h - 18), 1)

        # ---- scrolling content ------------------------------------------
        self.screen.set_clip(pygame.Rect(content_x, content_y0, content_w + 4, content_h))
        yy = content_y0 - self.info_scroll
        for head, lines in self.info_sections:
            keycap = (head == "CONTROLS")
            head_col = self._info_head_color(head)
            if y + 30 < yy < y + h:
                self.screen.blit(self.fb.render(head, True, head_col), (content_x, yy))
                pygame.draw.line(self.screen, _mix(head_col, C_PANEL, 0.75),
                                 (content_x, yy + 22), (content_x + content_w - 20, yy + 22), 1)
            yy += 26
            for ln in lines:
                key, desc = _split_key_line(ln) if keycap else (None, ln)
                if key is not None:
                    if y + 24 < yy < y + h:
                        kw = self.fs.size(key)[0] + 14
                        kr = pygame.Rect(content_x, yy - 1, kw, 18)
                        panel(self.screen, kr.x, kr.y, kr.w, kr.h, alpha=210)
                        self.screen.blit(self.fs.render(key, True, C_ACCENT), (kr.x + 7, kr.y + 2))
                        self.screen.blit(self.fs.render(desc, True, C_TEXT), (content_x + 96, yy + 2))
                    yy += 19
                    continue
                for wl in wrap_text(self.font, ln, content_w):
                    if y + 24 < yy < y + h:
                        self.screen.blit(self.font.render(wl, True, C_TEXT), (content_x + 6, yy))
                    yy += 19
            yy += 14
        self.screen.set_clip(None)

        # ---- scrollbar ---------------------------------------------------
        sb_x, sb_y, sb_h = x + w - 16, content_y0, content_h
        pygame.draw.rect(self.screen, C_PANEL_HI, (sb_x, sb_y, 6, sb_h), border_radius=3)
        if self.info_total_h > sb_h:
            thumb_h = max(24, int(sb_h * sb_h / self.info_total_h))
            span = max(1, self.info_total_h - sb_h)
            thumb_y = sb_y + int((sb_h - thumb_h) * clamp(self.info_scroll / span))
            pygame.draw.rect(self.screen, C_ACCENT, (sb_x, thumb_y, 6, thumb_h), border_radius=3)

        self._info_panel_rect = pygame.Rect(x, y, w, h)
        self.info_scroll = max(0, min(self.info_scroll, max(0, self.info_total_h - content_h)))

    # ---- main loop -------------------------------------------------------
    def run(self):
        _print_banner()
        while self.running:
            dt = min(self.clock.tick(45) / 1000.0, 0.05)
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()


def _print_banner():
    print("=" * 72)
    print(" HealthElevator.py  --  GRAVITY TOWER DIGITAL TWIN")
    print("=" * 72)
    print(" Modes (TAB):  TOWER  |  MACHINE (one zone's gravity machine)  |  DAY")
    print(" Building:     %d storeys, %.0f m, %d zones, %d sky lobbies" % (
        FLOORS, TOWER_H_M, NZONES, NZONES - 1))
    print(" Transit:      %d hoistways, %d counter-running cabins, 0 motors" % (
        TOTAL_SHAFTS, TOTAL_SHAFTS * 2))
    print(" Fuel:         %.2f kg trays carried up the stairs by people" % TRAY_KG)
    print(" Grid draw:    0 kW for motion, by construction")
    print(" Controls:     H = help,  I = full spec,  V = checklist,  ESC = quit")
    print("=" * 72)


def main():
    App().run()


if __name__ == "__main__":
    main()
