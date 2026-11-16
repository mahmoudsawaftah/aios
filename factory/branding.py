"""Generate a tiny original space-themed Windows icon without external packages.

This is an optional visual asset generated locally by the desktop shortcut installer.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
import struct
import zlib


def _chunk(tag: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + tag + payload + struct.pack(
        ">I", zlib.crc32(tag + payload) & 0xFFFFFFFF
    )


def _blend(base: tuple[int, int, int], tint: tuple[int, int, int], amount: float):
    amount = max(0.0, min(1.0, amount))
    return tuple(int(base[i] * (1.0 - amount) + tint[i] * amount) for i in range(3))


def _png(size: int) -> bytes:
    center = (size - 1) / 2.0
    pixels = bytearray()
    stars = ((.18,.17),(.83,.23),(.12,.75),(.86,.78),(.30,.89))
    for y in range(size):
        pixels.append(0)  # PNG filter: None
        for x in range(size):
            u = (x-center)/(size*.5)
            v = (y-center)/(size*.5)
            r = math.hypot(u,v)
            col = (9,16,48)
            col = _blend(col,(52,39,103),max(0.0,1-r)*.65)
            # Soft nebula behind the planet.
            glow = max(0, 1 - math.hypot(u*.95+.18,v*.95-.14)/.95)
            col = _blend(col,(51,102,178),glow*.32)
            # Planet with a glossy lit crescent.
            pr = math.hypot((u+.03)/.53,(v-.02)/.53)
            if pr < 1.0:
                light = max(0.0,1.0-math.hypot(u+.23,v+.26)*1.1)
                col = _blend((55,55,139),(133,197,253),min(.94,light*.95))
                if pr > .95:
                    col = _blend(col,(147,171,252),.35)
            # Thin Saturn-style orbit, rotated 25 degrees.
            theta = math.radians(-28)
            xx = u*math.cos(theta)+v*math.sin(theta)
            yy = -u*math.sin(theta)+v*math.cos(theta)
            ellipse = (xx/.87)**2+(yy/.31)**2
            if .89 < ellipse < 1.11 and (pr > .95 or yy > .02):
                col = _blend(col,(94,235,251),.94)
            for sx,sy in stars:
                d = math.hypot(x/size-sx,y/size-sy)
                if d < .012:
                    col = (210,250,255)
                elif d < .03:
                    col = _blend(col,(125,209,255),(.03-d)/.03*.6)
            pixels.extend((*col,255))
    image = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB",size,size,8,6,0,0,0))
        + _chunk(b"IDAT",zlib.compress(bytes(pixels),9))
        + _chunk(b"IEND",b"")
    )
    return image


def create_icon(path: Path) -> Path:
    sizes = [64,256]
    images = [_png(size) for size in sizes]
    header = struct.pack("<HHH",0,1,len(images))
    offset = 6 + 16 * len(images)
    entries = []
    for size, content in zip(sizes, images):
        # ICO uses 0 to represent 256px.
        entries.append(struct.pack("<BBBBHHII",size % 256,size % 256,0,0,1,32,len(content),offset))
        offset += len(content)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + b"".join(entries) + b"".join(images))
    return path


def main(argv=None):
    p = argparse.ArgumentParser(description="Create item space AI desktop icon")
    p.add_argument("--output",required=True,help="Absolute or relative icon file path")
    args = p.parse_args(argv)
    dest = Path(args.output).expanduser().resolve()
    create_icon(dest)
    print("Icon created: " + str(dest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
