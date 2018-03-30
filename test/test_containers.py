from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from nose.tools import *

from buckeye.containers import Word, Pause, LogEntry, Phone

class TestWord(object):

    def setup(self):
        self.word = Word('the', 0.05, 0.25, ['dh', 'iy'], ['dh'], 'DT')
        self.empty_word = Word('uh', 0.25, 0.40)

    def test_word(self):
        assert_equal(self.word.orthography, 'the')
        assert_equal(self.word.beg, 0.05)
        assert_equal(self.word.end, 0.25)
        assert_equal(self.word.phonemic, ['dh', 'iy'])
        assert_equal(self.word.phonetic, ['dh'])
        assert_equal(self.word.pos, 'DT')

        assert_equal(self.word.dur, 0.25 - 0.05)
        assert_is_none(self.word.phones)

    def test_empty_word(self):
        assert_equal(self.empty_word.orthography, 'uh')
        assert_equal(self.empty_word.beg, 0.25)
        assert_equal(self.empty_word.end, 0.40)
        assert_is_none(self.empty_word.phonemic)
        assert_is_none(self.empty_word.phonetic)
        assert_is_none(self.empty_word.pos)
        assert_is_none(self.empty_word.phones)
        assert_equal(self.empty_word.dur, 0.40 - 0.25)

    @raises(TypeError)
    def test_missing_word(self):
        word = Word()

    @raises(AttributeError)
    def test_word_nonnumeric_times(self):
        word = Word('the', 'beg', 'end', ['dh', 'iy'], ['dh'], 'DT')
        word.dur

    def test_syllables(self):
        assert_equal(self.word.syllables(), 1)
        assert_equal(self.word.syllables(phonetic=False), 1)
        assert_equal(self.word.syllables(phonetic=True), 0)

    def test_syllables_phones(self):
        word = Word('the', 0.05, 0.25, ['dh', 'iy'], ['dh'], 'DT')
        word._phones = [Phone('dh')]

        assert_equal(word.syllables(), 1)
        assert_equal(word.syllables(phonetic=False), 1)
        assert_equal(word.syllables(phonetic=True), 0)

    def test_empty_syllables(self):
        assert_raises(TypeError, self.empty_word.syllables)
        assert_raises(TypeError, self.empty_word.syllables, False)
        assert_raises(TypeError, self.empty_word.syllables, True)

    @raises(AttributeError)
    def test_readonly_orthography(self):
        self.word.orthography = 'an'

    @raises(AttributeError)
    def test_readonly_beg(self):
        self.word.beg = 0.0

    @raises(AttributeError)
    def test_readonly_end(self):
        self.word.end = 1.0

    @raises(AttributeError)
    def test_readonly_dur(self):
        self.word.dur = 1.0

    @raises(AttributeError)
    def test_readonly_phonemic(self):
        self.word.phonemic = ['uh', 'n']

    @raises(AttributeError)
    def test_readonly_phonetic(self):
        self.word.phonetic = ['en']

    @raises(AttributeError)
    def test_readonly_pos(self):
        self.word.pos = 'DT'

    def test_phones_setter(self):
        assert_false(self.word.misaligned)

        phone_th = Phone('th')
        phone_dh = Phone('dh')

        self.word._phones = [phone_th]
        assert_in(phone_th, self.word.phones)
        assert_true(self.word.misaligned)

        self.word._phones = [phone_dh]
        assert_in(phone_dh, self.word.phones)
        assert_false(self.word.misaligned)

        self.word._phones = []
        assert_true(self.word.misaligned)

    def test_misaligned_backwards(self):
        misaligned_word = Word('', 0.50, 0.25, phonetic=['dh'])
        misaligned_word._phones = [Phone('dh')]
        assert_true(misaligned_word.misaligned)

    def test_misaligned_missing_phonetic_no_phones(self):
        misaligned_word = Word('', 0.25, 0.50, phonetic=None)
        assert_false(misaligned_word.misaligned)

    def test_misaligned_missing_phonetic_with_phones(self):
        misaligned_word = Word('', 0.25, 0.50, phonetic=None)
        misaligned_word._phones = [Phone('dh')]
        assert_true(misaligned_word.misaligned)

    def test_misaligned_different_phonetic_and_phones(self):
        misaligned_word = Word('', 0.25, 0.50, phonetic=['th'])
        misaligned_word._phones = [Phone('dh')]
        assert_true(misaligned_word.misaligned)

    def test_misaligned_different_length_phonetic_and_phones(self):
        misaligned_word = Word('', 0.25, 0.50, phonetic=['dh', 'ah'])
        misaligned_word._phones = [Phone('dh')]
        assert_true(misaligned_word.misaligned)

    def test_misaligned_zero(self):
        zero_word = Word('', 0.40, 0.40)
        assert_false(zero_word.misaligned)

    def test_repr(self):
        assert_equal(repr(self.word), "Word('the', 0.05, 0.25, ['dh', 'iy'], ['dh'], 'DT')")

    def test_str(self):
        assert_equal(str(self.word), '<Word "the" at 0.05>')


