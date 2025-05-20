#!/usr/bin/env python3
"""
vox2raw.py
==========

Convert a custom ASCII .vox phantom (ID  density per voxel) into a
header-less 32-bit float .raw file containing linear attenuation
coefficients μ (cm⁻¹) for mgfpj.

Usage
-----
    python vox2raw.py  input.vox  output.raw
    # 可选：--quiet  只打印关键信息
"""
from pathlib import Path
import argparse
import numpy as np
import sys

# ----------------------------------------------------------------------
# ① 配置材料表 —— μ/ρ (cm² / g) @100 keV
#    若用其他能量或材料，请在这里改！
MU_RHO = {
    1: 0.1541,   # Air     (ρ≈0.001204 g/cm³)
    2: 0.1641,   # PMMA    (ρ≈1.18 g/cm³)
    3: 0.3717,   # Fe      (ρ≈7.874 g/cm³)
    # 继续添加新材料 ID…
}
# ----------------------------------------------------------------------


def parse_header(lines):
    """
    读取前 7 行 header，返回 (nx, ny, nz), (vx, vy, vz)
    """
    dims = list(map(int, lines[1].split()[:3]))
    vox_sizes = list(map(float, lines[2].split()[:3]))
    return dims, vox_sizes


def vox_to_raw(vox_path: Path, raw_path: Path, quiet=False):
    with vox_path.open("r") as f:
        hdr = [next(f) for _ in range(7)]
        (nx, ny, nz), _ = parse_header(hdr)
        nvox_expected = nx * ny * nz

        # 读取余下 nvox 行
        ids = np.fromiter(
            (int(line.split()[0]) for line in f),
            dtype=np.int32,
            count=nvox_expected,
        )

    if ids.size != nvox_expected:
        raise RuntimeError(
            f"[{vox_path}] 体素数不匹配：header={nvox_expected} 行，实际={ids.size} 行"
        )

    # 查 μ/ρ→μ；先构造密度表（第 2 列），再算 μ
    # 读取 density 同时算 μ 更直观
    with vox_path.open("r") as f:
        _ = [next(f) for _ in range(7)]  # skip header
        rho = np.fromiter(
            (float(line.split()[1]) for line in f),
            dtype=np.float32,
            count=nvox_expected,
        )

    mu_rho = np.vectorize(MU_RHO.get)(ids)
    if np.any(mu_rho == None):
        unknown = set(ids[mu_rho == None])
        raise KeyError(f"未知材料 ID：{unknown}. 请在 MU_RHO 中补充。")

    mu = mu_rho.astype(np.float32) * rho  # μ = (μ/ρ) × ρ

    # mgfpj slice-major: (Z, Y, X) -> flatten (C-order)
    mu = mu.reshape((ny, nz, nx))       # (Z, Y, X)
    raw_path.write_bytes(mu.tobytes())

    if not quiet:
        print(f"✓ {vox_path.name}  →  {raw_path.name}")
        print(f"  shape = (Z,Y,X) = {mu.shape}, dtype=float32, "
              f"size = {raw_path.stat().st_size/1e6:.2f} MB")


# ─────────────────────────── 主程序 ────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Convert .vox phantom to .raw (μ).")
    ap.add_argument("vox_path", type=Path, help=".vox file")
    ap.add_argument("out_path", type=Path,
                    help="output .raw file OR directory to store .raw")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    # 如果第二个参数是目录，则自动沿用 .vox 文件名
    out_path = args.out_path
    if out_path.is_dir():
        out_path = out_path / args.vox_path.with_suffix('.raw').name

    try:
        vox_to_raw(args.vox_path, out_path, quiet=args.quiet)   # ←← 这里！
    except Exception as e:
        print("转换失败:", e, file=sys.stderr)
        sys.exit(1)



if __name__ == "__main__":
    main()
