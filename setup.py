from setuptools import setup, find_packages

setup(
    name='insighta-cli',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'click==8.1.7',
        'requests==2.31.0',
        'rich==13.7.1',
    ],
    entry_points={
        'console_scripts': [
            'insighta=insighta.cli:cli',
        ],
    },
)