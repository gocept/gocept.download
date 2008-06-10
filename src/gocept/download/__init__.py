##############################################################################
#
# Copyright (c) 2007 gocept gmbh & co. kg and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os
import os.path
import urlparse
import urllib
import md5
import tempfile
import subprocess
import shutil

import zc.buildout.easy_install


class Recipe:
    """Recipe that downloads a package from the net and unpacks it.

    Configuration options:

        url
        strip-top-level-dir
        md5sum
        destination
        download-directory

    """

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name

        options.setdefault('download-directory',
                           buildout['buildout'].get('download-directory', ''))

        if not options.get('destination'):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'],
                self.name,
                )

        options['bin-directory'] = buildout['buildout']['bin-directory']
        options.setdefault('strip-top-level-dir', 'true')

        self.filename = urlparse.urlparse(options['url'])[2].split('/')[-1]

        self.remove_after_install = []

    def update(self):
        pass

    def install(self):
        destination = self.options.get('destination')
        # Fail if a destination is given and is not an empty directory.
        # Consider both None (destination option was not given) and ''
        # (destination option was given, but with an empty value) for the
        # destination to not be given.
        if (destination and
            os.path.exists(destination) and
            (not os.path.isdir(destination) or os.listdir(destination))
            ):
            raise ValueError(
                "Destination %s must be an empty directory." % destination)

        # Step 1: Download the package (if not downloaded already)
        download_filename = self.download()

        # Check MD5 sum
        if compute_md5sum(download_filename) != self.options['md5sum']:
            raise ValueError("Invalid MD5 sum for downloaded file %r" %
                             self.options['url'])

        # Step 2: Extract the package if the file is an archive
        extract_dir = tempfile.mkdtemp("buildout-" + self.name)
        self.remove_after_install.append(extract_dir)
        is_ext = download_filename.endswith
        is_archive = True
        if is_ext('.tar.gz') or is_ext('.tgz'):
            call = ['tar', 'xzf', download_filename, '-C', extract_dir]
        elif is_ext('.tar.bz2') or is_ext('.tbz2'):
            call = ['tar', 'xjf', download_filename, '-C', extract_dir]
        elif is_ext('.zip'):
            call = ['unzip', download_filename, '-d', extract_dir]
        else:
            is_archive = False

        if is_archive:
            retcode = subprocess.call(call)
            if retcode != 0:
                raise Exception("Extraction of file %r failed (tempdir: %r)" %
                                (download_filename, extract_dir))
        else:
            shutil.copy(download_filename, extract_dir)

        # Step 3: Move the desired element into the place of the part
        if is_archive and self.options['strip-top-level-dir'] == 'true':
            top_level_contents = os.listdir(extract_dir)
            if len(top_level_contents) != 1:
                raise ValueError("Can't strip top level directory because "
                                 "there is more than one element in the "
                                 "archive.")
            base = os.path.join(extract_dir, top_level_contents[0])
        else:
            base = extract_dir

        if destination is None:
            # We fail if the location already exists, typically this means it
            # is a broken installation.
            destination = self.options['location']
            os.mkdir(destination)
            part_directories = [destination]
        else:
            part_directories = []

        for filename in os.listdir(base):
            shutil.move(os.path.join(base, filename),
                        os.path.join(destination, filename))

        for path in self.remove_after_install:
            shutil.rmtree(path)
        return part_directories

    def download(self):
        # XXX undefined behavior when file already exists
        # XXX watch out for offline flag

        # If a download directory is given, the file will ultimately be placed
        # in it. If the file already exists there, we are finished.
        filename = None
        download_dir = self.options.get('download-directory')
        if download_dir:
            download_dir = os.path.join(
                self.buildout['buildout']['directory'], download_dir)
            if not os.path.isdir(download_dir):
                os.mkdir(download_dir)
            filename = os.path.join(download_dir, self.filename)
            if os.path.exists(filename):
                return filename

        # If a download cache is being used, we either take the file from it
        # (copying to the download directory first if there is one) or
        # remember to place a copy in the cache later.
        cache_filename = None
        cache_dir = zc.buildout.easy_install.download_cache()
        if cache_dir:
            cache_filename = os.path.join(cache_dir, self.filename)
            if os.path.exists(cache_filename):
                if filename:
                    shutil.copy(cache_filename, filename)
                return cache_filename

        # We really need to download the resource. For simplicity and to avoid
        # partial downloads littering the cache, we download it to a temporary
        # file, copy it to the download directory and the download cache as
        # needed and always return the temporary file to the installer.
        temp_dir = tempfile.mkdtemp()
        self.remove_after_install.append(temp_dir)

        download_filename = os.path.join(temp_dir, self.filename)
        urllib.urlretrieve(self.options['url'], download_filename)

        if filename:
            shutil.copy(download_filename, filename)
        if cache_filename:
            shutil.copy(download_filename, cache_filename)
        return download_filename


def compute_md5sum(filename):
    hash = md5.new('')
    f = file(filename)
    chunk = f.read(2**16)
    while chunk:
        hash.update(chunk)
        chunk = f.read(2**16)
    return hash.hexdigest()
