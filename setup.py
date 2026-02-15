#!/usr/bin/env python3
"""
Setup script for XCoder - Intelligent Coding Assistant
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "XCoder - Intelligent Coding Assistant with interactive CLI"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="xcoder",
    version="1.0.0",
    author="XCoder Team",
    # author_email will be added when published
    description="Intelligent Coding Assistant with interactive CLI",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    # url will be added when repository is published

    # Package discovery
    packages=find_packages(),

    # Include all Python files
    package_data={
        '': ['*.py', '*.yaml', '*.yml', '*.json', '*.txt'],
    },
    include_package_data=True,

    # Python version requirement
    python_requires=">=3.8",

    # Dependencies
    install_requires=read_requirements(),

    # Console scripts entry points
    entry_points={
        'console_scripts': [
            'xcoder=cli.xcoder_cli:main',
        ],
    },

    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Text Processing :: Linguistic",
    ],

    # Keywords
    keywords="coding assistant ai cli interactive ollama langchain",

    # Project URLs will be added when repository is published
    # project_urls={
    #     "Bug Reports": "",
    #     "Source": "",
    # },
)