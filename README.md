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

- `--material`: Dust material composition (default: E40R)
  - Available materials: x035, x040, x050A, x050B, E10, E10R, E20, E20R, E30, E30R, E40, E40R
- `--grain-size`: Grain size in microns (default: 0.3)
- `--temperatures`: Comma-separated temperatures in K (default: 10,100,200,300)
- `--output-dir`: Directory to save output files (default: radmc3d_model)
- `--nk-dir`: Directory containing .lnk files (default: data/nk_files)

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

## Output

The script generates files named: `dustkapscatmat_{material}_{temperature}K_a{size}.inp`

For example: `dustkapscatmat_E40R_100K_a0.3.inp`

## Available Dust Materials

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 