from setuptools import (
    find_packages,
    setup
)

INSTALL_REQUIRES = (
    'requests',
    'cached_property',
    'requests-ip-rotator'
)

setup(
    name='eircode',
    version='0.0.40',
    python_requires='>=3.5',
    author='Robert Lucey',
    url='https://github.com/RobertLucey/eircode',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=INSTALL_REQUIRES
)
