"""
    Setup file for lumos.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 4.0.1.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
from setuptools import setup

def read_requirements():
    """Parse requirements from requirements.txt."""
    with open("requirements.txt", "r") as file:
        return file.read().splitlines()


if __name__ == "__main__":
    try:

        setup(use_scm_version={"version_scheme": "no-guess-dev"}, install_requires=read_requirements())
    except:  # noqa
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools, "
            "setuptools_scm and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise
