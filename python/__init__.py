# Copyright (c) 2015-2019 Vector 35 Inc
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.


from __future__ import absolute_import
import atexit
import sys
import ctypes
from time import gmtime


# 2-3 compatibility
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY34 = sys.version_info[0:2] >= (3, 4)

try:
	import builtins  # __builtins__ for python2
except ImportError:
	pass

def range(*args):
	""" A Python2 and Python3 Compatible Range Generator """
	try:
		return xrange(*args)
	except NameError:
		return builtins.range(*args)

def valid_import(mod_name):
	if PY2:
		import imp
		try:
			imp.find_module(mod_name)
			found = True
		except ImportError:
			found = False
	elif PY34:
		import importlib.util
		mod_spec = importlib.util.find_spec(mod_name)
		found = mod_spec is not None
	elif PY3:
		import importlib
		mod_loader = importlib.find_loader(mod_name)
		found = mod_loader is not None
	else:
		return False
	return found


def with_metaclass(meta, *bases):
	"""Create a base class with a metaclass."""
	class metaclass(type):
		def __new__(cls, name, this_bases, d):
			return meta(name, bases, d)

		@classmethod
		def __prepare__(cls, name, this_bases):
			return meta.__prepare__(name, bases)
	return type.__new__(metaclass, 'temporary_class', (), {})


def cstr(arg):
	if isinstance(arg, bytes) or arg is None:
		return arg
	else:
		return arg.encode('charmap')


def pyNativeStr(arg):
	if isinstance(arg, str):
		return arg
	else:
		return arg.decode('charmap')


# Binary Ninja components
import binaryninja._binaryninjacore as core
# __all__ = [
# 	"enums",
# 	"databuffer",
# 	"filemetadata",
# 	"fileaccessor",
# 	"binaryview",
# 	"transform",
# 	"architecture",
# 	"basicblock",
# 	"function",
# 	"log",
# 	"lowlevelil",
# 	"mediumlevelil",
# 	"types",
# 	"functionrecognizer",
# 	"update",
# 	"plugin",
# 	"callingconvention",
# 	"platform",
# 	"demangle",
# 	"mainthread",
# 	"interaction",
# 	"lineardisassembly",
# 	"undoaction",
# 	"highlight",
# 	"scriptingprovider",
# 	"pluginmanager",
# 	"setting",
# 	"metadata",
# 	"flowgraph",
# ]
from binaryninja.enums import *
from binaryninja.databuffer import *
from binaryninja.filemetadata import *
from binaryninja.fileaccessor import *
from binaryninja.binaryview import *
from binaryninja.transform import *
from binaryninja.architecture import *
from binaryninja.basicblock import *
from binaryninja.function import *
from binaryninja.log import *
from binaryninja.lowlevelil import *
from binaryninja.mediumlevelil import *
from binaryninja.types import *
from binaryninja.functionrecognizer import *
from binaryninja.update import *
from binaryninja.plugin import *
from binaryninja.callingconvention import *
from binaryninja.platform import *
from binaryninja.demangle import *
from binaryninja.mainthread import *
from binaryninja.interaction import *
from binaryninja.lineardisassembly import *
from binaryninja.undoaction import *
from binaryninja.highlight import *
from binaryninja.scriptingprovider import *
from binaryninja.downloadprovider import *
from binaryninja.pluginmanager import *
from binaryninja.settings import *
from binaryninja.metadata import *
from binaryninja.flowgraph import *
from binaryninja.datarender import *


def shutdown():
	"""
	``shutdown`` cleanly shuts down the core, stopping all workers and closing all log files.
	"""
	core.BNShutdown()


atexit.register(shutdown)


def get_unique_identifier():
	return core.BNGetUniqueIdentifierString()


def get_install_directory():
	"""
	``get_install_directory`` returns a string pointing to the installed binary currently running

	..warning:: ONLY for use within the Binary Ninja UI, behavior is undefined and unreliable if run headlessly
	"""
	return core.BNGetInstallDirectory()


_plugin_api_name = "python2"


