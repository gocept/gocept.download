# Copyright (c) 2008 gocept gmbh & co. kg and Contributors.
# See also LICENSE.txt


import doctest
import unittest
import zc.buildout.testing


flags = (doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop("gocept.download", test)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
        "README.txt",
        setUp=setUp,
        tearDown=zc.buildout.testing.buildoutTearDown,
        package="gocept.download",
        optionflags=flags,
        ),
        ))
