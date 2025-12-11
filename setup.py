from setuptools import setup, find_packages

setup(
    name="srl",
    author="Hayes Barber",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "srl = srl.main:main",
        ],
    },
)
