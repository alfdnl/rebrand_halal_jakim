from setuptools import setup, find_packages

setup(
    name="halal-jakim",
    version="1.0",
    author="alfdnl080",
    description="Rebranding Halal Jakim Website",
    long_description="Improve Halal Jakim website to become more user friendly",
    url="https://github.com/alfdnl/rebrand_halal_jakim",
    keywords="scrap, data engineer, etl, dashboard",
    python_requires=">=3.8, <4",
    packages=find_packages(include=["rebrand_halal_jakim", "rebrand_halal_jakim.*"]),
)
