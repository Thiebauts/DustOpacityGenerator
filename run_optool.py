#!/usr/bin/env python3
"""
Dust Opacity Generator

Generates dust opacity files for astrophysical simulations using Optool,
with support for Karine Demyk dust optical constants, temperature-dependent
opacities, and composite core-mantle grain structures.
"""

import argparse
import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path

log = logging.getLogger(__name__)

# Default values
DEFAULT_MATERIAL = "E40R"
DEFAULT_GRAIN_SIZE = 0.3
DEFAULT_TEMPERATURES = [10, 100, 200, 300]
DEFAULT_NK_DIR = Path("data/nk_files")
DEFAULT_OUTPUT_DIR = Path("radmc3d_model")

# Regex for validating material names (alphanumeric, hyphens, underscores)
_SAFE_MATERIAL_RE = re.compile(r"^[A-Za-z0-9_\-]+$")

# Material densities (g/cm^3)
MATERIAL_DENSITIES: dict[str, float] = {
    "x035": 2.7,   # (0.65)MgO-(0.35)SiO2
    "x040": 2.7,   # (0.60)MgO-(0.40)SiO2
    "x050A": 2.7,  # (0.50)MgO-(0.50)SiO2 structure A
    "x050B": 2.7,  # (0.50)MgO-(0.50)SiO2 structure B
    "E10": 2.8,    # Mg(0.9)Fe(0.1)SiO3; Fe3+
    "E10R": 2.8,   # Mg(0.9)Fe(0.1)SiO3; Fe2+
    "E20": 2.9,    # Mg(0.8)Fe(0.2)SiO3; Fe3+
    "E20R": 2.9,   # Mg(0.8)Fe(0.2)SiO3; Fe2+
    "E30": 3.0,    # Mg(0.7)Fe(0.3)SiO3; Fe3+
    "E30R": 3.0,   # Mg(0.7)Fe(0.3)SiO3; Fe2+
    "E40": 3.1,    # Mg(0.6)Fe(0.4)SiO3; Fe3+
    "E40R": 3.1,   # Mg(0.6)Fe(0.4)SiO3; Fe2+
}


def _validate_material_name(name: str) -> None:
    """Raise ValueError if a material name contains unsafe characters."""
    if not _SAFE_MATERIAL_RE.match(name):
        raise ValueError(
            f"Invalid material name '{name}'. "
            "Only alphanumeric characters, hyphens, and underscores are allowed."
        )


