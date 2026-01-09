# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="korean-normalizer",
    version="0.1.0",
    description="Korean compound noun splitter and normalizer",
    author="Nathan",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": ["pytest", "pytest-cov"],
    },
    package_data={
        "normalizer": ["resources/lexicon/*.txt"],
    },
)
