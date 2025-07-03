# Dust Property Generator using Optool

A simple tool that generates dust opacity files for different temperatures using Optool, specifically designed to use Karine Demyk dust optical constants.

## Project Structure

```
DustOpacityGenerator/
├── run_optool.py          # Main script
├── data/
│   └── nk_files/          # Material optical constants (.lnk files)
├── README.md
└── LICENSE
```

## Requirements

- [Optool](https://github.com/cdominik/optool) must be installed and accessible in your PATH
- Python 3.6+ (uses only standard library modules)

## Quick Start

Generate dust properties for the default 4 temperatures (10K, 100K, 200K, 300K):

```bash
python run_optool.py --material E40R --grain-size 0.3 --output-dir dust_files
```

## Command Line Options

- `--material`: Dust material composition for the core (default: E40R)
  - Can use local materials: x035, x040, x050A, x050B, E10, E10R, E20, E20R, E30, E30R, E40, E40R
  - Can also use built-in optool materials (run `optool -c` for full list)
- `--grain-size`: Grain size in microns (default: 0.3)
- `--temperatures`: Comma-separated temperatures in K (default: 10,100,200,300)
- `--output-dir`: Directory to save output files (default: radmc3d_model)
- `--nk-dir`: Directory containing .lnk files (default: data/nk_files)
- `--mantle-material`: Mantle material (optional, can use local or built-in optool materials)
- `--mantle-fraction`: Mantle mass fraction relative to core mass (e.g., 0.2 for 20% mantle)

## Examples

Generate files for different material:
```bash
python run_optool.py --material E20R --grain-size 0.5 --output-dir my_dust_files
```

Generate for custom temperatures:
```bash
python run_optool.py --material E40R --grain-size 0.3 --temperatures 50,150,250,350
```

Generate single temperature file:
```bash
python run_optool.py --material E40R --grain-size 0.3 --no-temp-dependent
```

**NEW: Generate files with mantle using local materials** (20% x035 mantle around E40R core):
```bash
python run_optool.py --material E40R --grain-size 0.3 --mantle-material x035 --mantle-fraction 0.2
```

**NEW: Generate files with mantle using built-in optool materials** (30% water ice mantle around pyroxene core):
```bash
python run_optool.py --material pyr --grain-size 0.3 --mantle-material h2o --mantle-fraction 0.3
```

**NEW: Generate files with mantle for specific temperatures**:
```bash
python run_optool.py --material E40R --mantle-material x035 --mantle-fraction 0.15 --temperatures 100,200,300
```

## Mantle Functionality

The tool now supports adding mantles around dust grains using Optool's `-m` option. This allows you to model composite grains with different core and mantle materials.

### Key Features:
- **Core Material**: Any local material or built-in optool material can be used as the core
- **Mantle Material**: Any local material or built-in optool material can be used as the mantle
- **Mantle Fraction**: The mass fraction of the mantle relative to the core mass (e.g., 0.2 means the mantle is 20% of the core mass)
- **Temperature Consistency**: The same temperature is used for both core and mantle materials when available
- **Mixed Material Types**: You can mix local and built-in materials (e.g., local E40R core with built-in h2o mantle)

### Usage Notes:
- Both `--mantle-material` and `--mantle-fraction` must be specified together
- The mantle fraction should be between 0 and 1 (exclusive of 0)
- The tool will automatically find appropriate .lnk files for local materials or use built-in optool materials
- Output files include a mantle suffix to distinguish them from pure core files
- For a full list of built-in optool materials, run: `optool -c`

## Output

The script generates files named: `dustkappa_{material}[_mantle_info]_{temperature}K_a{size}.inp`

Examples:
- Pure core: `dustkappa_E40R_100K_a0.3.inp`
- With mantle (20%): `dustkappa_E40R_mx035_2e-01_100K_a0.3.inp`
- With mantle (0.5%): `dustkappa_E40R_mx035_5e-03_100K_a0.3.inp`
- With mantle (0.1%): `dustkappa_E40R_mx035_1e-03_100K_a0.3.inp`
- With mantle (0.001%): `dustkappa_E40R_mx035_1e-05_100K_a0.3.inp`

### Mantle Fraction Formatting

The mantle fraction in filenames is formatted using scientific notation for consistency and clarity:
- **0.2** → `2e-01`
- **0.15** → `1e-01` 
- **0.001** → `1e-03`
- **0.00001** → `1e-05`

This ensures that all mantle fractions are clearly distinguishable in filenames, regardless of their magnitude.

## Available Dust Materials

### Local Materials (with .lnk files in this package)

| Material | Composition | Density (g/cm³) |
|----------|-------------|-----------------|
| x035 | (0.65)MgO-(0.35)SiO2 | 2.7 |
| x040 | (0.60)MgO-(0.40)SiO2 | 2.7 |
| x050A | (0.50)MgO-(0.50)SiO2 structure A | 2.7 |
| x050B | (0.50)MgO-(0.50)SiO2 structure B | 2.7 |
| E10 | Mg(0.9)Fe(0.1)SiO3; Fe³⁺ | 2.8 |
| E10R | Mg(0.9)Fe(0.1)SiO3; Fe²⁺ | 2.8 |
| E20 | Mg(0.8)Fe(0.2)SiO3; Fe³⁺ | 2.9 |
| E20R | Mg(0.8)Fe(0.2)SiO3; Fe²⁺ | 2.9 |
| E30 | Mg(0.7)Fe(0.3)SiO3; Fe³⁺ | 3.0 |
| E30R | Mg(0.7)Fe(0.3)SiO3; Fe²⁺ | 3.0 |
| E40 | Mg(0.6)Fe(0.4)SiO3; Fe³⁺ | 3.1 |
| E40R | Mg(0.6)Fe(0.4)SiO3; Fe²⁺ | 3.1 |

### Built-in Optool Materials

Optool includes many additional built-in materials such as:
- `pyr` - Pyroxene
- `h2o` - Water ice
- `c` - Carbon
- `gra` - Graphite
- `sic` - Silicon carbide
- `fe-c` - Iron-carbon compounds
- And many more...

For a complete list of built-in materials, run: `optool -c`

All materials (local and built-in) can be used as either core or mantle materials.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 