#!/usr/bin/env python3
"""
Simple Optool Runner for Dust Opacity Generation

This script runs Optool to generate dust opacity files for various 
materials, temperatures, and grain sizes for astrophysical simulations.
"""

import os
import subprocess
import shutil
import argparse
import sys
from pathlib import Path
import re

# Default values
DEFAULT_MATERIAL = "E40R"
DEFAULT_GRAIN_SIZE = 0.3
DEFAULT_TEMPERATURES = [10, 100, 200, 300]
DEFAULT_NK_DIR = "data/nk_files"
DEFAULT_OUTPUT_DIR = "radmc3d_model"

# Material densities (g/cm³)
MATERIAL_DENSITIES = {
    'x035': 2.7,   # (0.65)MgO-(0.35)SiO2
    'x040': 2.7,   # (0.60)MgO-(0.40)SiO2
    'x050A': 2.7,  # (0.50)MgO-(0.50)SiO2 structure A
    'x050B': 2.7,  # (0.50)MgO-(0.50)SiO2 structure B
    'E10': 2.8,    # Mg(0.9)Fe(0.1)SiO3; Fe³⁺
    'E10R': 2.8,   # Mg(0.9)Fe(0.1)SiO3; Fe²⁺
    'E20': 2.9,    # Mg(0.8)Fe(0.2)SiO3; Fe³⁺
    'E20R': 2.9,   # Mg(0.8)Fe(0.2)SiO3; Fe²⁺
    'E30': 3.0,    # Mg(0.7)Fe(0.3)SiO3; Fe³⁺
    'E30R': 3.0,   # Mg(0.7)Fe(0.3)SiO3; Fe²⁺
    'E40': 3.1,    # Mg(0.6)Fe(0.4)SiO3; Fe³⁺
    'E40R': 3.1    # Mg(0.6)Fe(0.4)SiO3; Fe²⁺
}


def check_optool():
    """Check if Optool is available."""
    try:
        result = subprocess.run(["optool", "--version"], 
                               capture_output=True, text=True, check=False)
        if result.returncode == 0 or "optool" in result.stdout.lower() or "optool" in result.stderr.lower():
            return True
        return False
    except FileNotFoundError:
        return False


def find_nk_file(material, temp=None, nk_dir=DEFAULT_NK_DIR):
    """Find the .lnk file for the material and temperature."""
    if not os.path.exists(nk_dir):
        print(f"Error: Directory {nk_dir} not found.")
        return None
    
    # Try temperature-specific file first
    if temp is not None:
        temp_file = os.path.join(nk_dir, f"{material}_{temp}K.lnk")
        if os.path.exists(temp_file):
            return temp_file
    
    # Try exact match without temperature
    exact_file = os.path.join(nk_dir, f"{material}.lnk")
    if os.path.exists(exact_file):
        return exact_file
    
    # Search for partial matches
    for filename in os.listdir(nk_dir):
        if filename.lower().endswith('.lnk') and material.lower() in filename.lower():
            if temp is not None:
                print(f"Warning: Using {filename} which may not match {temp}K exactly.")
            return os.path.join(nk_dir, filename)
    
    return None


def format_mantle_fraction(fraction):
    """Format mantle fraction for filename using exact decimal notation."""
    if fraction is None:
        return ""
    
    # Format as decimal to avoid scientific notation
    return f"{fraction:.10f}".rstrip('0').rstrip('.')


