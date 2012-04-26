#!/usr/bin/env python

"""
An alternative to the pastee.py script that is distributed
at https://pastee.org/pastee.py

It uses requests.

GPL3 Licenced, etc.
"""

import os
import re
import sys

try:
	import requests
except ImportError:
	sys.exit("This script requires requests to run.")

class Paste(object):
	def __init__(self, **kwargs):
		self._ssl = kwargs.get('ssl', False)
		self._url = "https://pastee.org" if self._ssl else "http://pastee.org"
		self._posturl = self._url+"/submit"
		self._content = kwargs.get("content", None)
		if not self._content or len(self._content) == self._content.count('\n'):
			sys.exit("no files to upload and nothing or just newlines on stdin, go away:)")
		self._lexer = kwargs.get("lexer", "text")
		self._key = kwargs.get("key", None)
		self._ttl = int(kwargs.get("ttl") * 86400)
		
		self._headers = {"Content-type": "application/x-www-form-urlencoded"
			,"Accept": "text/plain"}
		self._params = {"lexer": self._lexer
			,"content": self._content
			,"ttl": self._ttl}
		
		if self._key:
			self._params["encrypt"] = "checked"
			self._params["key"] = self._key

	def makePaste(self):
		try:
			request = requests.post(self._posturl
				,headers=self._headers
				,data=self._params)
			if request.status_code != 200:
				request.raise_for_status()

		except requests.ConnectionError, e:
			return "Failed to make a connection to {0}:\n{1}".format(self._url, repr(e))
		except requests.HTTPError, e:
			return "Failed to make a request to {0}:\n{1}".format(self._url, repr(e))
		pasteID = re.findall("<h1>paste id <code>(\w{5})</code>(?:.*)</h1>", request.content)[0]
		return self._url+"/{0}".format(pasteID)

if __name__ == "__main__":
	from optparse import OptionParser
	parser = OptionParser()

	parser.add_option("-l", "--lexer", action="store",
		type="string", dest="lexer", metavar="LEXERNAME",
		help=("Force use of a particular lexer (ie: c, py). "
			"This defaults to the extention of the supplied "
			"filenames, or 'text' if pasting from stdin."))

	parser.add_option("-t", "--ttl", action="store",
		type="float", default=30, dest="ttl", metavar="DAYS",
		help=("Number of days before the paste will expire."))

	parser.add_option("-k", "--key", action="store",
		type="string", dest="key", metavar="PASSPHRASE",
		help=("Encrypt pastes with this key."))

	parser.add_option("-s", "--ssl", action="store_true",
		dest="ssl", metavar="SSL",
		help=("Use ssl when posting?"))

	opts, files = parser.parse_args()

	if len(files) >= 1:
		for _file in files:
			try:
				with open(_file, "r") as d:
					data = d.read()
			except IOError, e:
				print("Error reading file {0}".format(_file))
				continue
			if _file.find("."):
				l = _file.split(".")[-1]
			else:
				l = None

			Client = Paste(
				ssl = opts.ssl
				,lexer = l or opts.lexer
				,ttl = opts.ttl
				,key = opts.key
				,content = data)
			print(Client.makePaste())
	else:
		Client = Paste(
			ssl = opts.ssl
			,lexer = opts.lexer
			,ttl = opts.ttl
			,key = opts.key
			,content = sys.stdin.read())
		print(Client.makePaste())
