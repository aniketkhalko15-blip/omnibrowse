from setuptools import setup, find_packages

setup(
    name="omnibrowse",
    version="0.1.0",
    description="The Universal Autonomous Browser Engine for AI Agents",
    author="OmniBrowse Authors",
    packages=find_packages(),
    install_requires=[
        "playwright>=1.40.0"
    ],
    python_requires=">=3.9",
)
