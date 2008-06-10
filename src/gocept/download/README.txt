=========================================================================
gocept.download - A zc.buildout recipe to download and extract an archive
=========================================================================

Downloading a file
==================

The gocept.download recipe downloads a resource from a URL and verifies its
MD5 checksum. If the file isn't an archive of a known type, it is simply
placed in the buildout part's location:

    >>> import os.path
    >>> import md5

    >>> resource = os.path.join(tmpdir("server"), "resource")
    >>> write(resource, "foo")

    >>> write("buildout.cfg", """
    ... [buildout]
    ... parts = download
    ...
    ... [download]
    ... recipe = gocept.download
    ... url = file://%(resource)s
    ... md5sum = %(md5sum)s
    ...
    ... """ % {"resource": resource,
    ...        "md5sum": md5.new("foo").hexdigest()}
    ... )

    >>> print system(buildout),
    Installing download.

    >>> ls("parts", "download")
    -  resource

    >>> cat("parts", "download", "resource")
    foo

We can specify a download directory into which the recipe will place a copy of
the downloaded file. This allows, for example, to create a distribution
including all downloaded files. Either an absolute or a relative file system
path to the download directory may be given; a relative path is considered
relative to the buildout directory:

    >>> write("buildout.cfg", """
    ... [buildout]
    ... parts = download
    ...
    ... [download]
    ... recipe = gocept.download
    ... download-directory = download-directory
    ... url = file://%(resource)s
    ... md5sum = %(md5sum)s
    ...
    ... """ % {"resource": resource,
    ...        "md5sum": md5.new("foo").hexdigest()}
    ... )

    >>> print system(buildout),
    Uninstalling download.
    Installing download.

    >>> ls("download-directory")
    -  resource

    >>> cat("download-directory", "resource")
    foo

The resource will not be downloaded again from the URL once it exists in the
download directory:

    >>> write(resource, "bar")
    >>> remove("parts", "download")

    >>> print system(buildout),
    Uninstalling download.
    Installing download.

    >>> cat("download-directory", "resource")
    foo

    >>> cat("parts", "download", "resource")
    foo


Using the download cache
========================

When downloading a resource from its URL, the recipe tries to take advantage
of buildout's download cache. So far no download cache has been used, so let's
create one:

    >>> download_cache = tmpdir("download-cache")
    >>> ls(download_cache)

The downloaded file will now be placed in the download cache in addition to
the locations seen so far:

    >>> write(resource, "foo")
    >>> remove("parts", "download")
    >>> remove("download-directory", "resource")

    >>> write("buildout.cfg", """
    ... [buildout]
    ... parts = download
    ... download-cache = %(download_cache)s
    ...
    ... [download]
    ... recipe = gocept.download
    ... download-directory = download-directory
    ... url = file://%(resource)s
    ... md5sum = %(md5sum)s
    ...
    ... """ % {"download_cache": download_cache,
    ...        "resource": resource,
    ...        "md5sum": md5.new("foo").hexdigest()}
    ... )

    >>> print system(buildout),
    Uninstalling download.
    Installing download.

    >>> ls(download_cache)
    d  dist

    >>> ls(download_cache, "dist")
    -  resource

    >>> cat(download_cache, "dist", "resource")
    foo

    >>> cat("download-directory", "resource")
    foo

    >>> cat("parts", "download", "resource")
    foo

The same resource will not be downloaded again after it has been placed in the
download cache:

    >>> write(resource, "bar")
    >>> remove("parts", "download")
    >>> remove("download-directory", "resource")

    >>> print system(buildout),
    Uninstalling download.
    Installing download.

    >>> cat(download_cache, "dist", "resource")
    foo

    >>> cat("download-directory", "resource")
    foo

    >>> cat("parts", "download", "resource")
    foo


Extracting an archive
=====================

If the downloaded file is an archive of a type known to gocept.download, it
gets automatically extracted:

    >>> import pkg_resources

    >>> resource = pkg_resources.resource_filename(
    ...     "gocept.download", "sample.tar.gz")
    >>> sample = pkg_resources.resource_string(
    ...     "gocept.download", "sample.tar.gz")

    >>> write("buildout.cfg", """
    ... [buildout]
    ... parts = download
    ...
    ... [download]
    ... recipe = gocept.download
    ... download-directory = download-directory
    ... url = file://%(resource)s
    ... md5sum = %(md5sum)s
    ...
    ... """ % {"resource": resource,
    ...        "md5sum": md5.new(sample).hexdigest()}
    ... )

    >>> print system(buildout),
    Uninstalling download.
    Installing download.

    >>> ls("download-directory")
    -  ...
    -  sample.tar.gz

    >>> ls("parts", "download")
    -  LICENSE.txt

Our example archive contains a top-level directory which was, by default,
stripped away after extracting. We can suppress the stripping:

    >>> write("buildout.cfg", """
    ... [buildout]
    ... parts = download
    ...
    ... [download]
    ... recipe = gocept.download
    ... download-directory = download-directory
    ... url = file://%(resource)s
    ... md5sum = %(md5sum)s
    ... strip-top-level-dir = false
    ...
    ... """ % {"resource": resource,
    ...        "md5sum": md5.new(sample).hexdigest()}
    ... )

    >>> print system(buildout),
    Uninstalling download.
    Installing download.

    >>> ls("parts", "download")
    d  top-level

    >>> ls("parts", "download", "top-level")
    -  LICENSE.txt
