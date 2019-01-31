from setuptools import setup, find_packages
from setuptools.command.install import install

with open("README.md", "r") as fh:
    long_description = fh.read()

if __name__ == '__main__':
    setup(
        name="TripsIM",
        version="0.0.1",
        author="Yujie Liu, Jason Brar",
        author_email="rbose@cs.rochester.edu",
        description="Python implementation of the TRIPS interpretation manager",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/mrmechko/TripsIM",
        packages=find_packages(exclude=["test", "data"]),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
