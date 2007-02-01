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
import urlparse
import urllib
import md5
import tempfile
import subprocess
import shutil


class Recipe:
    """Recipe that downloads a package from the net and unpacks it.

    Configuration options:

        url
        strip-top-level-dir
        md5sum

    """

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name

        buildout['buildout'].setdefault(
            'download-directory', 
            os.path.join(buildout['buildout']['directory'], 'downloads'))

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )

        options['bin-directory'] = buildout['buildout']['bin-directory']
        options.setdefault('strip-top-level-dir', 'true')

        self.filename = urlparse.urlparse(options['url'])[2].split('/')[-1]

    def update(self):
        pass

    def install(self):
        download_dir = self.buildout['buildout']['download-directory']
        if not os.path.isdir(download_dir):
            os.mkdir(download_dir)

        if not os.path.isdir(self.options['location']):
            os.mkdir(self.options['location'])

        # Step 1: Download the package (if not downloaded already) 
        download_filename = os.path.join(download_dir, self.filename)
        if not os.path.exists(download_filename):
            # XXX undefined behavior when file already exists
            # XXX watch out for offline flag
            urllib.urlretrieve(self.options['url'], download_filename)

        # Check MD5 sum
        if compute_md5sum(download_filename) != self.options['md5sum']:
            raise ValueError("Invalid MD5 sum for downloaded file %r" % 
                             self.options['url'])

        # Step 2: Extract the package
        extract_dir = tempfile.mkdtemp()
        is_ext = download_filename.endswith
        if is_ext('.tar.gz') or is_ext('.tgz'):
            call = ['tar', 'xzf', download_filename, '-C', extract_dir]
        elif is_ext('.tar.bz2') or is_ext('.tbz2'):
            call = ['tar', 'xzf', download_filename, '-C', extract_dir]
        elif is_ext('.zip'):
            call = ['unzip', download_filename, '-d', extract_dir]
        else:
            raise ValueError("Unsupported file type: %r" % download_filename)

        retcode = subprocess.call(call)
        if retcode != 0:
            raise Exception("Extraction of file %r failed (tempdir: %r)" %
                            (download_filename, extract_dir))

        # Step 3: Move the desired element into the place of the part
        top_level_contents = os.listdir(extract_dir)
        if self.options['strip-top-level-dir'] == 'true':
            if len(top_level_contents) != 1:
                raise ValueError("Can't strip top level directory because "
                                 "there is more than one element in the "
                                 "archive.")
            base = os.path.join(extract_dir, top_level_contents[0])
        else:
            base = extract_dir

        for filename in os.listdir(base):
            shutil.move(os.path.join(base, filename), os.path.join(self.options['location'], filename))

        shutil.rmtree(extract_dir)
        return [self.options['location']]


def compute_md5sum(filename):
    hash = md5.new('')
    f = file(filename)
    chunk = f.read(2**16)
    while chunk:
        hash.update(chunk)
        chunk = f.read(2**16)
    return hash.hexdigest()
