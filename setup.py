from setuptools import setup, find_packages

setup(
    name="srl",
    version="0.1.0",
    author="Hayes Barber",
    packages=find_packages(),
    install_requires=[
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "srl = srl.main:main",
        ],
    },
)
