from setuptools import setup, find_packages

setup(
    name="dust_opacity_generator",
    version="1.0.0",
    description="A tool to generate dust opacity files for astrophysical simulations using Optool",
    author="Matthias",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "generate_dust_opacity=dust_opacity_generator.run_optool:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
) 