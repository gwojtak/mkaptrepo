#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""This script creates an apt repository at the named location
"""

import os
import argparse
import gzip
#import gnupg
import hashlib

from collections import OrderedDict
from time import strftime
from pydpkg import Dpkg

HEADER_KEYS = OrderedDict(
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

class Package(object):
    """Represents a .deb package
    """
    def __init__(self, package_path):
        """Initialize instance properties
        """
        self.dpkg = Dpkg(package_path)
        self.headers = dict()
        self.get_package_meta()

    def get_package_meta(self):
        """Reads in the package metadata and incorporates it into
        the class
        """
        for key, value in HEADER_KEYS.items():
            self.headers[key] = self.dpkg.get(value)

    def render_packages_file(self):
        """Dumps out the data that would go in a Packages file
        for an apt repo
        """
        ret = list()

        for key, value in HEADER_KEYS.items():
            ret.append("{0}: {1}".format(key, self.headers[key]))
        ret.append('')

        return "\n".join(ret)

    def __getattribute__(self, name):
        """Make the dpkg header keys case-insensitive
        """
        headers = [x.lower() for x in HEADER_KEYS]
        if name.lower() in headers:
            for key in HEADER_KEYS.keys():
                if key.lower() == name.lower():
                    return self.headers[key]
        else:
            return object.__getattribute__(self, name)

class Repo(object):
    """A class to define the apt repository variables and
    create it
    """
    def __init__(self, repodir):
        """Just initialize some instance variables
        """
        self.repo_directory = repodir

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
        gzpkg_hashes = dict()
        pkg_hashes = dict()

        for entry in os.scandir(self.repo_directory):
            if entry.name[-4:] == '.deb':
                deb = Package(entry.name)
                if deb.architecture not in architectures:
                    architectures.append(deb.architecture)

        with open('Packages', 'r') as pkg:
            pkg_contents = pkg.read()
            pkg.seek(0, 2)
            pkg_filesize = pkg.tell()
        with open('Packages.gz', 'rb') as gzpkg:
            gzpkg_contents = gzpkg.read()
            gzpkg.seek(0, 2)
            gzpkg_filesize = gzpkg.tell()

        pkg_hashes['MD5Sum'] = hashlib.md5(pkg_contents.encode('utf-8')).hexdigest()
        pkg_hashes['SHA1'] = hashlib.sha1(pkg_contents.encode('utf-8')).hexdigest()
        pkg_hashes['SHA256'] = hashlib.sha256(pkg_contents.encode('utf-8')).hexdigest()

        gzpkg_hashes['MD5Sum'] = hashlib.md5(gzpkg_contents).hexdigest()
        gzpkg_hashes['SHA1'] = hashlib.sha1(gzpkg_contents).hexdigest()
        gzpkg_hashes['SHA256'] = hashlib.sha256(gzpkg_contents).hexdigest()

        with open('Release', 'w') as release:
            release.write("Architectures: {0}\n".format(" ".join(architectures)))
            release.write("Date: {0}\n".format(strftime(time_fmt)))
            for method in ['MD5Sum', 'SHA1', 'SHA256']:
                release.write("{0}:\n".format(method))
                release.write(" {0} {1}\n".format(pkg_hashes[method], pkg_filesize))
                release.write(" {0} {1}\n".format(gzpkg_hashes[method], gzpkg_filesize))

def main():
    """Start out here
    """
    parser = argparse.ArgumentParser(description='create an apt repository')
    parser.add_argument(
        'repo_path',
        nargs='?',
        default='.',
        help='directory path of the packages'
    )
    parser.add_argument('-d', '--debug', action='store_true', help='print debug output')
    args = parser.parse_args()

    apt_repo = Repo(repodir=args.repo_path)
    apt_repo.write_package_meta()
    apt_repo.write_release_meta()

if __name__ == '__main__':
    main()
