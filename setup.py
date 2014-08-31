#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#**********************************************************************************************************************#
#                                        PYTOOLBOX - TOOLBOX FOR PYTHON SCRIPTS
#
#  Main Developer : David Fischer (david.fischer.ch@gmail.com)
#  Copyright      : Copyright (c) 2012-2014 David Fischer. All rights reserved.
#
#**********************************************************************************************************************#
#
# This file is part of David Fischer's pytoolbox Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the EUPL v. 1.1 as provided
# by the European Commission. This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the European Union Public License for more details.
#
# You should have received a copy of the EUPL General Public License along with this project.
# If not, see he EUPL licence v1.1 is available in 22 languages:
#     22-07-2013, <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>
#
# Retrieved from https://github.com/davidfischer-ch/pytoolbox.git

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from codecs import open
from os.path import dirname, join
from setuptools import setup, find_packages
from subprocess import check_output

# https://pypi.python.org/pypi?%3Aaction=list_classifiers

classifiers = """
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
Framework :: Flask
License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)
Natural Language :: English
Operating System :: POSIX :: Linux
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.2
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: PyPy
Topic :: Software Development :: Libraries :: Python Modules
"""

not_yet_tested = """
Operating System :: MacOS :: MacOS X
Operating System :: Unix
"""

keywords = [
    'celery', 'ffmpeg', 'django', 'flask', 'json', 'juju', 'mock', 'mongodb', 'rsync', 'rtp', 'smpte 2022-1', 'screen',
    'subprocess'
]

install_requires = [
    'argparse',
    'mock',
    'passlib',
    'pyaml',
    'pycallgraph',
    'pygal',
    'pymongo',
    'pytz',
    'requests',
    'six',
]

extras_require = {
    'django':    ['django'],
    'flask':     ['flask'],
    'mongo':     ['celery'],
    'smpte2022': ['fastxor'],
}

# Why not installing following packages for python 3 ?
#
# * hashlib, ipaddr: Part of python 3 standard library
# * sudo pip-3.3 install kitchen -> AttributeError: 'module' object has no attribute 'imap'
# * sudo pip-3.3 install ming    -> File "/tmp/pip_build_root/ming/setup.py", line 5, SyntaxError: invalid syntax

PY3 = sys.version_info[0] > 2

if not PY3:
    extras_require['ming'] = ['ming']
    try:
        import hashlib
    except ImportError:
        install_requires.append('hashlib')
    install_requires += [
        'ipaddr',
        'kitchen',
    ]

description = 'Toolbox for Python scripts'

if len(sys.argv) > 1 and sys.argv[1] in ('develop', 'install', 'test'):
    old_args = sys.argv[:]
    sys.argv = [old_args[0]] + [arg for arg in old_args if '--extra' in arg or '--help' in arg]
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter, epilog=description)
    for extra in extras_require.keys():
        parser.add_argument('--extra-{0}'.format(extra), action='store_true',
                            help='Install dependencies for the module/feature {0}.'.format(extra))
    parser.add_argument('--extra-all', action='store_true', help='Install dependencies for all modules/features.')
    args = vars(parser.parse_args())

    for extra, enabled in sorted(args.items()):
        extra = extra.replace('extra_', '')
        if (args['extra_all'] or enabled) and extra in extras_require:
            print('Enable dependencies for feature/module {0}'.format(extra))
            install_requires += extras_require[extra]
    sys.argv = [arg for arg in old_args if not '--extra' in arg]

    if sys.argv[1] == 'test':
        print('Download the test media assets')
        from pytoolbox.network.http import download_ext
        download_ext('http://techslides.com/demos/sample-videos/small.mp4', join(dirname(__file__), 'small.mp4'),
                     force=False)

setup(name='pytoolbox',
      version='9.4.2',
      packages=find_packages(),
      description=description,
      long_description=open('README.rst', 'r', encoding='utf-8').read(),
      author='David Fischer',
      author_email='david.fischer.ch@gmail.com',
      url='https://github.com/davidfischer-ch/pytoolbox',
      license='EUPL 1.1',
      classifiers=filter(None, classifiers.split('\n')),
      keywords=keywords,
      extras_require=extras_require,
      install_requires=install_requires,
      tests_require=['coverage', 'mock', 'nose', 'nose-exclude'],
      # Thanks to https://github.com/graingert/django-browserid/commit/46c763f11f76b2f3ba365b164196794a37494f44
      test_suite='nose.collector',
      use_2to3=PY3,
      use_2to3_exclude_fixers=['lib2to3.fixes.fix_import'])
