# Copyright (c) 2020, DCSO GmbH

import os
import fileinput
from distutils.command.sdist import sdist, dir_util
from distutils.errors import DistutilsFileError
from distutils import log

from setuptools import setup
from packaging.version import Version

from lib._version import __version__

VERSION = Version(__version__)
# SPLUNKAPP_BASE_DIR is the folder name in which the App or AddOn is made available
SPLUNKAPP_BASE_DIR = "DCSO_TIE_AddOn" + str(VERSION.major)
# SPLUNKAPP_DISTNAME is the filename of the distribution
SPLUNKAPP_DISTNAME = "DCSO_TIE_Splunk_AddOn" + str(VERSION.major)

class SplunkDist(sdist):
    description = "create a Splunk distribution"
    splunkapp_base_dir = SPLUNKAPP_BASE_DIR

    def __init__(self, dist):
        super().__init__(dist)

    def _write_version(self, base_name):
        # default/app.conf
        app_conf = 'default/app.conf'
        if app_conf not in self.filelist.files:
            raise DistutilsFileError("file {} not in distribution file list".format(app_conf))

        p = os.path.join(base_name, app_conf)
        with fileinput.input(p, inplace=True, backup=False) as f:
            for line in f:
                # remove ending whitespace; print adds newline
                line = line.rstrip()
                if line.startswith('version'):
                    print("version = {}".format(__version__))
                else:
                    print(line)

        log.info("wrote version to {}".format(app_conf))

    def make_distribution(self):
        """make_distribution is verbatim copy of distutils.command.sdist.sdist
        except for the base_dir being well defined, not having the version
        number.
        """
        base_dir = self.splunkapp_base_dir
        base_name = os.path.join(self.dist_dir, base_dir)

        self.make_release_tree(base_dir, self.filelist.files)
        self._write_version(base_dir)

        archive_files = []  # remember names of files we create
        # tar archive must be created last to avoid overwrite and remove
        if 'tar' in self.formats:
            self.formats.append(self.formats.pop(self.formats.index('tar')))

        for fmt in self.formats:
            file = self.make_archive(base_name, fmt, base_dir=base_dir,
                                     owner=self.owner, group=self.group)

            new_file = file.replace(SPLUNKAPP_BASE_DIR, SPLUNKAPP_DISTNAME + '-' + __version__)
            os.rename(file, new_file)
            log.info("renamed distribution file as {}".format(new_file))

            archive_files.append(new_file)
            self.distribution.dist_files.append(('sdist', '', new_file))

        self.archive_files = archive_files

        if not self.keep_temp:
            dir_util.remove_tree(base_dir, dry_run=self.dry_run)


setup(name='dcso_tie_splunk_ta',
      version=__version__,
      description="DCSO Threat Intelligence Engine (TIE) Technical Add-on for Splunk 8.0",
      author='DCSO GmbH',
      author_email='ti-support@dcso.de',
      url="https://tie.dcso.de",
      package_dir={'': 'lib'},
      cmdclass={
          'splunkdist': SplunkDist,
      }
      )
