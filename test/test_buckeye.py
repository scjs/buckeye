from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

try:
    import unittest.mock as mock
except ImportError:
    import mock

from nose.tools import *

import io
import os
import struct
import zipfile

from buckeye import corpus, process_logs, process_phones, process_words

from buckeye import Speaker, Track

from buckeye.containers import Pause, Word

LOG = """header
#
    0.24  121 <VOICE=modal>
    0.37  121 <CONF=L>
    0.99  121 <VOICE=modal>
    1.19  121 <VOICE=creaky>

"""

PHONES = """header
#
    0.06  121 dh
    0.15  121 ah
    0.24  121 k
    0.37  121 ae
    0.44  121 t;
    0.51  121 ih
    0.59  121 z
    0.70  121 aa
    0.77  121 n
    0.82  121 dh
    0.91  121 ah
    0.99  121 m
    1.12  121 ae+1
    1.19  121 t
"""

WORDS = """header
#
    0.15  121 the; dh iy; dh ah; DT
    0.44  121 cat; k ae t; k ae t; NN
    0.59  121 is; ih z; ih z; VBZ
    0.77  121 on; aa n; aa n; IN
    0.91  121 the; dh iy; dh ah; DT
    1.19  121 mat; m ae t; m ae t; NN
"""

TXT = """the cat is on the mat
"""

with io.open(os.path.join('test', 'files', 'noise.wav'), 'rb') as wav:
    WAV = wav.read()


class TestSpeaker(object):

    @classmethod
    @mock.patch('buckeye.buckeye.Track')
    @mock.patch('buckeye.buckeye.zipfile.ZipFile')
    def setup_class(cls, ZipFileMock, TrackMock):
        ZipFileMock.return_value = ZipFileMock
        ZipFileMock.namelist.return_value = ['s02/s0201b.zip',
                                             's02/s0201a.zip',
                                             's02/s02.zip']
        ZipFileMock.read.return_value = b''

        cls.track = object()
        TrackMock.from_zip.return_value = cls.track

        cls.speaker = Speaker.from_zip('speakers/s02.zip')
        cls.TrackMock = TrackMock

    def test_init(self):
        assert_equal(self.speaker.name, 's02')
        assert_equal(self.speaker.sex, 'f')
        assert_equal(self.speaker.age, 'o')
        assert_equal(self.speaker.interviewer, 'm')

        assert_equal(self.speaker.tracks, [self.track, self.track])

        expected_tracks = ['s02/s0201a.zip', 's02/s0201b.zip']

        for i, track in enumerate(self.TrackMock.call_args_list):
            assert_equal(track[0][0], expected_tracks[i])

    @raises(IOError)
    def test_bad_init(self):
        bad_speaker = Speaker.from_zip('speakers/s41.zip')

    def test_default_init(self):
        speaker = Speaker('s03', range(3))

        assert_equal(speaker.name, 's03')
        assert_equal(speaker.sex, 'm')
        assert_equal(speaker.age, 'o')
        assert_equal(speaker.interviewer, 'm')

        assert_equal(speaker.tracks, range(3))

    def test_iter(self):
        assert_equal(list(iter(self.speaker)), self.speaker.tracks)

    def test_getitem(self):
        assert_equal(self.speaker[0], self.track)

    def test_repr(self):
        assert_equal(repr(self.speaker), 'Speaker("s02")')

    def test_str(self):
        assert_equal(str(self.speaker), '<Speaker s02 (f, o)>')


