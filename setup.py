#!/usr/bin/env python3
"""
Setup script for FinWiz - AI Stock Research Tool

This makes finwiz globally accessible as a command-line tool.

Installation:
    pip install -e .

Usage after installation:
    finwiz NVDA
    finwiz -r NVDA MSFT GOOGL
    finwiz -n NVDA
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="finwiz",
    version="1.0.0",
    author="AI Stock Research",
    description="AI Stock Research Command Line Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-stock-research",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "finwiz=finwiz:main_sync",
        ],
    },
    py_modules=["finwiz", "config", "polygon_mcp"],
    include_package_data=True,
    package_data={
        "": ["watchlists/*.json", ".env.example"],
    },
)
