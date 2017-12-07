from setuptools import setup, find_packages

setup(
    name='eastern',
    description='Simple Kubernetes Deployment',
    version='2.0',
    packages=find_packages(),
    url='https://github.com/wongnai/eastern',
    install_requires=[
        'Click==6.7',
        'PyYAML==3.12',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={'console_scripts': ['eastern = eastern.cli:cli']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Systems Administration',
    ])
