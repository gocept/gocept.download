from setuptools import setup, find_packages

name = "gocept.download"
setup(
    name = name,
    version = "0.9.3",
    author = "Christian Theune",
    author_email = "ct@gocept.com",
    description = "zc.buildout recipe for downloading and extracting an archive.",
    long_description = open('README.txt').read(),
    license = "ZPL 2.1",
    keywords = "zope3 buildout",
    classifiers = ["Framework :: Buildout"],
    url='http://svn.gocept.com/repos/gocept/'+name,
    download_url='https://svn.gocept.com/repos/gocept/gocept.download/trunk#egg=gocept.download-dev',
    zip_safe=False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['gocept'],
    install_requires = ['zc.buildout', 'setuptools'],
    entry_points = {
        'zc.buildout': [
             'default = %s:Recipe' % name,
             ]
        },
    )
