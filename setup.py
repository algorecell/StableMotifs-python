
from setuptools import setup, find_packages

NAME = 'stablemotifs'

setup(name=NAME,
    version="9999",
    author = "Loïc Paulevé",
    author_email = "loic.pauleve@labri.fr",
    url = "https://github.com/algorecell/pyStableMotifs",
    description = "Python interface to StableMotifs",
    install_requires = [
        "colomoto_jupyter",
        "algorecell_types",
        "pandas",
    ],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    keywords="computational systems biology",

    include_package_data = True,
    packages = find_packages(exclude=["examples"]),
    py_modules = ["stablemotifs_setup"]
)

