#!/usr/bin/env python3
"""
Setup script for WizFlow - AI-Powered Automation CLI Tool
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text().splitlines()

setup(
    name="wizflow",
    version="1.0.0",
    author="MiniMax Agent",
    description="AI-powered automation workflow generator CLI tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "wizflow=wizflow.cli:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: System Shells",
        "Topic :: Utilities",
    ],
    keywords="automation workflow cli ai llm gpt claude",
    project_urls={
        "Source": "https://github.com/minimax/wizflow",
        "Documentation": "https://github.com/minimax/wizflow/blob/main/README.md",
    },
)
