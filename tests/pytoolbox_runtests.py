#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#**********************************************************************************************************************#
#                                        PYTOOLBOX - TOOLBOX FOR PYTHON SCRIPTS
#
#  Main Developer : David Fischer (david.fischer.ch@gmail.com)
#  Copyright      : Copyright (c) 2012-2015 David Fischer. All rights reserved.
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

import shutil, six, sys, tarfile, tempfile
from os.path import join
from pytoolbox.exception import BadHTTPResponseCodeError
from pytoolbox.network.http import download_ext
from pytoolbox.unittest import runtests

from . import constants


def main():
    print('Download the test assets')
    for url, filename in constants.TEST_ASSETS:
        download_ext(url, filename, force=False)

    print('Download ffmpeg static binary')
    try:
        download_ext(constants.FFMPEG_URL, constants.FFMPEG_ARCHIVE, force=False)
        if six.PY2:
            import contextlib, lzma
            with contextlib.closing(lzma.LZMAFile(constants.FFMPEG_ARCHIVE)) as xz:
                with tarfile.open(fileobj=xz) as f:
                    f.extractall(constants.TESTS_DIRECTORY)
        else:
            with tarfile.open(constants.FFMPEG_ARCHIVE) as f:
                f.extractall(constants.TESTS_DIRECTORY)
        for filename in 'ffmpeg', 'ffprobe':
            shutil.copy(join(constants.FFMPEG_DIRECTORY, filename), tempfile.gettempdir())
    except BadHTTPResponseCodeError:
        print('Unable to download ffmpeg: Will mock ffmpeg if missing')

    print('Run the tests with nose')
    # Ignore django module (how to filter by module ?) + ignore ming module if Python > 2.x
    ignore = ('fields.py|mixins.py|signals.py|storage.py|utils.py|validators.py|widgets.py|pytoolbox_filters.py|'
              'pytoolbox_tags.py' + ('|session.py|schema.py' if sys.version_info[0] > 2 else ''))
    return runtests(__file__, cover_packages=['pytoolbox'], packages=['pytoolbox', 'tests'], ignore=ignore)

if __name__ == '__main__':
    main()
