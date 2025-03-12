"""Setup script for dd-converter package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dd-converter",
    version="0.1.0",
    author="Your Name",
    author_email="mahmoudmobir@gmail.com",
    description="A tool to convert GAMS DD files to CSV format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mmobir/dd-converter",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "dd-converter=dd_converter.__main__:main",
        ],
    },
) 