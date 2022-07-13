# Learn more: https://github.com/kennethreitz/setup.py
from setuptools import find_packages
from setuptools import setup


with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="SPC",
    version="0.0.0",
    description="Western Electric SPC rules",
    long_description=readme,
    author="Kyle Patterson",
    url="https://github.com/kylekap/",
    license=license,
    packages=find_packages(exclude=("tests", "docs")),
)
