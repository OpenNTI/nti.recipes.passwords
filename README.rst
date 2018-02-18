=======================
 nti.recipes.passwords
=======================

.. image:: https://travis-ci.org/NextThought/nti.recipes.passwords.svg?branch=master
    :target: https://travis-ci.org/NextThought/nti.recipes.passwords

.. image:: https://coveralls.io/repos/github/NextThought/nti.recipes.passwords/badge.svg?branch=master
    :target: https://coveralls.io/github/NextThought/nti.recipes.passwords?branch=master

This is a ``zc.buildout`` recipe for `securely storing encrypted files
in version control
<https://johnresig.com/blog/keeping-passwords-in-source-control/>`_,
but decrypting them when buildout is run. The output can either be a
decrypted file on disk, or a set of values in a buildout part for use
by other parts.

Lets look at an example using a buildout part. Decrypted values are
commonly used by other parts. Here, we're setting environment
variables in the entry point scripts buildout generates::

  [passwords]
  recipe = nti.recipes.passwords
  file = prod_passwords.pass.cast5

  # Declare the variables in the password file
  # for convenience
  aws_secret_access_key =

  [boto]
  aws_access_key_id = MYAWSACCESSKEY

  [eggs]
  eggs = my.eggs
         boto

  # Let scripts know how they should contact
  # It's important to only put the Boto keys in the environment
  # if they are defined, as they take highest precedence
  initialization +=
      if "${boto:aws_access_key_id}": os.environ['AWS_ACCESS_KEY_ID'] = "${boto:aws_access_key_id}"
      if "${passwords:aws_secret_access_key}": os.environ['AWS_SECRET_ACCESS_KEY'] = "${passwords:aws_secret_access_key}"


They can also be used in templates for new files::

  [backup-scripts]
  recipe = z3c.recipe.filetemplate
  source-directory = templates
  dest-directory = ${buildout:root-directory}
  files = ascript

Where ``templates/ascript.in`` might look like this::

  #!${deployment:bin-directory}/python

  import subprocess
  cmd = [
      '${deployment:bin-directory}/s3put',
      '--access_key', '${boto:aws_access_key_id}',
      '--secret_key', '${passwords:aws_secret_access_key}',
      ...
  ]

  subprocess.check_call(cmd)

Creating The Encrypted Data
===========================

The encrypted file is a standard ConfigParser (``ini``) file.
Continuing our example, it might look something like this::

  [passwords]
  aws_secret_access_key = MYSECRETKEY

Note that the name of the section in the ini file matches the name of
the section in the buildout configuration. You can have multiple
sections in one ini file, each corresponding to a different section in
the buildout configuration.

You'll encrypt the file using openssl::

  openssl cast5-cbc -e -in prod_passwords.pass -out prod_passwords.pass.cast5

The file ``prod_passwords.pass.cast5`` is then checked into version
control and distributed securely with the buildout configuration. (The
file ``prod_passwords.pass`` is **not** checked into version control.)

The ``.cast5`` extension is mandatory.

Decrypting The Encrypted Data
=============================

The first time buildout is run, or when the encrypted data's
modification time or checksum changes, you will be interactively
prompted to enter the password to decrypt the file. This means that
for that first run, buildout must be run in the foreground with TTY
access.

Decrypting Files
================

To produce a decrypted file on disk, rather than a set of values in a
buildout part, use the ``nti.recipes.passwords:decryptFile`` recipe.
It functions the same as the default recipe, with the addition of a
``output-file`` setting. The input data can be in any file format::

  [file]
  recipe = nti.recipes.passwords:decryptFile
  file = sensitivedata.bin.cast5
  output-file = ${deployment:etc-directory}/sensitivedata.bin
