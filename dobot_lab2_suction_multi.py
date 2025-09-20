#!/usr/bin/env python3
"""
Lab 2.1 – Suction Cup sequence
Order: 1 -> 2 -> 4 -> 3 (forward), then back 3 -> 4 -> 2 -> 1 (return).
"""

import time, argparse

try:
    from pydobot.dobot import MODE_PTP
    import pydobot as dobot_mod
except Exception:
    from pydobot2.dobot import MODE_PTP
    import pydobot2 as dobot_mod

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="/dev/ttyACM0")
    ap.add_argument("--hover", type=float, default=30.0)
    ap.add_argument("--v", type=int, default=1000)
    ap.add_argument("--a", type=int, default=1000)
    ap.add_argument("--pick_dwell", type=float, default=0.6)
    ap.add_argument("--release_dwell", type=float, default=0.35)
    ap.add_argument("--hold", type=float, default=2.0)
    args = ap.parse_args()

    # Waypoints (replace with your measured ones)
    HOME      = dict(x=239.59, y=0.00,   z=149.46, r=0.00)
    ATPICK1   = dict(x=313.84, y=-89.02, z=-43.95, r=-15.83)
    ATPLACE1  = dict(x=308.05, y=-0.20,  z=-43.95, r=-0.04)
    ATPICK2   = dict(x=249.19, y=-88.08, z=-43.95, r=-19.46)
    ATPLACE2  = dict(x=248.49, y=-0.17,  z=-43.95, r=-0.04)
    ATPICK3   = dict(x=248.95, y=-31.49, z=-43.95, r=-7.20)
    ATPLACE3  = dict(x=309.47, y=58.85,  z=-43.95, r=10.77)
    ATPICK4   = dict(x=309.60, y=-31.26, z=-43.95, r=-5.76)
    ATPLACE4  = dict(x=247.78, y=57.10,  z=-43.95, r=12.98)

    def hover(pt): return {**pt, "z": pt["z"] + args.hover}
    def mov(pt, mode=MODE_PTP.MOVJ_XYZ, wait=0.3): dev.move_to(mode=int(mode), **pt); time.sleep(wait)

    def pick_then_lift(above, at):
        mov(above); mov(at)
        dev.suck(True); time.sleep(args.pick_dwell)
        mov(above)

    def place_then_release(above, at):
        mov(above); mov(at)
        time.sleep(args.hold)
        dev.suck(False); time.sleep(args.release_dwell)
        mov(above)

    dev = dobot_mod.Dobot(port=args.port)
    try:
        dev.speed(args.v, args.a)
        dev.home(); time.sleep(1.0)

        # Forward
        pick_then_lift(hover(ATPICK1), ATPICK1); place_then_release(hover(ATPLACE1), ATPLACE1)
        pick_then_lift(hover(ATPICK2), ATPICK2); place_then_release(hover(ATPLACE2), ATPLACE2)
        pick_then_lift(hover(ATPICK4), ATPICK4); place_then_release(hover(ATPLACE4), ATPLACE4)
        pick_then_lift(hover(ATPICK3), ATPICK3); place_then_release(hover(ATPLACE3), ATPLACE3)

        # Return
        pick_then_lift(hover(ATPLACE3), ATPLACE3); place_then_release(hover(ATPICK3), ATPICK3)
        pick_then_lift(hover(ATPLACE4), ATPLACE4); place_then_release(hover(ATPICK4), ATPICK4)
        pick_then_lift(hover(ATPLACE2), ATPLACE2); place_then_release(hover(ATPICK2), ATPICK2)
        pick_then_lift(hover(ATPLACE1), ATPLACE1); place_then_release(hover(ATPICK1), ATPICK1)

        mov(HOME)
        print("✅ Suction sequence complete")
    finally:
        dev.close()


if __name__ == "__main__":
    main()