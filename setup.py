"""
Setup script for Mirror Watcher CLI - Triune Swarm Engine Testing Suite
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# Read version from __init__.py
def get_version():
    version_file = os.path.join('mirror_watcher', '__init__.py')
    with open(version_file, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('"')[1]
    return '1.0.0'

setup(
    name="mirror-watcher-cli",
    version=get_version(),
    author="Triune Oracle",
    author_email="oracle@triune-swarm.dev",
    description="Comprehensive testing and validation system for Triune Swarm Engine",
    long_description="Mirror Watcher CLI provides comprehensive monitoring, analysis, and validation capabilities for the Triune Swarm Engine system components and workflows.",
    long_description_content_type="text/plain",
    url="https://github.com/Triune-Oracle/triune-swarm-engine",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.20.0",
        "pydantic>=2.0.0",
        "click>=8.0.0",
        "requests>=2.28.0",
        "jsonschema>=4.0.0",
        "pyyaml>=6.0",
        "rich>=13.0.0",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-autodoc-typehints>=1.19.0",
        ],
        "testing": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "httpx>=0.24.0",
            "factory-boy>=3.2.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "mirror-watcher=mirror_watcher.cli:main",
            "mw=mirror_watcher.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mirror_watcher": [
            "data/*.json",
            "schemas/*.json",
            "templates/*.json",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Triune-Oracle/triune-swarm-engine/issues",
        "Source": "https://github.com/Triune-Oracle/triune-swarm-engine",
        "Documentation": "https://github.com/Triune-Oracle/triune-swarm-engine/wiki",
    },
    keywords=[
        "testing",
        "validation", 
        "monitoring",
        "swarm-intelligence",
        "cli",
        "triune-oracle",
        "automation",
        "analysis"
    ],
    zip_safe=False,
)