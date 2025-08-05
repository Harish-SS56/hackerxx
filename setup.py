#!/usr/bin/env python
"""Setup script for HackRx 6.0 Document QA API."""

from setuptools import setup, find_packages

setup(
    name="hackrx-document-qa-api",
    version="1.0.0",
    description="HackRx 6.0 - Intelligent Document Question-Answering API using Gemini Flash 1.5",
    author="HackRx Team",
    python_requires=">=3.11",
    packages=find_packages(include=["app", "app.*"]),
    install_requires=[
        "fastapi>=0.116.1",
        "google-genai>=1.28.0",
        "pydantic-settings>=2.10.1",
        "pymupdf>=1.26.3",
        "requests>=2.32.4",
        "uvicorn>=0.35.0",
    ],
    entry_points={
        "console_scripts": [
            "hackrx-api=main:main",
        ],
    },
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    include_package_data=True,
)