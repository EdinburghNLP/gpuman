from setuptools import setup

setup(
    name="gpuman",
    version="0.1",
    packages=["gpuman"],
    install_requires=['nvidia-ml-py3', "fire", "pyYAML"],
    entry_points = {
        "console_scripts": [
            "gpuman = gpuman.cmd:main",
        ]
    },
)
