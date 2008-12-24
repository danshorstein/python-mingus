from binascii import a2b_hex

class MidiFileOut:

	tracks = []
	time_division = "\x00\x02"

	def __init__(self):
		pass

	def get_midi_data(self):
		tracks = [ t.get_midi_data() for t in self.tracks ]
		return self.header() + "".join(tracks)

	def header(self):
		"""Returns a header for type 1 midi file"""
		tracks = a2b_hex("%04x" % len(self.tracks))
		return "MThd\x00\x00\x00\x06\x00\x01" + tracks + self.time_division

class MidiTrack:

	track_data = ''
	delta_time = '\x00'

	def end_of_track(self):
		"""End of track meta event."""
		return "\x00\xff\x2f\x00"

	def play_Note(self, channel, note, velocity = 64):
		self.track_data += self.note_on(channel, int(note), velocity)
		print len(self.track_data)

	def play_NoteContainer(self, channel, notecontainer, velocity = 64):
		[self.play_Note(channel, x, velocity) for x in notecontainer]


	def stop_Note(self, channel, note, velocity = 64):
		self.track_data += self.note_off(channel, int(note), velocity)

	def header(self):
		print len(self.track_data), "%08x" % (len(self.track_data))
		chunk_size = a2b_hex("%08x" % (len(self.track_data) +\
				len(self.end_of_track())))
		return "MTrk" + chunk_size

	def get_midi_data(self):
		return self.header() + self.track_data + self.end_of_track()

	def midi_event(self, event_type, channel, param1, param2):
		"""Parameters should be given as integers."""
		"""event_type and channel: 4 bits."""
		"""param1 and param2: 1 byte."""
		assert event_type < 128 and event_type >= 0
		assert channel < 16 and channel >= 0
		tc = a2b_hex("%x%x" % (event_type, channel))
		params = a2b_hex("%02x%02x" % (param1, param2))

		return self.delta_time + tc + params

	def note_off(self, channel, note, velocity):
		return self.midi_event(8, channel, note, velocity)

	def note_on(self, channel, note, velocity):
		return self.midi_event(9, channel, note, velocity)

	def reset(self):
		self.track_data = ''
		self.delta_time = '\x00'

	def set_deltatime(self, delta_time):
		self.delta_time = delta_time


if __name__ == '__main__':
	m = MidiFileOut()
	t = MidiTrack()
	m.tracks = [t]
	t.play_Note(1, 60)
	t.play_Note(1, 64)
	t.play_Note(1, 67)
	t.set_deltatime("\x01")
	t.stop_Note(1, 60)
	t.stop_Note(1, 64)
	t.stop_Note(1, 67)
	t.play_NoteContainer(1, [60, 65, 68])
	f = open("mingustest.mid", "wb")
	f.write(m.get_midi_data())
	print "Wrote to mingustest.mid"
	f.close()