class PluginManagerLoadPluginCallback(object):
	"""Callback for BNLoadPluginForApi("python2", ...), dynamically loads python plugins."""
	def __init__(self):
		self.cb = ctypes.CFUNCTYPE(
			ctypes.c_bool,
			ctypes.c_char_p,
			ctypes.c_char_p,
			ctypes.c_void_p)(self._load_plugin)

	def _load_plugin(self, repo_path, plugin_path, ctx):
		try:
			repo = RepositoryManager()[repo_path]
			plugin = repo[plugin_path]

			if plugin.api != _plugin_api_name:
				raise ValueError("Plugin API name is not " + _plugin_api_name)

			if not plugin.installed:
				plugin.installed = True

			if repo.full_path not in sys.path:
				sys.path.append(repo.full_path)

			__import__(plugin.path)
			log_info("Successfully loaded plugin: {}/{}: ".format(repo_path, plugin_path))
			return True
		except KeyError:
			log_error("Failed to find python plugin: {}/{}".format(repo_path, plugin_path))
		except ImportError as ie:
			log_error("Failed to import python plugin: {}/{}: {}".format(repo_path, plugin_path, ie))
		return False


load_plugin = PluginManagerLoadPluginCallback()
core.BNRegisterForPluginLoading(_plugin_api_name, load_plugin.cb, 0)


class _DestructionCallbackHandler(object):
	def __init__(self):
		self._cb = core.BNObjectDestructionCallbacks()
		self._cb.context = 0
		self._cb.destructBinaryView = self._cb.destructBinaryView.__class__(self.destruct_binary_view)
		self._cb.destructFileMetadata = self._cb.destructFileMetadata.__class__(self.destruct_file_metadata)
		self._cb.destructFunction = self._cb.destructFunction.__class__(self.destruct_function)
		core.BNRegisterObjectDestructionCallbacks(self._cb)

	def destruct_binary_view(self, ctxt, view):
		BinaryView._unregister(view)

	def destruct_file_metadata(self, ctxt, f):
		FileMetadata._unregister(f)

	def destruct_function(self, ctxt, func):
		Function._unregister(func)


_plugin_init = False


def _init_plugins():
	global _plugin_init
	if not _plugin_init:
		core.BNInitCorePlugins()
		core.BNInitUserPlugins()
		core.BNInitRepoPlugins()
	if core.BNIsLicenseValidated():
		_plugin_init = True
	else:
		raise RuntimeError("License is not valid. Please supply a valid license.")


_destruct_callbacks = _DestructionCallbackHandler()

def bundled_plugin_path():
	"""
		``bundled_plugin_path`` returns a string containing the current plugin path inside the `install path <https://docs.binary.ninja/getting-started.html#binary-path>`_

		:return: current bundled plugin path
		:rtype: str, or None on failure
	"""
	return core.BNGetBundledPluginDirectory()

def user_plugin_path():
	"""
		``user_plugin_path`` returns a string containing the current plugin path inside the `user directory <https://docs.binary.ninja/getting-started.html#user-folder>`_

		:return: current user plugin path
		:rtype: str, or None on failure
	"""
	return core.BNGetUserPluginDirectory()

def core_version():
	"""
		``core_version`` returns a string containing the current version

		:return: current version
		:rtype: str, or None on failure
	"""
	return core.BNGetVersionString()

def core_build_id():
	"""
		``core_build_id`` returns a string containing the current build id

		:return: current build id
		:rtype: str, or None on failure
	"""
	core.BNGetBuildId()

def core_serial():
	"""
		``core_serial`` returns a string containing the current serial number

		:return: current serial
		:rtype: str, or None on failure
	"""
	return core.BNGetSerialNumber()

def core_expires():
	'''License Expiration'''
	return gmtime(core.BNGetLicenseExpirationTime())

def core_product():
	'''Product string from the license file'''
	return core.BNGetProduct()

def core_product_type():
	'''Product type from the license file'''
	return core.BNGetProductType()

def core_license_count():
	'''License count from the license file'''
	return core.BNGetLicenseCount()

def core_ui_enabled():
	'''Indicates that a UI exists and the UI has invoked BNInitUI'''
	return core.BNIsUIEnabled()


def core_set_license(licenseData):
	'''Set the Binary Ninja license data, an alternative to storing a ``license.dat`` file'''
	core.BNSetLicense(licenseData)


def get_memory_usage_info():
	count = ctypes.c_ulonglong()
	info = core.BNGetMemoryUsageInfo(count)
	result = {}
	for i in range(0, count.value):
		result[info[i].name] = info[i].value
	core.BNFreeMemoryUsageInfo(info, count.value)
	return result

#if not valid_import("binaryninjaui") and not core_ui_enabled():
#	#Use print because we're headless and log_functions won't work yet
#	print("BINARYNINJAUI module not available.\nPlease re-run the install_api.py python script (with the appropriate version of python you plan to use) to properly set up your Binary Ninja python paths.")