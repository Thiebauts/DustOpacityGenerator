# Dust Opacity Generator

Generate temperature-dependent dust opacity files for RADMC-3D simulations, powered by [Optool](https://github.com/cdominik/optool) and [Karine Demyk's](https://www.irap.omp.eu/en/experimentation/the-astrodust-group/optical-properties/) silicate optical constants.

## What It Does

- Produces RADMC-3D-compatible `dustkappa_*.inp` files for 12 silicate compositions across arbitrary temperatures and grain sizes
- Supports composite core-mantle grains (e.g. silicate core + water ice mantle)
- Accepts both bundled Demyk optical constants and Optool's built-in material library

## Quick Start

```bash
# Clone and run with defaults (E40R silicate, 0.3 um, 10/100/200/300 K)
git clone https://github.com/<user>/DustOpacityGenerator.git
cd DustOpacityGenerator
python run_optool.py
```

Output files land in `radmc3d_model/`:
```
dustkappa_E40R_10K_a0.3.inp
dustkappa_E40R_100K_a0.3.inp
dustkappa_E40R_200K_a0.3.inp
dustkappa_E40R_300K_a0.3.inp
```

## Requirements

- **Python** 3.10+ (standard library only, zero dependencies)
- **[Optool](https://github.com/cdominik/optool)** installed and on your `PATH`

## Usage

```
python run_optool.py [OPTIONS]
```

| Option | Default | Description |
|---|---|---|
| `--material` | `E40R` | Core dust material (local or built-in) |
| `--grain-size` | `0.3` | Grain size in microns |
| `--temperatures` | `10,100,200,300` | Comma-separated temperatures (K) |
| `--output-dir` | `radmc3d_model` | Output directory |
| `--nk-dir` | `data/nk_files` | Directory with `.lnk` files |
| `--no-temp-dependent` | | Single file without temperature dependence |
| `--mantle-material` | | Mantle composition (requires `--mantle-fraction`) |
| `--mantle-fraction` | | Mantle mass fraction, 0-1 (requires `--mantle-material`) |
| `-v, --verbose` | | Debug-level output |

### Examples

```bash
# Different material and grain size
python run_optool.py --material E20R --grain-size 0.5

# Custom temperature grid
python run_optool.py --temperatures 50,150,250,350

# Core-mantle grain: 20% x035 mantle around E40R core
python run_optool.py --material E40R --mantle-material x035 --mantle-fraction 0.2

# Built-in materials: 30% water ice mantle on pyroxene core
python run_optool.py --material pyr --mantle-material h2o --mantle-fraction 0.3
```

## Available Materials

### Bundled Demyk Silicates

Each material ships with optical constants at 10, 100, 200, and 300 K.

| Material | Composition | Density (g/cm^3) |
|---|---|---|
| x035 | (0.65)MgO-(0.35)SiO2 | 2.7 |
| x040 | (0.60)MgO-(0.40)SiO2 | 2.7 |
| x050A | (0.50)MgO-(0.50)SiO2 (structure A) | 2.7 |
| x050B | (0.50)MgO-(0.50)SiO2 (structure B) | 2.7 |
| E10 / E10R | Mg(0.9)Fe(0.1)SiO3 (Fe3+ / Fe2+) | 2.8 |
| E20 / E20R | Mg(0.8)Fe(0.2)SiO3 (Fe3+ / Fe2+) | 2.9 |
| E30 / E30R | Mg(0.7)Fe(0.3)SiO3 (Fe3+ / Fe2+) | 3.0 |
| E40 / E40R | Mg(0.6)Fe(0.4)SiO3 (Fe3+ / Fe2+) | 3.1 |

### Built-in Optool Materials

Optool provides additional materials (`pyr`, `ol`, `h2o`, `c`, `gra`, `sic`, `fe-c`, ...). Run `optool -c` for the full list. Any built-in material can serve as core or mantle.

## Output Naming Convention

```
dustkappa_{material}[_m{mantle}_{fraction}][_{temp}K]_a{size}.inp
```

| File | Meaning |
|---|---|
| `dustkappa_E40R_100K_a0.3.inp` | Pure E40R, 100 K, 0.3 um |
| `dustkappa_E40R_mx035_0.2_100K_a0.3.inp` | E40R + 20% x035 mantle |
| `dustkappa_E40R_a0.3.inp` | E40R, temperature-independent |

Mantle fractions are always written in decimal notation (no scientific notation).

## Project Structure

```
DustOpacityGenerator/
├── run_optool.py          # CLI entry point
├── data/
│   └── nk_files/          # Demyk optical constants (.lnk, 48 files)
├── LICENSE                # MIT
└── README.md
```

## License

[MIT](LICENSE)
