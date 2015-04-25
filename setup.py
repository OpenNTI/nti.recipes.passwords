import codecs
from setuptools import setup, find_packages

VERSION = '0.0.0'

entry_points = {
	"zc.buildout" : [
		'default = nti.recipes.passwords:DecryptSection',
		'decryptFile = nti.recipes.passwords:DecryptFile'
	],
}

import platform
py_impl = getattr(platform, 'python_implementation', lambda: None)
IS_PYPY = py_impl() == 'PyPy'

setup(
	name = 'nti.recipes.passwords',
	version = VERSION,
	author = 'Jason Madden',
	author_email = 'open-source@nextthought.com',
	description = "zc.buildout recipes for securely storing passwords in version control",
	long_description = codecs.open('README.rst', encoding='utf-8').read(),
	license = 'Proprietary',
	keywords = 'buildout password',
	classifiers = [
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.3',
		'Topic :: Software Development :: Testing'
		'Framework :: Buildout',
	],
	packages=find_packages('src'),
	package_dir={'': 'src'},
	namespace_packages=['nti', 'nti.recipes'],
	install_requires=[
		'setuptools',
		'zc.buildout',
		'zc.recipe.deployment',
		# NOTE: We use Crypto but CANNOT depend on it, it's too late,
		# it must be installed in the buildout. See __init__.py for details.
		'pycrypto >= 2.6' if not IS_PYPY else ''
	],
	entry_points=entry_points
)
