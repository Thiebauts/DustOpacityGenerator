# Dust Opacity Generator

A Python tool for generating dust opacity files for astrophysical simulations using Optool. This tool is designed to help astronomers and researchers generate dust opacity files for various materials, temperatures, and grain sizes, which can be used with radiative transfer codes like RADMC-3D.

## Features

- Generate dust opacity files for various materials and temperatures
- Support for multiple grain sizes
- Temperature-dependent opacity calculations
- Compatible with RADMC-3D input format
- Easy-to-use command line interface

## Installation

1. First, ensure you have [Optool](https://github.com/cdominik/optool) installed and accessible in your PATH.

2. Clone this repository:
```bash
git clone https://github.com/yourusername/DustOpacityGenerator.git
cd DustOpacityGenerator
```

3. Install the package:
```bash
pip install -e .
```

## Quick Start

Generate dust properties for the default 4 temperatures (10K, 100K, 200K, 300K):

```bash
generate_dust_opacity --material E40R --grain-size 0.3 --output-dir dust_files
```

## Command Line Options

- `--material`: Dust material composition (default: E40R)
  - Available materials: x035, x040, x050A, x050B, E10, E10R, E20, E20R, E30, E30R, E40, E40R
- `--grain-size`: Grain size in microns (default: 0.3)
- `--temperatures`: Comma-separated temperatures in K (default: 10,100,200,300)
- `--output-dir`: Directory to save output files (default: radmc3d_model)
- `--nk-dir`: Directory containing .lnk files (default: nk_optool)

## Examples

Generate files for different material:
```bash
generate_dust_opacity --material E20R --grain-size 0.5 --output-dir my_dust_files
```

Generate for custom temperatures:
```bash
generate_dust_opacity --material E40R --grain-size 0.3 --temperatures 50,150,250,350
```

Generate single temperature file:
```bash
generate_dust_opacity --material E40R --grain-size 0.3 --no-temp-dependent
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