# -*- coding: utf-8 -*-
"""Setup for spirit.releaser package."""

from setuptools import find_packages
from setuptools import setup

version = '0.2'
description = 'Plugins for release automation with zest.releaser.'
long_description = ('\n'.join([
    open('README.rst').read(),
    open('CHANGES.rst').read(),
]))

install_requires = [
    'setuptools',
    # -*- Extra requirements: -*-
    'zest.releaser[recommended]',
]

setup(
    name='spirit.releaser',
    version=version,
    description=description,
    long_description=long_description,
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
    ],
    keywords=[
        'diazo',
        'packaging,'
        'releasing',
    ],
    author='it-spirit',
    author_email='info@it-spir.it',
    url='https://github.com/it-spirit/spirit.releaser',
    download_url='http://pypi.python.org/pypi/spirit.releaser',
    license='BSD',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['spirit'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'test': [
            'mock',
            'nose',
            'nose-selecttests',
            'unittest2',
        ]
    },
    entry_points={
        'console_scripts': [
            'release_diazo = spirit.releaser.diazo:main',
        ],
        'zest.releaser.releaser.after': [
            'release_diazo=spirit.releaser.diazo:release_diazo',
        ],
    },
)
