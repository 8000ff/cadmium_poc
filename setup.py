from setuptools import setup

setup(
    name='cadmium',
    version='0.0.1',
    description='Design cut paths',
    author='Excale',
    packages=['cadmium'],
    install_requires=[
        'numpy',
        'sdf',
        'pygcode',
    ],
    license='GNU',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)