def check_optool() -> bool:
    """Check if Optool is installed and accessible."""
    try:
        result = subprocess.run(
            ["optool", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        return (
            result.returncode == 0
            or "optool" in result.stdout.lower()
            or "optool" in result.stderr.lower()
        )
    except FileNotFoundError:
        return False


def find_nk_file(
    material: str,
    temp: int | None = None,
    nk_dir: Path = DEFAULT_NK_DIR,
) -> Path | None:
    """Find the .lnk file for a given material and optional temperature.

    Search order:
      1. Temperature-specific file  ({material}_{temp}K.lnk)
      2. Exact match               ({material}.lnk)
      3. Partial (case-insensitive) match among directory entries
    """
    if not nk_dir.is_dir():
        log.error("Directory %s not found.", nk_dir)
        return None

    if temp is not None:
        temp_file = nk_dir / f"{material}_{temp}K.lnk"
        if temp_file.exists():
            return temp_file

    exact_file = nk_dir / f"{material}.lnk"
    if exact_file.exists():
        return exact_file

    for path in sorted(nk_dir.iterdir()):
        if path.suffix.lower() == ".lnk" and material.lower() in path.name.lower():
            if temp is not None:
                log.warning(
                    "Using %s which may not match %dK exactly.", path.name, temp
                )
            return path

    return None


def format_mantle_fraction(fraction: float | None) -> str:
    """Format a mantle fraction as a clean decimal string (no scientific notation)."""
    if fraction is None:
        return ""
    return f"{fraction:.10f}".rstrip("0").rstrip(".")


def run_optool(
    material: str,
    grain_size: float,
    temp: int | None = None,
    nk_dir: Path = DEFAULT_NK_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    mantle_material: str | None = None,
    mantle_fraction: float | None = None,
) -> Path | None:
    """Run Optool to generate a single opacity file.

    Returns the path to the generated file, or None on failure.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Resolve core material
    nk_file = find_nk_file(material, temp, nk_dir)
    if nk_file:
        core_arg = str(nk_file)
    else:
        log.info("Using built-in optool material: %s", material)
        core_arg = material

    # Resolve mantle material
    mantle_arg: str | None = None
    if mantle_material and mantle_fraction:
        mantle_nk = find_nk_file(mantle_material, temp, nk_dir)
        if mantle_nk:
            mantle_arg = str(mantle_nk)
        else:
            log.info("Using built-in optool material for mantle: %s", mantle_material)
            mantle_arg = mantle_material

    temp_dir = output_dir / "temp_optool"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        cmd: list[str] = [
            "optool",
            core_arg,
            "-radmc",
            "-a", str(grain_size),
            "-o", str(temp_dir),
        ]

        if mantle_arg and mantle_fraction:
            cmd.extend(["-m", mantle_arg, str(mantle_fraction)])

        status_parts = [f"{material}, grain size {grain_size}\u03bcm"]
        if temp:
            status_parts.append(f"at {temp}K")
        if mantle_material and mantle_fraction:
            status_parts.append(
                f"with {mantle_material} mantle ({mantle_fraction * 100:.1f}%)"
            )
        log.info("Running Optool for %s...", " ".join(status_parts))

        subprocess.run(cmd, capture_output=True, text=True, check=True)

        source_file = temp_dir / "dustkappa.inp"
        if not source_file.exists():
            log.error("Expected output file %s not found.", source_file)
            return None

        # Build final filename
        base_material = re.sub(r"_\d+K$", "", material)
        mantle_suffix = (
            f"_m{mantle_material}_{format_mantle_fraction(mantle_fraction)}"
            if mantle_material
            else ""
        )
        temp_part = f"_{temp}K" if temp else ""
        final_name = f"dustkappa_{base_material}{mantle_suffix}{temp_part}_a{grain_size}.inp"

        final_path = output_dir / final_name
        shutil.copy2(source_file, final_path)

        log.info("Generated: %s", final_name)
        return final_path

    except subprocess.CalledProcessError as exc:
        log.error("Optool failed: %s", exc)
        if exc.stdout:
            log.error("stdout: %s", exc.stdout.strip())
        if exc.stderr:
            log.error("stderr: %s", exc.stderr.strip())
        return None
    except Exception:
        log.exception("Unexpected error")
        return None
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate dust opacity files using Optool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Default parameters (material={DEFAULT_MATERIAL}, grain-size={DEFAULT_GRAIN_SIZE})
  python run_optool.py

  # Custom material and grain size
  python run_optool.py --material E20R --grain-size 0.5

  # Custom temperatures
  python run_optool.py --temperatures 50,150,250

  # Single temperature-independent file
  python run_optool.py --material E40R --grain-size 0.3 --no-temp-dependent

  # Core-mantle grain with local materials (20% x035 mantle on E40R core)
  python run_optool.py --material E40R --grain-size 0.3 --mantle-material x035 --mantle-fraction 0.2

  # Core-mantle grain with built-in optool materials (30% water ice on pyroxene)
  python run_optool.py --material pyr --grain-size 0.3 --mantle-material h2o --mantle-fraction 0.3
        """,
    )

    parser.add_argument(
        "--material",
        default=DEFAULT_MATERIAL,
        help=(
            f"Core dust material (default: {DEFAULT_MATERIAL}). "
            f"Local: {', '.join(MATERIAL_DENSITIES)}. "
            'Built-in: run "optool -c" for full list.'
        ),
    )
    parser.add_argument(
        "--grain-size",
        type=float,
        default=DEFAULT_GRAIN_SIZE,
        help=f"Grain size in microns (default: {DEFAULT_GRAIN_SIZE})",
    )
    parser.add_argument(
        "--temperatures",
        default=",".join(map(str, DEFAULT_TEMPERATURES)),
        help=f'Comma-separated temperatures in K (default: {",".join(map(str, DEFAULT_TEMPERATURES))})',
    )
    parser.add_argument(
        "--nk-dir",
        type=Path,
        default=DEFAULT_NK_DIR,
        help=f"Directory with .lnk files (default: {DEFAULT_NK_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--no-temp-dependent",
        action="store_true",
        help="Generate a single file without temperature dependency",
    )
    parser.add_argument(
        "--mantle-material",
        default=None,
        help=(
            "Mantle material (optional). Accepts local or built-in optool materials."
        ),
    )
    parser.add_argument(
        "--mantle-fraction",
        type=float,
        default=None,
        help="Mantle mass fraction relative to core (e.g. 0.2 = 20%%)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose (debug) output",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    # --- Validation ----------------------------------------------------------

    if not check_optool():
        log.error(
            "Optool not found. Install it and ensure it is in your PATH.\n"
            "  https://github.com/cdominik/optool"
        )
        return 1

    # Material name safety
    try:
        _validate_material_name(args.material)
        if args.mantle_material:
            _validate_material_name(args.mantle_material)
    except ValueError as exc:
        log.error("%s", exc)
        return 1

    # Mantle arguments must come in pairs
    if args.mantle_material and args.mantle_fraction is None:
        log.error("--mantle-fraction is required when --mantle-material is specified.")
        return 1
    if args.mantle_fraction is not None and args.mantle_material is None:
        log.error("--mantle-material is required when --mantle-fraction is specified.")
        return 1
    if args.mantle_fraction is not None and not (0 < args.mantle_fraction <= 1):
        log.error("--mantle-fraction must be between 0 (exclusive) and 1 (inclusive).")
        return 1

    # Grain size must be positive
    if args.grain_size <= 0:
        log.error("--grain-size must be positive.")
        return 1

    # Warn about unknown materials
    for label, name in [("Core", args.material), ("Mantle", args.mantle_material)]:
        if name and name not in MATERIAL_DENSITIES:
            log.info(
                "%s material '%s' not in local database; will try as built-in optool material.",
                label,
                name,
            )

    if not args.nk_dir.is_dir():
        log.error("Directory '%s' not found.", args.nk_dir)
        return 1

    # --- Execution -----------------------------------------------------------

    if args.no_temp_dependent:
        result = run_optool(
            args.material,
            args.grain_size,
            nk_dir=args.nk_dir,
            output_dir=args.output_dir,
            mantle_material=args.mantle_material,
            mantle_fraction=args.mantle_fraction,
        )
        return 0 if result else 1

    temperatures: list[int] = []
    for t in args.temperatures.split(","):
        t = t.strip()
        try:
            val = int(t)
        except ValueError:
            log.error("Invalid temperature value: '%s'", t)
            return 1
        if val <= 0:
            log.error("Temperatures must be positive, got %d.", val)
            return 1
        temperatures.append(val)

    log.info("Generating opacity files for temperatures: %s", temperatures)
    if args.mantle_material:
        log.info(
            "Mantle: %s (%.1f%% of core mass)",
            args.mantle_material,
            args.mantle_fraction * 100,
        )

    success_count = sum(
        1
        for temp in temperatures
        if run_optool(
            args.material,
            args.grain_size,
            temp,
            args.nk_dir,
            args.output_dir,
            args.mantle_material,
            args.mantle_fraction,
        )
    )

    log.info("Generated %d/%d files.", success_count, len(temperatures))
    log.info("Output directory: %s", args.output_dir.resolve())

    return 0 if success_count == len(temperatures) else 1


if __name__ == "__main__":
    sys.exit(main())
