#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""This script creates an apt repository at the named location
"""

import os
import argparse
import gzip

from collections import OrderedDict
from time import strftime
from pydpkg import Dpkg

class Package(object):
    """Represents a .deb package
    """
    def __init__(self, package_path):
        """Initialize instance properties
        """
        self.dpkg = Dpkg(package_path)
        self.headers = dict()
        self.header_keys = OrderedDict(
            [
                ('Package', 'package'),
                ('Version', 'version'),
                ('Architecture', 'architecture'),
                ('Maintainer', 'maintainer'),
                ('Filename', 'filename'),
                ('Size', 'filesize'),
                ('MD5sum', 'md5'),
                ('SHA1', 'sha1'),
                ('SHA256', 'sha256'),
                ('Description', 'description')
            ]
        )
        self.get_package_meta()

    def get_package_meta(self):
        """Reads in the package metadata and incorporates it into
        the class
        """
        for key, value in self.header_keys.items():
            self.headers[key] = self.dpkg.get(value)

    def render_packages_file(self):
        """Dumps out the data that would go in a Packages file
        for an apt repo
        """
        ret = list()

        for key, value in self.header_keys.items():
            ret.append("{0}: {1}".format(key, self.headers[key]))
        ret.append('')
        print("\n".join(ret))
        return "\n".join(ret)

class Repo(object):
    """A class to define the apt repository variables and
    create it
    """
    def __init__(self, **kwargs):
        """Just initialize some instance variables
        """
        self.repo_directory = kwargs.get('repodir', '/var/www/apt')

    def write_package_meta(self):
        """Creates the Packages file in the apt repository directory
        Emulates the functionality of dpkg-scanpackages
        """
        os.chdir(self.repo_directory)
        for entry in os.scandir('.'):
            if entry.name[-4:] == '.deb':
                dpkg = Package(entry.name)
                with open('Packages', 'a') as pkgs:
                    with gzip.open('Packages.gz', 'wb') as gz_pkgs:
                        meta = dpkg.render_packages_file()
                        pkgs.write(meta)
                        gz_pkgs.write(bytearray(meta, 'utf-8'))
                del dpkg

    def write_release_meta(self):
        """Creates the Release file in the repo directory
        """
        time_fmt = '%a, %d %b %Y %H:%M:%S %z'
        architectures = list()
        with os.scandir(self.repo_directory) as entry:
            if entry.name[-4:] == '.deb':
                with open(entry.name, 'r') as deb:
                    for line in deb.readlines():
                        if line.startswith("Arch"):
                            _, arch = line.split(' ')
                            if arch not in architectures:
                                architectures.append(arch)

        with open('Release', 'w') as release:
            release.write("Architectures: {0}\n".format(architectures))
            release.write("Date: {0}\n".format(strftime(time_fmt)))

def main():
    """Start out here
    """
    parser = argparse.ArgumentParser(description='create an apt repository')
    parser.add_argument('repo_path', required=False, help='directory path of the packages')
    parser.add_argument('-d', '--debug', type='store_true', help='print debug output')
    args = parser.parse_args()

    if not args.repo_path:
        apt_repo = Repo()
    else:
        apt_repo = Repo(repo_directory=args.repo_path)
    apt_repo.write_package_meta()
    apt_repo.write_release_meta()

if __name__ == '__main__':
    main()
