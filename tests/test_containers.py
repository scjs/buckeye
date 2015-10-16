from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from nose.tools import *

from buckeye.containers import Word, Pause, LogEntry, Phone, Utterance

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

    def test_syllables(self):
        assert_equal(self.word.syllables(), 1)
        assert_equal(self.word.syllables(phonetic=False), 1)
        assert_equal(self.word.syllables(phonetic=True), 0)

        assert_is_none(self.empty_word.syllables())
        assert_is_none(self.empty_word.syllables(False))
        assert_is_none(self.empty_word.syllables(True))

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

        self.word.phones = [phone_th]
        assert_in(phone_th, self.word.phones)
        assert_true(self.word.misaligned)

        self.word.phones = [phone_dh]
        assert_in(phone_dh, self.word.phones)
        assert_false(self.word.misaligned)

        self.word.phones = []
        assert_true(self.word.misaligned)

    def test_misaligned(self):
        misaligned_word = Word('', 0.50, 0.25)
        assert_true(misaligned_word.misaligned)

        phone_dh = Phone('dh')
        misaligned_word.phones = [phone_dh]
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

        self.pause.phones = [phone_sil]
        assert_in(phone_sil, self.pause.phones)
        assert_false(self.pause.misaligned)

        self.pause.phones = []
        assert_false(self.pause.misaligned)

    def test_misaligned(self):
        misaligned_pause = Pause('', 0.50, 0.25)
        assert_true(misaligned_pause.misaligned)

        phone_sil = Phone('SIL')
        misaligned_pause.phones = [phone_sil]
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
        assert_is_none(empty_log.dur)

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
        assert_is_none(empty_phone.dur)

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


