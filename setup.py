import os.path

from setuptools import setup, find_packages

setup(
    name="eastern",
    description="Simple Kubernetes Deployment",
    long_description=open(os.path.join(os.path.dirname(__file__), "README.md")).read(),
    long_description_content_type="text/markdown",
    version="5.0.0",
    packages=find_packages(),
    url="https://github.com/wongnai/eastern",
    install_requires=["Click~=6.7", "click-log~=0.3.2", "PyYAML~=6.0", "stevedore~=1.29.0"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-asyncio"],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": ["eastern = eastern.cli:cli"],
        "eastern.command": [
            "load? = eastern.yaml_formatter.overrides:load",
            "load! = eastern.yaml_formatter.overrides:load_strict",
        ],
        "eastern.formatter": ["yaml = eastern.yaml_formatter:Formatter"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: System :: Systems Administration",
    ],
    license="MIT",
)