class TestTrack(object):

    @classmethod
    def setup_class(cls):

        def read_mock(filename):
            if filename.endswith('.words'):
                return WORDS.encode('latin-1')

            if filename.endswith('.phones'):
                return PHONES.encode('latin-1')

            if filename.endswith('.log'):
                return LOG.encode('latin-1')

            if filename.endswith('.txt'):
                return TXT.encode('latin-1')

            if filename.endswith('.wav'):
                return WAV

        mock_contents = mock.Mock()
        mock_contents.read = read_mock

        cls.track = Track.from_zip('s02/s0201a.zip', mock_contents, True)
        cls.track_no_wav = Track.from_zip('s02/s0201a.zip', mock_contents)

    def test_init(self):
        assert_equal(self.track.name, 's0201a')

        assert_equal(len(self.track.words), 6)
        assert_equal(len(self.track.phones), 14)
        assert_equal(len(self.track.log), 4)
        assert_equal(self.track.txt, [TXT.strip()])
        assert_equal(self.track.wav.getnframes(), 9520)

    @raises(AttributeError)
    def test_init_without_wav(self):
        self.track_no_wav.wav

    def test_default_init(self):
        words = os.path.join('test', 'files', 'test.words')
        phones = os.path.join('test', 'files', 'test.phones')
        log = os.path.join('test', 'files', 'test.log')
        txt = os.path.join('test', 'files', 'test.txt')
        wav = os.path.join('test', 'files', 'noise.wav')

        track = Track('test', words, phones, log, txt, wav)

        assert_equal(track.name, 'test')

        assert_equal(len(track.words), 6)
        assert_equal(len(track.phones), 14)
        assert_equal(len(track.log), 4)
        assert_equal(track.txt, [TXT.strip()])
        assert_equal(track.wav.getnframes(), 9520)

    def test_toplevel_zip_init(self):
        zip = os.path.join('test', 'files', 'test.zip')

        track = Track.from_zip(zip, load_wav=True)

        assert_equal(track.name, 'test')

        assert_equal(len(track.words), 6)
        assert_equal(len(track.phones), 14)
        assert_equal(len(track.log), 4)
        assert_equal(track.txt, [TXT.strip()])
        assert_equal(track.wav.getnframes(), 9520)

    def test_repr(self):
        assert_equal(repr(self.track), 'Track("s0201a")')

    def test_str(self):
        assert_equal(str(self.track), '<Track s0201a>')

    def test_clip_wav(self):
        wav_file = io.BytesIO()
        self.track.clip_wav(wav_file, 0.0625, 0.075)

        wav_file.seek(44)
        wav_data = wav_file.read()

        expected = [11779, -14105, -27182, 18371, 30907, -19274, -20887,
                    -26111, 12225, 9851, -17760, 30857, -48, -24792, 28607,
                    8733, 29351, -2146, -12496, 7156, 10389, 30899, 30018,
                    27682, -20565, 9274, -5434, -3414, 13601, 24391, 23657,
                    -7280, -2812, 289, -10859, -30167, 2427, 32293, -22277,
                    32039, 4320, 9779, 13151, 27233, -18332, 29767, -1154,
                    -762, -29000, 3282, -13765, 16919, 11040, 1974, 5365,
                    -27286, 21645, 4398, 17455, 3663, 10553, 3674, -25464,
                    2940, 1382, 11373, -11383, -10087, -8467, 1669, -28032,
                    22010, -6675, 32262, -7948, -11989, 9052, 26283, 3260,
                    -29169, 4516, 31328, -10681, 5354, -7529, -18111, 13744,
                    -26421, 3542, -30737, -12517, 12230, 1776, -10746, 20828,
                    -4235, -27868, -31525, 28116, 182]

        assert_equal(len(wav_data), 2 * len(expected))

        for i in range(0, len(wav_data), 2):
            val = wav_data[i:i + 2]
            val_unpacked = struct.unpack('h', val)
            assert_equal(val_unpacked[0], expected[i // 2])

    @raises(AttributeError)
    def test_clip_unopened_wav(self):
        wav_file = io.BytesIO()
        self.track_no_wav.clip_wav(wav_file, 0.0625, 0.075)

    def test_set_phones(self):
        assert_equal(self.track.words[1].phones[0].seg, 'k')
        assert_equal(self.track.words[1].phones[1].seg, 'ae')
        assert_equal(self.track.words[1].phones[2].seg, 't')
        assert_equal(len(self.track.words[1].phones), 3)

    def test_set_phones_left_edge_misaligned(self):
        self.track.phones[2]._beg = 0.18
        self.track._set_phones()

        yield self.test_set_phones

        self.track.phones[2]._beg = 0.15
        self.track._set_phones()

    def test_set_phones_left_edge_too_long(self):
        self.track.phones[2]._beg = 0.01
        self.track._set_phones()

        assert_equal(self.track.words[1].phones[0].seg, 'ae')
        assert_equal(len(self.track.words[1].phones), 2)

        self.track.phones[2]._beg = 0.15
        self.track._set_phones()

    def test_set_phones_right_edge_misaligned(self):
        self.track.phones[4]._end = 0.43
        self.track._set_phones()

        yield self.test_set_phones

        self.track.phones[4]._end = 0.44
        self.track._set_phones()

    def test_set_phones_right_edge_too_long(self):
        self.track.phones[4]._end = 0.52
        self.track._set_phones()

        assert_equal(self.track.words[1].phones[1].seg, 'ae')
        assert_equal(len(self.track.words[1].phones), 2)

        self.track.phones[4]._end = 0.44
        self.track._set_phones()

    def test_set_phones_backwards_word(self):
        self.track.words[1]._beg = 0.44
        self.track.words[1]._end = 0.15
        self.track._set_phones()

        assert_equal(self.track.words[1].phones, [])

        self.track.words[1]._beg = 0.15
        self.track.words[1]._end = 0.44
        self.track._set_phones()

    def test_set_phones_zero_word(self):
        self.track.words[1]._end = 0.15
        self.track._set_phones()

        assert_equal(self.track.words[1].phones, [])

        self.track.words[1]._end = 0.44
        self.track._set_phones()

    def test_set_phones_phonetic_is_none(self):
        self.track.words[1]._phonetic = None
        self.track._set_phones()

        yield self.test_set_phones

        self.track.words[1]._phonetic = ['k', 'ae', 't']
        self.track._set_phones()

    def test_get_logs_too_early(self):
        logs = self.track.get_logs(-1.0, 0.0)
        assert_equal(logs, [])

    def test_get_logs_too_late(self):
        logs = self.track.get_logs(2.0, 3.0)
        assert_equal(logs, [])

    def test_get_logs_exact(self):
        logs = self.track.get_logs(0.24, 0.37)

        assert_equal(len(logs), 1)
        assert_equal(logs[0].entry, '<CONF=L>')

    def test_get_logs_exact_two(self):
        logs = self.track.get_logs(0.24, 0.99)

        assert_equal(len(logs), 2)
        assert_equal(logs[0].entry, '<CONF=L>')
        assert_equal(logs[1].entry, '<VOICE=modal>')

    def test_get_logs_left_overlap(self):
        logs = self.track.get_logs(0.35, 0.99)

        assert_equal(len(logs), 2)
        assert_equal(logs[0].entry, '<CONF=L>')
        assert_equal(logs[1].entry, '<VOICE=modal>')

    def test_get_logs_right_overlap(self):
        logs = self.track.get_logs(0.24, 0.39)

        assert_equal(len(logs), 2)
        assert_equal(logs[0].entry, '<CONF=L>')
        assert_equal(logs[1].entry, '<VOICE=modal>')

    def get_logs_all(self):
        logs = self.track.get_logs(0, 1.19)

        assert_equal(len(logs), 4)
        assert_equal(logs[0].entry, '<VOICE=modal>')
        assert_equal(logs[1].entry, '<CONF=L>')
        assert_equal(logs[2].entry, '<VOICE=modal>')
        assert_equal(logs[3].entry, '<VOICE=creaky>')

    def test_get_logs_backwards(self):
        logs = self.track.get_logs(0.39, 0.22)
        assert_equal(logs, [])

    def get_logs_backwards_all(self):
        logs = self.track.get_logs(1.19, 0)
        assert_equal(logs, [])

    def test_get_logs_last_overlap(self):
        logs = self.track.get_logs(1.0, 1.2)

        assert_equal(len(logs), 1)
        assert_equal(logs[0].entry, '<VOICE=creaky>')

    def test_get_logs_last_overlap_two(self):
        logs = self.track.get_logs(0.98, 1.2)

        assert_equal(len(logs), 2)
        assert_equal(logs[0].entry, '<VOICE=modal>')
        assert_equal(logs[1].entry, '<VOICE=creaky>')


class TestCorpus(object):

    @mock.patch('buckeye.buckeye.glob.glob')
    @mock.patch('buckeye.buckeye.Speaker')
    def test_corpus(self, SpeakerMock, GlobMock):
        GlobMock.return_value = ['s02.zip', 's03.zip', 's01.zip']

        expected_calls = [mock.call('s01.zip', False),
                          mock.call('s02.zip', False),
                          mock.call('s03.zip', False)]

        for speaker in corpus(''):
            pass

        assert_equal(SpeakerMock.from_zip.call_args_list, expected_calls)


class TestProcessLogs(object):

    @classmethod
    def setup_class(cls):
        cls.expected_entries = ['<VOICE=modal>', '<CONF=L>',
                                '<VOICE=modal>', '<VOICE=creaky>']

        cls.expected_begs = [0.0, 0.24, 0.37, 0.99]
        cls.expected_ends = [0.24, 0.37, 0.99, 1.19]

    def check_expected(self, logs):
        assert_equal(len(logs), 4)

        for i, log in enumerate(logs):
            assert_equal(log.entry, self.expected_entries[i])
            assert_equal(log.beg, self.expected_begs[i])
            assert_equal(log.end, self.expected_ends[i])

    def test_process_logs(self):
        logs = list(process_logs(io.StringIO(LOG)))

        yield self.check_expected, logs

    @raises(EOFError)
    def test_process_blank_logs(self):
        blank_logfile = io.StringIO('\n\n\n\n')
        list(process_logs(blank_logfile))

    @raises(EOFError)
    def test_process_empty_logs(self):
        no_entries = io.StringIO('header#\n\n\n')
        list(process_logs(no_entries))

    def test_blank_line_in_header(self):
        with_spaced_header = '\n\n'.join([LOG[:8], LOG[8:]])
        logs_spaced = list(process_logs(io.StringIO(with_spaced_header)))

        yield self.check_expected, logs_spaced

    def test_blank_line_in_entry(self):
        with_spaced_entry = '\n\n'.join([LOG[:36], LOG[36:]])
        logs_spaced = list(process_logs(io.StringIO(with_spaced_entry)))

        yield self.check_expected, logs_spaced

    def test_missing_entry(self):
        lines = 'header\n#\n    0.07  121   \n'
        missing_entry = next(process_logs(io.StringIO(lines)))

        assert_equal(missing_entry.entry, None)
        assert_equal(missing_entry.beg, 0.0)
        assert_equal(missing_entry.end, 0.07)


class TestProcessPhones(object):

    @classmethod
    def setup_class(cls):
        cls.expected_segs = ['dh', 'ah', 'k', 'ae', 't', 'ih', 'z', 'aa', 'n',
                             'dh', 'ah', 'm', 'ae', 't']

        cls.expected_begs = [0.0, 0.06, 0.15, 0.24, 0.37, 0.44, 0.51, 0.59,
                             0.70, 0.77, 0.82, 0.91, 0.99, 1.12]
        cls.expected_ends = [0.06, 0.15, 0.24, 0.37, 0.44, 0.51, 0.59, 0.70,
                             0.77, 0.82, 0.91, 0.99, 1.12, 1.19]

    def check_expected(self, phones):
        assert_equal(len(phones), 14)

        for i, phone in enumerate(phones):
            assert_equal(phone.seg, self.expected_segs[i])
            assert_equal(phone.beg, self.expected_begs[i])
            assert_equal(phone.end, self.expected_ends[i])

    def test_process_phones(self):
        phones = list(process_phones(io.StringIO(PHONES)))

        yield self.check_expected, phones

    @raises(EOFError)
    def test_process_blank_phones(self):
        blank_phonesfile = io.StringIO('\n\n\n\n')
        list(process_phones(blank_phonesfile))

    @raises(EOFError)
    def test_process_empty_phones(self):
        no_entries = io.StringIO('header#\n\n\n')
        list(process_phones(no_entries))

    def test_blank_line_in_header(self):
        with_spaced_header = '\n\n'.join([PHONES[:8], PHONES[8:]])
        phones_spaced = list(process_phones(io.StringIO(with_spaced_header)))

        yield self.check_expected, phones_spaced

    def test_blank_line_in_entry(self):
        with_spaced_entry = '\n\n'.join([PHONES[:75], PHONES[75:]])
        phones_spaced = list(process_phones(io.StringIO(with_spaced_entry)))

        yield self.check_expected, phones_spaced

    def test_missing_seg(self):
        lines = 'header\n#\n    0.03  121   \n'
        missing_seg = next(process_phones(io.StringIO(lines)))

        assert_equal(missing_seg.seg, None)
        assert_equal(missing_seg.beg, 0.0)
        assert_equal(missing_seg.end, 0.03)


class TestProcessWords(object):

    @classmethod
    def setup_class(cls):
        cls.expected_begs = [0.0, 0.15, 0.44, 0.59, 0.77, 0.91]
        cls.expected_ends = [0.15, 0.44, 0.59, 0.77, 0.91, 1.19]
        cls.expected_orthographies = ['the', 'cat', 'is', 'on', 'the', 'mat']

        cls.expected_phonemics = [['dh', 'iy'], ['k', 'ae', 't'], ['ih', 'z'],
                                  ['aa', 'n'], ['dh', 'iy'], ['m', 'ae', 't']]

        cls.expected_phonetics = [['dh', 'ah'], ['k', 'ae', 't'], ['ih', 'z'],
                                  ['aa', 'n'], ['dh', 'ah'], ['m', 'ae', 't']]

        cls.expected_pos = ['DT', 'NN', 'VBZ', 'IN', 'DT', 'NN']

    def check_expected(self, words):
        assert_equal(len(words), 6)

        for i, word in enumerate(words):
            assert_equal(word.beg, self.expected_begs[i])
            assert_equal(word.end, self.expected_ends[i])
            assert_equal(word.orthography, self.expected_orthographies[i])
            assert_equal(word.phonemic, self.expected_phonemics[i])
            assert_equal(word.phonetic, self.expected_phonetics[i])
            assert_equal(word.pos, self.expected_pos[i])

    def test_process_words(self):
        words = list(process_words(io.StringIO(WORDS)))

        yield self.check_expected, words

    @raises(EOFError)
    def test_process_blank_words(self):
        blank_wordsfile = io.StringIO('\n\n\n\n')
        list(process_words(blank_wordsfile))

    @raises(EOFError)
    def test_process_empty_words(self):
        no_entries = io.StringIO('header#\n\n\n')
        list(process_words(no_entries))

    def test_blank_line_in_header(self):
        with_spaced_header = '\n\n'.join([WORDS[:8], WORDS[8:]])
        words_spaced = list(process_words(io.StringIO(with_spaced_header)))

        yield self.check_expected, words_spaced

    def test_blank_line_in_entry(self):
        with_spaced_entry = '\n\n'.join([WORDS[:44], WORDS[44:]])
        words_spaced = list(process_words(io.StringIO(with_spaced_entry)))

        yield self.check_expected, words_spaced

    def test_pause_in_words(self):
        pause_line = '\n    0.44  121 <SIL>; S; S; null'
        with_pause_entry = pause_line.join([WORDS[:44], WORDS[82:]])
        words_paused = list(process_words(io.StringIO(with_pause_entry)))

        assert_equal(words_paused[1].beg, 0.15)
        assert_equal(words_paused[1].end, 0.44)
        assert_equal(words_paused[1].entry, '<SIL>')

    def test_two_fields(self):
        lines = 'header\n#\n0.15  121 the; DT\n'
        two_field_word = next(process_words(io.StringIO(lines)))

        assert_equal(two_field_word.beg, 0.0)
        assert_equal(two_field_word.end, 0.15)
        assert_equal(two_field_word.orthography, 'the')
        assert_equal(two_field_word.phonemic, None)
        assert_equal(two_field_word.phonetic, None)
        assert_equal(two_field_word.pos, 'DT')

    def test_three_fields(self):
        lines = 'header\n#\n0.15  121 the; dh iy; DT\n'
        three_field_word = next(process_words(io.StringIO(lines)))

        assert_equal(three_field_word.beg, 0.0)
        assert_equal(three_field_word.end, 0.15)
        assert_equal(three_field_word.orthography, 'the')
        assert_equal(three_field_word.phonemic, ['dh', 'iy'])
        assert_equal(three_field_word.phonetic, None)
        assert_equal(three_field_word.pos, 'DT')
