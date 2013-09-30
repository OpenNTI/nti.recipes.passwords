#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Recipes to decrypt and encrypt passwords.

$Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)
import os

import zc.buildout

from ConfigParser import SafeConfigParser as ConfigParser

class Decrypt(object):

	output_file = ()

	def __init__(self, buildout, name, options ):
		# Allow no file to be able to specify defaults
		# for developers; obviously production must have
		# the real things
		if not options.get('file'):
			return

		input_file = options['file']
		if not input_file.endswith( '.cast5' ):
			raise zc.buildout.UserError("Input is not a .cast5 file")
		output_file = input_file[:-6]

		input_mod_time = os.stat(input_file).st_mtime
		options['input_mod_time'] = repr(input_mod_time)


		self.buildout = buildout
		self.options = options
		self.name = name
		self.input_file = input_file
		self.output_file = output_file



		if not os.path.isfile(output_file) or os.stat(output_file).st_mtime < input_mod_time:
			options['fresh'] = b'true'
			# Hmm...If we don't do this now, sections that depend on
			# us cant interpolate and they fail.
			self._decrypt()
			self._read()
		else:
			options['fresh'] = b'false'
			self._read()


	def _read(self):
		config = ConfigParser()
		config.read( self.output_file )
		for key, value in config.items(self.name):
			self.options[key] = value

	def _decrypt(self):
		os.system( "openssl cast5-cbc -d -in '%s' -out '%s'" % (self.input_file, self.output_file) )

	def install(self):
		return self.output_file

	def update(self):
		pass

class Encrypt(Decrypt):
	pass