def run_optool(material, grain_size, temp=None, nk_dir=DEFAULT_NK_DIR, output_dir=DEFAULT_OUTPUT_DIR, 
               mantle_material=None, mantle_fraction=None):
    """Run Optool to generate opacity file."""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Find the .lnk file for core material
    nk_file = find_nk_file(material, temp, nk_dir)
    use_builtin_core = False
    if not nk_file:
        # Try as built-in optool material
        use_builtin_core = True
        nk_file = material
        print(f"Using built-in optool material: {material}")
    
    # Find the .lnk file for mantle material if specified
    mantle_nk_file = None
    use_builtin_mantle = False
    if mantle_material and mantle_fraction:
        mantle_nk_file = find_nk_file(mantle_material, temp, nk_dir)
        if not mantle_nk_file:
            # Try as built-in optool material
            use_builtin_mantle = True
            mantle_nk_file = mantle_material
            print(f"Using built-in optool material for mantle: {mantle_material}")
    
    # Create temporary directory for Optool output
    temp_dir = os.path.join(output_dir, "temp_optool")
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Build Optool command
        cmd = [
            "optool",
            nk_file,
            "-radmc",                # RADMC-3D format
            "-a", str(grain_size),   # grain size in microns
            "-o", temp_dir           # output directory
        ]
        
        # Add mantle option if specified
        if mantle_material and mantle_fraction:
            cmd.extend(["-m", mantle_nk_file, str(mantle_fraction)])
        
        print(f"Running Optool for {material}, grain size {grain_size}μm" + 
              (f" at {temp}K" if temp else "") + 
              (f" with {mantle_material} mantle ({mantle_fraction*100:.1f}%)" if mantle_material else "") + "...")
        
        # Run Optool
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Find generated file
        source_file = os.path.join(temp_dir, "dustkappa.inp")
        if not os.path.exists(source_file):
            print(f"Error: Expected output file {source_file} not found.")
            return None
        
        # Create final filename
        base_material = re.sub(r'_\d+K$', '', material)
        mantle_suffix = f"_m{mantle_material}_{format_mantle_fraction(mantle_fraction)}" if mantle_material else ""
        if temp:
            final_name = f"dustkappa_{base_material}{mantle_suffix}_{temp}K_a{grain_size}.inp"
        else:
            final_name = f"dustkappa_{base_material}{mantle_suffix}_a{grain_size}.inp"
        
        # Copy to final location
        final_path = os.path.join(output_dir, final_name)
        shutil.copy2(source_file, final_path)
        
        print(f"Generated: {final_name}")
        return final_path
        
    except subprocess.CalledProcessError as e:
        print(f"Error running Optool: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command error: {e.stderr}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Generate dust opacity files using Optool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Default parameters (material={DEFAULT_MATERIAL}, grain-size={DEFAULT_GRAIN_SIZE})
  python run_optool.py
  
  # Custom material and grain size
  python run_optool.py --material E20R --grain-size 0.5
  
  # Custom temperatures
  python run_optool.py --temperatures 50,150,250
  
  # Single temperature
  python run_optool.py --material E40R --grain-size 0.3 --no-temp-dependent
  
  # With mantle using local materials (20% x035 mantle on E40R core)
  python run_optool.py --material E40R --grain-size 0.3 --mantle-material x035 --mantle-fraction 0.2
  
  # With mantle using built-in optool materials (30% water ice mantle on pyroxene core)
  python run_optool.py --material pyr --grain-size 0.3 --mantle-material h2o --mantle-fraction 0.3
  
  # With mantle for different temperatures
  python run_optool.py --material E40R --mantle-material x035 --mantle-fraction 0.15 --temperatures 100,200,300
        """
    )
    
    parser.add_argument('--material', type=str, default=DEFAULT_MATERIAL,
                       help=f'Dust material for the core (default: {DEFAULT_MATERIAL}). '
                            f'Can use local materials ({", ".join(MATERIAL_DENSITIES.keys())}) '
                            f'or built-in optool materials (run "optool -c" for full list)')
    parser.add_argument('--grain-size', type=float, default=DEFAULT_GRAIN_SIZE,
                       help=f'Grain size in microns (default: {DEFAULT_GRAIN_SIZE})')
    parser.add_argument('--temperatures', type=str, 
                       default=','.join(map(str, DEFAULT_TEMPERATURES)),
                       help=f'Comma-separated temperatures in K (default: {",".join(map(str, DEFAULT_TEMPERATURES))})')
    parser.add_argument('--nk-dir', type=str, default=DEFAULT_NK_DIR,
                       help=f'Directory with .lnk files (default: {DEFAULT_NK_DIR})')
    parser.add_argument('--output-dir', type=str, default=DEFAULT_OUTPUT_DIR,
                       help=f'Output directory (default: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('--no-temp-dependent', action='store_true',
                       help='Generate single file without temperature dependency')
    
    # Mantle options
    parser.add_argument('--mantle-material', type=str, default=None,
                       help='Mantle material (optional). Can use local materials '
                            f'({", ".join(MATERIAL_DENSITIES.keys())}) or built-in optool materials')
    parser.add_argument('--mantle-fraction', type=float, default=None,
                       help='Mantle mass fraction relative to core mass (e.g., 0.2 for 20%% mantle)')
    
    args = parser.parse_args()
    
    # Check if Optool is available
    if not check_optool():
        print("Error: Optool not found. Please install Optool and ensure it's in your PATH.")
        print("See: https://github.com/cdominik/optool")
        return 1
    
    # Validate mantle arguments
    if args.mantle_material and args.mantle_fraction is None:
        print("Error: --mantle-fraction is required when --mantle-material is specified.")
        return 1
    
    if args.mantle_fraction is not None and args.mantle_material is None:
        print("Error: --mantle-material is required when --mantle-fraction is specified.")
        return 1
    
    if args.mantle_fraction is not None and (args.mantle_fraction <= 0 or args.mantle_fraction > 1):
        print("Error: --mantle-fraction must be between 0 and 1 (exclusive of 0).")
        return 1
    
    # Check if materials are known
    if args.material not in MATERIAL_DENSITIES:
        print(f"Note: Material '{args.material}' not found in local database. Will try as built-in optool material.")
        print("Local materials available:", ", ".join(MATERIAL_DENSITIES.keys()))
        print("For full list of optool materials, run: optool -c")
    
    if args.mantle_material and args.mantle_material not in MATERIAL_DENSITIES:
        print(f"Note: Mantle material '{args.mantle_material}' not found in local database. Will try as built-in optool material.")
        print("Local materials available:", ", ".join(MATERIAL_DENSITIES.keys()))
        print("For full list of optool materials, run: optool -c")
    
    # Check if nk directory exists
    if not os.path.exists(args.nk_dir):
        print(f"Error: Directory '{args.nk_dir}' not found.")
        return 1
    
    # Generate opacity files
    if args.no_temp_dependent:
        # Single file without temperature
        result = run_optool(args.material, args.grain_size, 
                          nk_dir=args.nk_dir, output_dir=args.output_dir,
                          mantle_material=args.mantle_material, 
                          mantle_fraction=args.mantle_fraction)
        return 0 if result else 1
    else:
        # Temperature series
        temperatures = [int(t.strip()) for t in args.temperatures.split(',')]
        
        print(f"Generating opacity files for temperatures: {temperatures}")
        if args.mantle_material:
            print(f"Using mantle: {args.mantle_material} ({args.mantle_fraction*100:.1f}% of core mass)")
        
        success_count = 0
        
        for temp in temperatures:
            result = run_optool(args.material, args.grain_size, temp,
                              args.nk_dir, args.output_dir,
                              args.mantle_material, args.mantle_fraction)
            if result:
                success_count += 1
        
        print(f"\nSuccessfully generated {success_count}/{len(temperatures)} files")
        print(f"Output directory: {os.path.abspath(args.output_dir)}")
        
        return 0 if success_count == len(temperatures) else 1


if __name__ == "__main__":
    sys.exit(main()) 