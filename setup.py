from setuptools import setup, find_packages

setup(
    name='eastern',
    version='2.0',
    packages=find_packages(),
    install_requires=[
        'Click==6.7',
    ],
    entry_points={
        'console_scripts': [
            'eastern = eastern.cli:cli'
        ]
    }
)
