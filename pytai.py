#!/usr/bin/env python -tt
# TAI timestamp manipulation class for Python

__author__ = "Michael T. Babcock <mike@triplepc.com>"
__copyright__ = "Copyright (C) 2003, Michael T. Babcock"
__gpgkeyid__ = "0x8EA27C2D"
__license__ = "LGPL"
__version__ = "0.73"

__about__ = '''I've written this code from -scratch- to decode DJB's tai64n timestamps based on his writings on cr.yp.to and comparing my data to that returned by his programs.

If you are interested in helping with this class's development, feel free to E-mail me at <mike@triplepc.com> with a subject that mentions both Python and TAI.  Any code I receive I will assume you are giving me full copy rights to as per the LGPL this program is under as well as giving me implicit permission to license it to others for a fee under different rules as per their needs.  Should you disagree, please say so explicitly *before* sending me your code / patches.

If you feel that it is unfair that I've made this LGPL'd instead of public domain like Dan's own library, that's really too bad -- I have a different code licensing agenda than Dan and you're free to just write your own, of course, or offer to pay me for a special-case license.

For Dan's original libtai C library with which this should be feature-compatible at some point, see http://cr.yp.to/libtai.html.

As with Dan's own library notes, some of the features in this class library are untested and should be more rigorously tested for exceptions, etc.  Please E-mail me any patches with notes as above re: licensing.'''

__history__ = '''Date       Version  Notes
2003-09-06    0.01  Original play-testing with TAI external formatting, etc.
2003-09-07    0.5   Relatively functional library with the features I needed to decode binary tai values used by supervise/status files.
2003-09-14    0.7   More feature-full library of functions
2003-09-16    0.71  Using map() for some extra readability / efficiency
2003-09-16    0.72  Fixed up localtime() to return times resembling those from tai64nlocal
2003-09-17    0.73  Added special functions to make life easier
'''

__notes__ = '''TAI64N is 12 binary bytes, 8 for seconds, 4 for nanoseconds
TAI64NA is 16 bytes, tai64 + pico and attoseconds'''

def hex_decode(c):
	'''Decode a 4-bit hex character ([0-9A-F]) into its decimal value'''

	o = ord(c[:1])
	if o >= ord('A') and o <= ord('F'):
		return 10 + o - ord('A')
	if o >= ord('a') and o <= ord('f'):
		return 10 + o - ord('a')
	if o >= ord('0') and o <= ord('9'):
		return o - ord('0')


