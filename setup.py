#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
    name="ion-AP client",
    version="0.1",
    packages=find_packages(),
    scripts=[
        'ion-ap-client.py',
    ],

    install_requires=[
        'requests'
    ],

    extra_requires=[
    ],

    package_data={
    },

    # metadata for upload to PyPI
    author="Ionite",
    author_email="contact@ionite.net",
    description="This sample script/library for interacting with the ion-AP API",
    license="Propietary",
    keywords="ion-AP invoicing peppol",
    url="https://ionite.net/",  # project home page, if any
    include_package_data=True,
    project_urls={
        "Bug Tracker": "https://ionite.net/",
        "Documentation": "https://ionite.net/",
        "Source Code": "-",
    }

    # could also include long_description, download_url, classifiers, etc.
)
