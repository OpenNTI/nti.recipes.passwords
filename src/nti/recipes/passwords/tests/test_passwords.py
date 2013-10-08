#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""


$Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import zc.buildout.buildout
import zc.buildout.testing

import unittest
import os
from .. import Decrypt

class NoDefaultBuildout(zc.buildout.testing.Buildout):
	# The testing buildout doesn't provide a way to
	# ignore local defaults, which makes it system dependent, which
	# is clearly wrong
	def __init__(self):
		zc.buildout.buildout.Buildout.__init__(
            self,
			'',
			[('buildout', 'directory', os.getcwd())],
			user_defaults=False)

class TestDecrypt(unittest.TestCase):

	def test_no_file(self):
		# No verification, just sees if it runs

		buildout = NoDefaultBuildout()
		Decrypt( buildout, 'passwords', {} )

		#buildout.print_options()
