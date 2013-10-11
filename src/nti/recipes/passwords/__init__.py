#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Recipes to decrypt and encrypt passwords and related data.

File Format
===========

We are duplicating the OpenSSL file format, which is reverse engineered to be
the following::

  'Salted__' + ........ + ciphertext

where ``........`` is the 8 byte salt. The 16-byte key and 8 byte IV are
derived from the passphrase combined with the salt (the IV is not stored
in the file)::

  Key = MD5( passphrase + salt )
  IV  = MD5( key + passphrase + salt )[:8]

That is, the key is the MD5 checksum of concatenating the passphrase
followed by the salt, and the initial vector is the first 8 bytes of the
MD5 of the key, passphrase and salt concatenated.

$Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)
import os

import zc.buildout

from ConfigParser import SafeConfigParser as ConfigParser

from Crypto.Cipher import CAST
from Crypto import Random
from cStringIO import StringIO
import getpass
from hashlib import md5

class _BaseFormat(object):

	#: Eight bytes of random salt data
	salt = None

	def new_salt(self):
		return Random.new().read(CAST.block_size)

	def make_key( self, passphrase ):
		if isinstance(passphrase,unicode):
			passphrase = passphrase.encode("utf-8")
		return md5( passphrase + self.salt ).digest()

	def make_iv( self, passphrase ):
		key = self.make_key( passphrase )
		if isinstance(passphrase,unicode):
			passphrase = passphrase.encode('utf-8')
		return md5( key + passphrase + self.salt ).digest()[:8]

	def _make_cipher( self, passphrase ):
		key = self.make_key( passphrase )
		iv = self.make_iv( passphrase )
		cipher = CAST.new( key, CAST.MODE_CBC, iv )
		return cipher

	def make_ciphertext( self, passphrase, plaintext ):
		if isinstance(plaintext, unicode):
			plaintext = plaintext.encode('utf-8')

		return self._make_cipher( passphrase ).encrypt( plaintext )

	def get_plaintext( self, passphrase, ciphertext ):
		return self._make_cipher( passphrase ).decrypt( ciphertext )

def _read(name, mode):
	# For ease of mocking
	with open(name, mode) as f:
		return f.read()

class _EncryptedFile(_BaseFormat):

	def __init__( self, name ):
		self.name = name
		self._data = _read(name, 'rb')

		if not self._data.startswith( b'Salted__' ):
			raise zc.buildout.UserError("Improper input file format")

	@property
	def checksum(self):
		# In a format just like the md5sum command line
		# program. Must be bytes
		csum = md5(self._data).hexdigest()
		basename = os.path.basename( self.name )
		return csum + b'  ' + basename + b'\n'

	@property
	def salt(self):
		return self._data[8:16]

	@property
	def ciphertext(self):
		return self._data[16:]



class _BaseDecrypt(object):

	needs_write = False
	plaintext = None

	def __init__(self, buildout, name, options ):
		# Allow no file to be able to specify defaults
		# for developers; obviously production must have
		# the real things
		if not options.get('file'):
			return

		input_file = options['file']
		if not input_file.endswith( '.cast5' ):
			raise zc.buildout.UserError("Input is not a .cast5 file")
		input_file = os.path.abspath( input_file )
		if not os.path.isfile( input_file ):
			raise zc.buildout.UserError("Input file '%s' does not exist" % input_file)

		try:
			stat = os.stat(input_file)
		except OSError: # For testing
			mtime = 0
		else:
			mtime = stat.st_mtime
		options[b'_input_mod_time'] = repr(mtime)

		self._encrypted_file = _EncryptedFile( input_file )
		options[b'_checksum'] = self._encrypted_file.checksum

		self.part_dir = os.path.join( buildout['buildout']['parts-directory'], name )

		self.checksum_file = os.path.join( self.part_dir, 'checksum' )
		self.plaintext_file = os.path.join( self.part_dir, 'plaintext' )

		old_checksum = None
		self.plaintext = None
		if os.path.exists( self.checksum_file ):
			old_checksum = open(self.checksum_file, 'rb' ).read()

		if (old_checksum != self._encrypted_file.checksum \
			or not os.path.exists( self.plaintext_file ) ):
			passphrase = getpass.getpass( 'Password for ' + name + ': ' )

			self.plaintext = self._encrypted_file.get_plaintext( passphrase,
																 self._encrypted_file.ciphertext )
			# XXX FIXME: WTF?
			if self.plaintext.endswith( b'\x01' ):
				self.plaintext = self.plaintext[:-1]

			self.needs_write = True

		if self.plaintext is None:
			with open(self.plaintext_file, 'rb') as f:
				self.plaintext = f.read()


	def _do_write(self):
		if not os.path.isdir( self.part_dir ):
			os.mkdir( self.part_dir, 0700 )

		if self.needs_write:
			with open(self.plaintext_file, 'wb') as f:
				f.write( self.plaintext )

			with open(self.checksum_file, 'wb') as f:
				f.write( self._encrypted_file.checksum )

		return self.checksum_file, self.plaintext_file


	def install(self):
		return self._do_write()

	update = install

class DecryptSection(_BaseDecrypt):

	def __init__( self, buildout, name, options ):
		super(DecryptSection,self).__init__( buildout, name, options )
		if self.plaintext:
			config = ConfigParser()
			config.readfp( StringIO( self.plaintext ) )
			for key, value in config.items(name):
				options[key] = value



class DecryptFile(_BaseDecrypt):

	def __init__( self, buildout, name, options ):
		self.output_file = options['output-file'] # validate before we decrypt
		super(DecryptFile,self).__init__( buildout, name, options )


	def _do_write(self):
		base_files = super(DecryptFile,self)._do_write()
		if self.needs_write:
			with open( self.output_file, 'wb') as f:
				f.write( self.plaintext )
		return base_files + (self.output_file,)
