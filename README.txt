===============
gocept.download
===============


zc.buildout recipe to download and extract an archive.


Configuration options
=====================

:url:
    The URL of the archive to download.

:strip-top-level-dir: (optional)
    Whether to remove the top-level directory from the extracted archive
    contents.

:md5sum: (optional)
    MD5 checksum of the archive.

:destination:
    Where to put the extracted archive contents.

:download-directory: (optional)
    Where to put the downloaded archive.


Caching
=======

The download directory, if given, acts as a cache. In addition,
gocept.download takes advantage of zc.buildout's download cache.