class tai:
	'''Defines a tai timestamp'''

	def __init__(self, t2 = None):
		'''Initialize seconds, micro and attoseconds as well as special
		values like the number of tai seconds in the epoch'''

		# self.epoch = hex_decode("0x4000000000000000")
		self.epoch = 4611686018427387904L
		self.leapsecsfile = "/etc/leapsecs.dat"
		self.timefmt = "%Y-%m-%d %H:%M:%S"

		# ms = milliseconds: 0.001
		# us = microseconds: 0.000001
		# ns = nanoseconds:  0.000000001
		#	   1062966644.596941500
		# ?s = picoseconds:  0.000000000001
		# ?s = attoseconds:  0.000000000000001

		if t2:
			self.secs, self.nsec, self.asec = t2.secs, t2.nsec, t2.asec
		else:
			self.secs, self.nsec, self.asec = 0L, 0L, 0L


	def get_seconds(self):
		'''Return the seconds portion of value'''

		return self.secs


	def get_float(self):
		'''Return sub-second time as a floating-point value'''

		return float("%d.%d" % (self.secs, self.nsec))


	def from_unixtime(self, value):
		'''Convert Unix timestamp in seconds to tai time.'''

		# TODO: take leap-seconds into account
		secs = long(value)
		self.secs = long(self.epoch) + secs

		# Account for sub-second values as floating-point
		subsec = value - secs
		assert(subsec < 1.0)
		self.nsec = long(subsec * 1000000000)


	def _unpack_binary(self, taistr):
		'''Unpack a binary string into x-bit value'''

		bits = len(taistr) * 8

		def bitshift(ord, i):
			val = long(ord) << (bits - (i * 8))
			return val

		ords = map(ord, taistr)

		return sum(map(bitshift, ords, range(1, len(taistr)+1)))


	def _unpack_external(self, str):
		'''Unpack an ascii hex string, then decode'''

		if not str:
			return 0L

		from string import atol
		return atol(str, 16)


	def from_tai64n(self, s):
		'''Convert tai64n binary value and store'''

		self.from_tai64na(s)
		

	def from_tai64na(self, s):
		'''Convert from tai64na binary value'''

		if not s:
			print "Cannot convert empty value"
			return None

		secs,usec,asec = s[:8],s[8:12],s[12:16]

		self.secs = long(self._unpack_binary(secs))
		self.nsec = long(self._unpack_binary(usec))
		self.asec = long(self._unpack_binary(asec))


	def _tobin(self, value, bits):
		'''Helper function for to_tai64... functions'''

		from string import join

		def getbyte(bit):
			'''Returns the byte at the bit position "bit"
			(Dummy-function to replace lambda for readability)'''

			return "%c" % ((value & (long(0xFF) << bit)) >> bit)

		return join(map(getbyte, range(bits-8, -1, -8)), '')
		


	def to_tai64n(self):
		'''Convert seconds to tai64n binary value and return'''

		return self._tobin(self.secs, 64)


	def to_tai64na(self):
		'''Convert to tai64na binary value and return'''

		return self._tobin(self.secs, 64) \
		     + self._tobin(self.nsec, 32) \
		     + self._tobin(self.asec, 32)


	def _toext(self, str):
		'''Returns the binary string as an external hexadecimal string'''

		from string import join
		
		def _gethexchars(c):
			'''Internal function to replace lambda out of preference.
			   N.B. tai64nlocal assumes lower case hex digits.'''

			return "%02x" % ord(c)

		return join(map(_gethexchars, str), '')


	def to_tai64n_ext(self):
		'''Unlike to_tai64n, returns seconds through nanoseconds as a
		   tai64n external timestamp.'''

		bintime = self._tobin(self.secs, 64) \
			+ self._tobin(self.nsec, 32)

		return "@" + self._toext(bintime)


	def pack(self):
		'''Emulate pack(s,t)
		Call as: s = t.pack()'''

		return self.to_tai64n()
	    

	def from_tai64n_ext(self, s):
		'''Read and convert tai64n external value'''

		if s[0] == "@": s = s[1:]

		secs,usec,asec = s[:16],s[16:24],s[24:32]

		self.secs = long(self._unpack_external(secs))
		self.nsec = long(self._unpack_external(usec))
		self.asec = long(self._unpack_external(asec))


	def __str__(self):
		'''Return local time in human-readable format'''

		from time import localtime,strftime

		return "%s.%d" % (strftime(self.timefmt, localtime(int(self))), self.nsec)


	def __repr__(self):
		'''Return a string representation of ourselves.
		   Although it was a toss-up, I decided this should return a
		   tai64na binary timestamp.'''

		return self.to_tai64na()


	def __float__(self):
		'''Return a floating point value representing the current tai time in
		   Unix seconds.'''

		return float("%d.%d" % (self.secs - self.epoch, self.nsec))


	def __int__(self):
		'''Return unix seconds'''

		return self.secs - self.epoch


	def __add__(self, t2):
		'''Add tai(t2) to self'''

		# Add seconds
		self.secs += t2.secs

		# Add atto, then nanoseconds
		nsec = self.nsec + t2.nsec
		asec = self.asec + t2.asec
		
		if asec >= 1000000000L:
			nsec += 1
			asec -= 1000000000L
		self.asec = asec

		if nsec >= 1000000000L:
			self.secs += 1
			nsec -= 1000000000L
		self.nsec = nsec


	def __sub__(self, t2):
		'''Subtract tai(t2) from self'''

		# Subtract seconds, atto then nanoseconds
		self.secs -= t2.secs
		self.nsec -= t2.nsec
		self.asec -= t2.asec
		# TODO: carrying values properly; see taia_sub.c for example?


	def __nonzero__(self):
		'''Return whether we're zero or not'''

		if self.secs == 0 and self.nsec == 0 and self.asec == 0:
			return 0
		return 1


	def __eq__(self, t2):
		'''Compare tai(t2) to self for equality'''

		return self.secs == t2.secs and self.nsec == t2.nsec and self.asec == t2.asec


	def __ne__(self, t2):
		'''Opposite of __eq__()'''

		return not self.__eq__(t2)


	def __lt__(self, t2):
		'''Am I less than t2?'''

		return self.__repr__() < t2.__repr__()


	def __gt__(self, t2):
		'''Am I greater than t2?'''

		return self.__repr__() > t2.__repr__()


	def __le__(self, t2):
		'''Am I less than or equal to t2?'''

		return self.__repr__() <= self.__repr__()


	def __ge__(self, t2):
		'''Am I greater than or equal to t2?'''

		return self.__repr__() >= self.__repr__()


def now():
	'''Emulate tai_now(t)
	Call as: t = tai.now()'''

	from time import time

	t = tai()
	t.from_unixtime(time())
	return t


def add(t1, t2):
	'''Emulate tai_add(t, u, v)
	Call as: t = add(u, v)'''

	return t1 + t2


def sub(t1, t2):
	'''Emulate tai_sub(t, u, v)
	Call as: t = tai.sub(u, v); subtracts v from u'''

	return t1 - t2


def tests():
	'''Run some tests to validate the class'''

	# taistamp.bin contains a 12 byte tai64 timestamp from a
	# supervise/status file for testing.

	f = file("taistamp.bin", "r")
	tai64bin = f.read(12)
	f.close()

	time = tai()
	time.from_tai64n(tai64bin)

	print "%.9f (floating-point value)" % time
	print "%.9f" % time

	if "1063192928.940106511" == "%.9f" % time:
		print "Time conversion from tai64 binary succesful"
	else:
		print "Failed to convert tai64 binary format correctly (1)."

	time.from_tai64n_ext("@400000003f5b957423949abc")

	if str(time) == "2003-09-07 16:30:44.596941500":
		print "Time conversion from tai64n external successful"
	else:
		print "Failed to convert tai64n external format correctly (2)."

	print ""
	print "The decimal values here should look similar:"
	print "         %.9f (floating-point value)" % time
	print time

	binary = time.to_tai64na()
	time2 = tai()
	time2.from_tai64na(binary)
	
	if not time == time2:
		print "Time converstion to/from tai64n format failed."

	print "%s Tai64n external timestamp (pipe through tai64nlocal to get above time)" % time.to_tai64n_ext()


if __name__ == "__main__":
	'''Run some tests'''

	tests()
