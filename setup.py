from setuptools import setup, find_packages


name = "gocept.download"

classifiers = [
    "Environment :: Console",
    "Environment :: Plugins",
    "Framework :: Buildout",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Zope Public License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Software Development :: Build Tools",
    "Topic :: System :: Software Distribution",
    ]

setup(
    name = name,
    version = "0.9.4",
    author = "Christian Theune",
    author_email = "ct@gocept.com",
    description = \
    "zc.buildout recipe for downloading and extracting an archive.",
    long_description = open("README.txt").read(),
    license = "ZPL 2.1",
    keywords = "buildout zc.buildout recipe download extract archive",
    classifiers = classifiers,
    url = "http://svn.gocept.com/repos/gocept/" + name,
    download_url = \
    "https://svn.gocept.com/repos/gocept/"
    "%(name)s/trunk#egg=%(name)s-dev" % {"name": name},
    packages = find_packages("src"),
    include_package_data = True,
    package_dir = {"": "src"},
    namespace_packages = ["gocept"],
    install_requires = ["zc.buildout", "setuptools"],
    extras_require = {"test": ["zope.testing"]},
    entry_points = {"zc.buildout": ["default = %s:Recipe" % name,],},
    )
