import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "mqtt-mysql-bridge",
    version = "0.0.1",
    author = "Michele Pinassi",
    author_email = "o-zone@zerozone.it",
    description = ("A bridge from mqtt to mysql db"),
    license = "MIT License",
    keywords = "mqtt mysql",
    url = "http://www.zerozone.it",
    scripts=['mqtt-bridge.py'],
    packages=['mqtt-bridge'],
    long_description=read('../README.md'),
    install_requires=['argparse','paho-mqtt','MySQL-python'],
    classifiers=[
        "Development Status :: 3 - Alpha",
	"Environment :: Console",
	"Intended Audience :: Information Technology",
	"Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
    ],
)