class TestUtterance(object):

    def setup(self):
        self.words = [
            Word('the', 0, 0.10, ['dh', 'iy'], ['dh'], 'DT'),
            Word('cat', 0.10, 0.39, ['k', 'ae', 't'], ['k', 'ae', 't'], 'NN'),
            Word('is', 0.39, 0.55, ['ih', 'z'], ['ih', 'z'], 'VB'),
            Word('on', 0.55, 0.73, ['aa', 'n'], ['aan'], 'IN'),
            Word('the', 0.73, 0.80, ['dh', 'iy'], ['dh', 'uh'], 'DT'),
            Word('mat', 0.80, 1.25, ['m', 'ae', 't'], ['m', 'ae', 't'], 'NN')]

        self.utt = Utterance(self.words)
        self.empty_utt = Utterance()

    def test_utterance(self):
        assert_equal(self.utt.beg, 0)
        assert_equal(self.utt.end, 1.25)
        assert_equal(self.utt.dur, 1.25 - 0)
        assert_equal(self.utt.words(), self.words)
        assert_equal(self.utt._Utterance__previous, 1.25)

    def test_empty_utterance(self):
        assert_is_none(self.empty_utt.beg)
        assert_is_none(self.empty_utt.end)
        assert_is_none(self.empty_utt.dur)
        assert_equal(self.empty_utt.words(), [])
        assert_equal(self.empty_utt._Utterance__previous, 0.0)

    @raises(ValueError)
    def test_backwards_utterance(self):
        utt_backwards = Utterance(self.words[::-1])

    @raises(AttributeError)
    def test_readonly_beg(self):
        self.utt.beg = 0.0

    @raises(AttributeError)
    def test_readonly_end(self):
        self.utt.end = 1.0

    @raises(AttributeError)
    def test_readonly_dur(self):
        self.utt.dur = 1.0

    def test_append(self):
        utt_a = Utterance()

        word = Word('the', 0.05, 0.25, ['dh', 'iy'], ['dh'], 'DT')
        utt_a.append(word)

        assert_equal(utt_a.words(), [word])
        assert_equal(utt_a.beg, 0.05)
        assert_equal(utt_a.end, 0.25)
        assert_equal(utt_a.dur, 0.25 - 0.05)

        uh = Word('uh', 0.25, 0.45, ['ah'], ['ah'], 'UH')
        utt_a.append(uh)

        assert_equal(utt_a.words(), [word, uh])
        assert_equal(utt_a.beg, 0.05)
        assert_equal(utt_a.end, 0.45)
        assert_equal(utt_a.dur, 0.45 - 0.05)

    @raises(TypeError)
    def test_append_missing(self):
        self.empty_utt.append('the')

    @raises(ValueError)
    def test_append_before_utterance(self):
        word = Word('uh', 0.25, 0.45, ['ah'], ['ah'], 'UH')
        self.utt.append(word)

    @raises(ValueError)
    def test_append_before_utterance_beg_none(self):
        word = Word('uh', None, 0.45, ['ah'], ['ah'], 'UH')
        self.utt.append(word)

    @raises(ValueError)
    def test_append_before_utterance_end_none(self):
        word = Word('uh', 0.25, None, ['ah'], ['ah'], 'UH')
        self.utt.append(word)

    @raises(ValueError)
    def test_append_backwards(self):
        word = Word('uh', 1.95, 1.65, ['ah'], ['ah'], 'UH')
        self.empty_utt.append(word)

    def test_append_none(self):
        word = Word('the', 0.05, 0.25, ['dh', 'iy'], ['dh'], 'DT')
        utt_append_none = Utterance([word])
        assert_equal(utt_append_none._Utterance__previous, 0.25)

        none_word = Word('uh', None, None, ['ah'], ['ah'], 'UH')
        utt_append_none.append(none_word)
        assert_equal(utt_append_none[-1], none_word)
        assert_equal(utt_append_none._Utterance__previous, 0.25)

        none_beg_word = Word('uh', None, 0.5, ['ah'], ['ah'], 'UH')
        utt_append_none.append(none_beg_word)
        assert_equal(utt_append_none[-1], none_beg_word)
        assert_equal(utt_append_none._Utterance__previous, 0.5)

        none_end_word = Word('uh', 0.65, None, ['ah'], ['ah'], 'UH')
        utt_append_none.append(none_end_word)
        assert_equal(utt_append_none[-1], none_end_word)
        assert_equal(utt_append_none._Utterance__previous, 0.65)

    def test_len(self):
        assert_equal(len(self.utt), 6)

    def test_speech_rate(self):
        assert_equal(self.utt.speech_rate(), 4.0)
        assert_equal(self.utt.speech_rate(use_phonetic=False), 4.8)

        assert_equal(self.empty_utt.speech_rate(), 0.0)
        assert_equal(self.empty_utt.speech_rate(use_phonetic=False), 0.0)

        pause = Pause(beg=1.25, end=1.50)

        self.utt.append(pause)
        assert_equal(self.utt.speech_rate(), 4.0)
        assert_not_in(pause, self.utt)

    def test_strip_beg_pause(self):
        pause = Pause(beg=0, end=0.55)
        utt_strip = Utterance([pause] + self.words[3:])

        utt_strip.strip()

        assert_not_in(pause, utt_strip)
        assert_equal(utt_strip.words(), self.words[3:])

    def test_strip_end_pause(self):
        pause = Pause(beg=1.25, end=1.85)
        utt_strip = Utterance(self.words + [pause])

        utt_strip.strip()

        assert_not_in(pause, utt_strip)
        assert_equal(utt_strip.words(), self.words)

    def test_strip_beg_invalid(self):
        invalid = Word('', 0.55, 'n/a')
        utt_strip = Utterance([invalid] + self.words[3:])

        utt_strip.strip()

        assert_not_in(invalid, utt_strip)
        assert_equal(utt_strip.words(), self.words[3:])
    
    def test_strip_end_invalid(self):
        invalid = Word('', 1.25, 'n/a')
        utt_strip = Utterance(self.words + [invalid])

        utt_strip.strip()

        assert_not_in(invalid, utt_strip)
        assert_equal(utt_strip.words(), self.words)
    
    def test_strip_beg_zero(self):
        zero = Word('', 0.0, 0.0)
        utt_strip = Utterance([zero] + self.words)

        utt_strip.strip()

        assert_not_in(zero, utt_strip)
        assert_equal(utt_strip.words(), self.words)

    def test_strip_end_zero(self):
        zero = Word('', 1.25, 1.25)
        utt_strip = Utterance(self.words + [zero])

        utt_strip.strip()

        assert_not_in(zero, utt_strip)
        assert_equal(utt_strip.words(), self.words)

    def test_strip_beg_multiple(self):
        pause = Pause(beg=0, end=0.55)
        invalid = Word('', 0.55, None)
        zero = Word('', 0.55, 0.55)
        utt_strip = Utterance([pause, invalid, zero] + self.words[3:])
        
        utt_strip.strip()
        
        for entry in {pause, invalid, zero}:
            assert_not_in(entry, utt_strip)

        assert_equal(utt_strip.words(), self.words[3:])
    
    def test_strip_end_multiple(self):
        pause = Pause(beg=1.25, end=1.95)
        invalid = Word('', 1.95, None)
        zero = Word('', 1.95, 1.95)
        utt_strip = Utterance(self.words + [pause, invalid, zero])

        utt_strip.strip()

        for entry in {pause, invalid, zero}:
            assert_not_in(entry, utt_strip)

        assert_equal(utt_strip.words(), self.words)

    def test_strip_pause_only(self):
        pause = Pause(beg=1.25, end=1.95)
        utt_strip = Utterance([pause])
        
        utt_strip.strip()
        
        assert_equal(utt_strip.words(), [])

    def test_update_timestamps(self):
        self.empty_utt.update_timestamps()

        assert_is_none(self.empty_utt.beg)
        assert_is_none(self.empty_utt.end)
        assert_is_none(self.empty_utt.dur)

        word = Word('the', 0.05, 0.25, ['dh', 'iy'], ['dh'], 'DT')
        na_beg = Word('the', 'n/a', 0.25, ['dh', 'iy'], ['dh'], 'DT')
        na_end = Word('the', 0.05, 'n/a', ['dh', 'iy'], ['dh'], 'DT')

        utt_u = Utterance()

        # bypass __init__ and append calls to update_timestamps()
        utt_u._Utterance__words = [word]
        utt_u.update_timestamps()
        assert_equal(utt_u.beg, 0.05)
        assert_equal(utt_u.end, 0.25)
        assert_equal(utt_u.dur, 0.25 - 0.05)

        utt_u._Utterance__words = [na_beg]
        utt_u.update_timestamps()
        assert_is_none(utt_u.beg)
        assert_equal(utt_u.end, 0.25)
        assert_is_none(utt_u.dur)

        utt_u._Utterance__words = [na_end]
        utt_u.update_timestamps()
        assert_equal(utt_u.beg, 0.05)
        assert_is_none(utt_u.end)
        assert_is_none(utt_u.dur)

    def test_repr(self):
        expected_repr = ("Utterance(["
                          "Word('the', 0.0, 0.1, ['dh', 'iy'], ['dh'], 'DT'), "
                          "Word('cat', 0.1, 0.39, ['k', 'ae', 't'], ['k', 'ae', 't'], 'NN'), "
                          "Word('is', 0.39, 0.55, ['ih', 'z'], ['ih', 'z'], 'VB'), "
                          "Word('on', 0.55, 0.73, ['aa', 'n'], ['aan'], 'IN'), "
                          "Word('the', 0.73, 0.8, ['dh', 'iy'], ['dh', 'uh'], 'DT'), "
                          "Word('mat', 0.8, 1.25, ['m', 'ae', 't'], ['m', 'ae', 't'], 'NN')"
                         "])")
        assert_equal(repr(self.utt), expected_repr)

    def test_str(self):
        assert_equal(str(self.utt), '<Utterance "the cat is on the mat">')