class TestPause(object):

    def setup(self):
        self.pause = Pause('<SIL>', 0.0, 0.05)

    def test_pause(self):
        assert_equal(self.pause.entry, '<SIL>')
        assert_equal(self.pause.beg, 0.0)
        assert_equal(self.pause.end, 0.05)

    def test_empty_pause(self):
        empty_pause = Pause()

        assert_is_none(empty_pause.entry)
        assert_is_none(empty_pause.beg)
        assert_is_none(empty_pause.end)

    @raises(AttributeError)
    def test_pause_nonnumeric_times(self):
        pause = Pause('<SIL>', 'beg', 'end')
        pause.dur

    @raises(AttributeError)
    def test_readonly_entry(self):
        self.pause.entry = 'an'

    @raises(AttributeError)
    def test_readonly_beg(self):
        self.pause.beg = 0.0

    @raises(AttributeError)
    def test_readonly_end(self):
        self.pause.end = 1.0

    def test_phones_setter(self):
        assert_false(self.pause.misaligned)

        phone_sil = Phone('SIL')

        self.pause._phones = [phone_sil]
        assert_in(phone_sil, self.pause.phones)
        assert_false(self.pause.misaligned)

        self.pause._phones = []
        assert_false(self.pause.misaligned)

    def test_misaligned(self):
        misaligned_pause = Pause('', 0.50, 0.25)
        assert_true(misaligned_pause.misaligned)

        phone_sil = Phone('SIL')
        misaligned_pause._phones = [phone_sil]
        assert_true(misaligned_pause.misaligned)

    def test_misaligned_zero(self):
        zero_pause = Pause('', 0.40, 0.40)
        assert_false(zero_pause.misaligned)

    def test_repr(self):
        assert_equal(repr(self.pause), "Pause('<SIL>', 0.0, 0.05)")

    def test_str(self):
        assert_equal(str(self.pause), '<Pause <SIL> at 0.0>')


class TestLogEntry(object):

    def setup(self):
        self.log = LogEntry('<voiceless-vowel>', 0.45, 0.50)

    def test_log(self):
        assert_equal(self.log.entry, '<voiceless-vowel>')
        assert_equal(self.log.beg, 0.45)
        assert_equal(self.log.end, 0.50)
        assert_equal(self.log.dur, 0.50 - 0.45)

    def test_empty_log(self):
        empty_log = LogEntry('<voiceless-vowel>')

        assert_equal(empty_log.entry, '<voiceless-vowel>')
        assert_is_none(empty_log.beg)
        assert_is_none(empty_log.end)
        assert_raises(AttributeError, getattr, empty_log, 'dur')

    @raises(TypeError)
    def test_log_missing(self):
        log = LogEntry()

    @raises(AttributeError)
    def test_readonly_entry(self):
        self.log.entry = '<VOICE=creaky>'

    @raises(AttributeError)
    def test_readonly_beg(self):
        self.log.beg = 0.0

    @raises(AttributeError)
    def test_readonly_end(self):
        self.log.end = 1.0

    @raises(AttributeError)
    def test_readonly_dur(self):
        self.log.dur = 1.0

    def test_repr(self):
        assert_equal(repr(self.log), "LogEntry('<voiceless-vowel>', 0.45, 0.5)")

    def test_str(self):
        assert_equal(str(self.log), '<Log "<voiceless-vowel>" at 0.45>')


class TestPhone(object):

    def setup(self):
        self.phone = Phone('dh', 0.05, 0.15)

    def test_phone(self):
        assert_equal(self.phone.seg, 'dh')
        assert_equal(self.phone.beg, 0.05)
        assert_equal(self.phone.end, 0.15)
        assert_equal(self.phone.dur, 0.15 - 0.05)

    def test_empty_phone(self):
        empty_phone = Phone('th')

        assert_equal(empty_phone.seg, 'th')
        assert_is_none(empty_phone.beg)
        assert_is_none(empty_phone.end)
        assert_raises(AttributeError, getattr, empty_phone, 'dur')

    @raises(TypeError)
    def test_phone_missing(self):
        phone = Phone()

    @raises(AttributeError)
    def test_readonly_seg(self):
        self.phone.seg = 'ah'

    @raises(AttributeError)
    def test_readonly_beg(self):
        self.phone.beg = 0.0

    @raises(AttributeError)
    def test_readonly_end(self):
        self.phone.end = 1.0

    @raises(AttributeError)
    def test_readonly_dur(self):
        self.phone.dur = 1.0

    def test_repr(self):
        assert_equal(repr(self.phone), "Phone('dh', 0.05, 0.15)")

    def test_str(self):
        assert_equal(str(self.phone), '<Phone [dh] at 0.05>')
