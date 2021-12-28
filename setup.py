from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setup(
    name="pyfood",
    version="0.0.5",
    author="Michel Deudon",
    author_email="michel@local-seasonal.org",
    license="Creative Commons Attribution 4.0 International License.",
    maintainer="Local Seasonal",
    description="Pyfood: A Python package to process food",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "scikit-learn>=0.20.1",
        "Unidecode>=1.1.0",
    ],
    python_requires=">=3.6",
)
