import os
import asyncio
import subprocess
import sys


class ProcessTimeout:
	_timed_out = False
	
	def __init__(self, timeout, *args, **kwargs):
		assert 'stdin' not in kwargs
		assert 'stdout' not in kwargs

		self.timeout = timeout
		self.args = args
		self.kwargs = kwargs
	
	def run_sync(self):
		loop = asyncio.get_event_loop()
		return loop.run_until_complete(self.run(loop))
	
	def stop(self):
		self._subprocess.kill()
		self._timeout.cancel()

	async def run(self, loop):
		stdout = os.fdopen(sys.stdout.fileno(), 'wb')

		self._subprocess = await asyncio.create_subprocess_exec(
			stdout=asyncio.subprocess.PIPE,
			stderr=sys.stderr,
			*self.args,
			**self.kwargs
		)
		terminated = asyncio.ensure_future(self._subprocess.wait())
		try:
			self.set_timeout(loop)

			last_line = None
			while not terminated.done() and not self._timed_out:
				try:
					line = await self._subprocess.stdout.readuntil(b'\n')
				except asyncio.IncompleteReadError as e:
					stdout.write(e.partial)
					break

				stdout.write(line)

				if line != last_line:
					# Reset the timer
					self._timeout.cancel()
					self.set_timeout(loop)
				
				last_line = line
		finally:
			self._timeout.cancel()

		await terminated

		# Flush the remaining output
		stdout.write(await self._subprocess.stdout.read())

		if self._timed_out:
			raise subprocess.TimeoutExpired(self.args, self.timeout)

		return self._subprocess.returncode
		
	def set_timeout(self, loop):
		self._timeout = loop.call_later(self.timeout, self.on_timeout)
		return self._timeout
	
	def on_timeout(self):
		self._timed_out = True
		self._subprocess.kill()
