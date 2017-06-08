import codecs
from setuptools import setup, find_packages

VERSION = '0.0.0'

entry_points = {
    "zc.buildout": [
        'default = nti.recipes.passwords:DecryptSection',
        'decryptFile = nti.recipes.passwords:DecryptFile'
    ],
}

TESTS_REQUIRE = [
    'nti.testing',
    'zope.testrunner',
]

import platform
py_impl = getattr(platform, 'python_implementation', lambda: None)
IS_PYPY = py_impl() == 'PyPy'


def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()


setup(
    name='nti.recipes.passwords',
    version=_read('version.txt').strip(),
    author='Jason Madden',
    author_email='open-source@nextthought.com',
    description="zc.buildout recipes for securely storing passwords in version control",
    long_description=(_read('README.rst') + '\n\n' + _read("CHANGES.rst")),
    license='Apache',
    keywords='buildout password',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Framework :: Buildout',
    ],
    zip_safe=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['nti', 'nti.recipes'],
    tests_require=TESTS_REQUIRE,
    install_requires=[
        'setuptools',
        'six',
        'zc.buildout',
        'zc.recipe.deployment',
        # NOTE: We use Crypto but CANNOT depend on it, it's too late,
        # it must be installed in the buildout. See __init__.py for
        # details.
        'pycrypto >= 2.6' if not IS_PYPY else ''
    ],
    extras_require={
        'test': TESTS_REQUIRE,
    },
    entry_points=entry_points,
    test_suite="nti.recipes.passwords.tests",
)
