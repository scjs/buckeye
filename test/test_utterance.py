from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from nose.tools import *

from buckeye.containers import Word, Pause
from buckeye.utterance import Utterance
from buckeye.utterance import words_to_utterances


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
        assert_equal(self.utt.words, self.words)

    @raises(AttributeError)
    def test_empty_beg(self):
        self.empty_utt.beg

    @raises(AttributeError)
    def test_empty_end(self):
        self.empty_utt.end

    @raises(AttributeError)
    def test_empty_dur(self):
        self.empty_utt.dur

    def test_empty_words(self):
        assert_equal(self.empty_utt.words, [])

    def test_backwards_utterance(self):
        utt_backwards = Utterance(self.words[::-1])
        assert_equal(utt_backwards._words, self.words)

    @raises(ValueError)
    def test_flipped_word(self):
        word = Word('the', 0.10, 0, ['dh', 'iy'], ['dh'], 'DT')
        utt = Utterance([word])

    @raises(ValueError)
    def test_overlapping_words(self):
        words = [
            Word('the', 0, 0.10, ['dh', 'iy'], ['dh'], 'DT'),
            Word('cat', 0.05, 0.39, ['k', 'ae', 't'], ['k', 'ae', 't'], 'NN')]

        utt = Utterance(words)

    def test_append(self):
        utt_a = Utterance()

        word = Word('the', 0.05, 0.25, ['dh', 'iy'], ['dh'], 'DT')
        utt_a.append(word)

        assert_equal(utt_a.words, [word])
        assert_equal(utt_a.beg, 0.05)
        assert_equal(utt_a.end, 0.25)
        assert_equal(utt_a.dur, 0.25 - 0.05)

        uh = Word('uh', 0.25, 0.45, ['ah'], ['ah'], 'UH')
        utt_a.append(uh)

        assert_equal(utt_a.words, [word, uh])
        assert_equal(utt_a.beg, 0.05)
        assert_equal(utt_a.end, 0.45)
        assert_equal(utt_a.dur, 0.45 - 0.05)

    @raises(AttributeError)
    def test_append_missing(self):
        self.empty_utt.append('the')

    @raises(ValueError)
    def test_append_overlap(self):
        word = Word('uh', 0.25, 0.45, ['ah'], ['ah'], 'UH')
        self.utt.append(word)

    @raises(TypeError)
    def test_append_beg_none(self):
        word = Word('uh', None, 0.45, ['ah'], ['ah'], 'UH')
        self.utt.append(word)

    @raises(TypeError)
    def test_append_end_none(self):
        word = Word('uh', 0.25, None, ['ah'], ['ah'], 'UH')
        self.utt.append(word)

    @raises(ValueError)
    def test_append_backwards(self):
        word = Word('uh', 1.95, 1.65, ['ah'], ['ah'], 'UH')
        self.empty_utt.append(word)

    def test_append_none(self):
        word = Word('the', 0.05, 0.25, ['dh', 'iy'], ['dh'], 'DT')
        utt_append_none = Utterance([word])

        none_word = Word('uh', None, None, ['ah'], ['ah'], 'UH')
        assert_raises(TypeError, utt_append_none.append, none_word)

        none_beg_word = Word('uh', None, 0.5, ['ah'], ['ah'], 'UH')
        assert_raises(TypeError, utt_append_none.append, none_beg_word)

        none_end_word = Word('uh', 0.65, None, ['ah'], ['ah'], 'UH')
        assert_raises(TypeError, utt_append_none.append, none_end_word)

    def test_len(self):
        assert_equal(len(self.utt), 6)

    def test_speech_rate(self):
        assert_equal(self.utt.speech_rate(), 4.0)
        assert_equal(self.utt.speech_rate(use_phonetic=False), 4.8)

    def test_speech_rate_empty(self):
        assert_raises(ValueError, self.empty_utt.speech_rate)
        assert_raises(ValueError, self.empty_utt.speech_rate, False)

    def test_speech_rate_pause_at_beg_raise(self):
        words = [Pause(beg=0, end=0.39)] + self.words[2:]
        utt = Utterance(words)

        assert_raises(ValueError, utt.speech_rate)

    def test_speech_rate_pause_at_beg_ignore(self):
        words = [Pause(beg=0, end=0.39)] + self.words[2:]
        utt = Utterance(words)

        assert_equal(utt.speech_rate(ignore_missing_syllables=True), 3.2)

    def test_speech_rate_pause_at_beg_and_middle_raise(self):
        words = [Pause(beg=0, end=0.39)] + self.words[2:]
        words[2] = Pause(beg=0.55, end=0.73)
        utt = Utterance(words)

        assert_raises(ValueError, utt.speech_rate)

    def test_speech_rate_pause_at_beg_and_middle_ignore(self):
        words = [Pause(beg=0, end=0.39)] + self.words[2:]
        words[2] = Pause(beg=0.55, end=0.73)
        utt = Utterance(words)

        assert_equal(utt.speech_rate(ignore_missing_syllables=True), 2.4)

    def test_speech_rate_pause_at_end_raise(self):
        utt = Utterance(self.words)
        utt.append(Pause(beg=1.25, end=1.50))

        assert_raises(ValueError, utt.speech_rate)

    def test_speech_rate_pause_at_end_ignore(self):
        utt = Utterance(self.words)
        utt.append(Pause(beg=1.25, end=1.50))

        assert_equal(utt.speech_rate(ignore_missing_syllables=True), 10/3)

    def test_speech_rate_pause_at_end_and_middle_raise(self):
        words = self.words + [Pause(beg=1.25, end=1.50)]
        words[-3] = Pause(beg=0.73, end=0.80)
        utt = Utterance(words)

        assert_raises(ValueError, utt.speech_rate)

    def test_speech_rate_pause_at_end_and_middle_ignore(self):
        words = self.words + [Pause(beg=1.25, end=1.50)]
        words[-3] = Pause(beg=0.73, end=0.80)

        utt = Utterance(words)
        assert_equal(utt.speech_rate(ignore_missing_syllables=True), 8/3)

    def test_repr(self):
        expected_repr = ("Utterance(["
                         "Word('the', 0, 0.1, ['dh', 'iy'], ['dh'], 'DT'), "
                         "Word('cat', 0.1, 0.39, ['k', 'ae', 't'], ['k', 'ae', 't'], 'NN'), "
                         "Word('is', 0.39, 0.55, ['ih', 'z'], ['ih', 'z'], 'VB'), "
                         "Word('on', 0.55, 0.73, ['aa', 'n'], ['aan'], 'IN'), "
                         "Word('the', 0.73, 0.8, ['dh', 'iy'], ['dh', 'uh'], 'DT'), "
                         "Word('mat', 0.8, 1.25, ['m', 'ae', 't'], ['m', 'ae', 't'], 'NN')"
                         "])")
        assert_equal(repr(self.utt), expected_repr)

    def test_str(self):
        assert_equal(str(self.utt), '<Utterance "the cat is on the mat">')

    def test_str_pause(self):
        utt = Utterance(self.words)
        utt.append(Pause('VOCNOISE', 1.25, 1.50))

        assert_equal(str(utt), '<Utterance "the cat is on the mat VOCNOISE">')

    def test_str_other(self):
        utt = Utterance(self.words)

        class CompatibleWord(object):
            def __init__(self):
                self.beg = 1.25
                self.end = 1.5

            def __str__(self):
                return '<CompatibleWord object>'

        utt.append(CompatibleWord())

        expected = '<Utterance "the cat is on the mat <CompatibleWord object>">'
        assert_equal(str(utt), expected)

class TestWordsToUtterances(object):

    @classmethod
    def setup_class(cls):
        cls.words = [Word('the', 0.05, 0.15, ['dh', 'iy'], ['dh', 'ah']),
                     Word('cat', 0.15, 0.44, ['k', 'ae', 't'], ['k', 'ae', 't']),
                     Word('is', 0.44, 0.59, ['ih', 'z'], ['ih', 'z']),
                     Word('on', 0.59, 0.77, ['aa', 'n'], ['aa', 'n']),
                     Word('the', 0.77, 0.91, ['dh', 'iy'], ['dh', 'ah']),
                     Word('mat', 0.91, 1.19, ['m', 'ae', 't'], ['m', 'ae', 't'])]

    def check_expected_with_defaults(self, utterances):
        assert_equal(len(utterances), 1)

        for i, word in enumerate(utterances[0]):
            assert_equal(self.words[i].beg, word.beg)
            assert_equal(self.words[i].end, word.end)
            assert_equal(self.words[i].orthography, word.orthography)
            assert_equal(self.words[i].phonemic, word.phonemic)
            assert_equal(self.words[i].phonetic, word.phonetic)

    def test_words_to_utterances(self):
        utterances = list(words_to_utterances(self.words))

        yield self.check_expected_with_defaults, utterances

    def test_initial_pause(self):
        initial_pause = Pause('<SIL>', 0.0, 0.05)
        utterances = list(words_to_utterances([initial_pause] + self.words))

        yield self.check_expected_with_defaults, utterances

    def test_initial_pause_no_strip(self):
        initial_pause = Pause('<SIL>', 0.0, 0.05)
        words = [initial_pause] + self.words

        utterances = list(words_to_utterances(words, strip_pauses=False))

        assert_equal(len(utterances), 1)
        assert_equal(len(utterances[0]), 7)

        for i, word in enumerate(utterances[0]):
            assert_equal(words[i].beg, word.beg)
            assert_equal(words[i].end, word.end)

    def test_final_pause(self):
        final_pause = Pause('<SIL>', 1.19, 1.25)
        utterances = list(words_to_utterances(self.words + [final_pause]))

        yield self.check_expected_with_defaults, utterances

    def test_final_pause_no_strip(self):
        final_pause = Pause('<SIL>', 1.19, 1.25)
        words = self.words + [final_pause]

        utterances = list(words_to_utterances(words, strip_pauses=False))

        assert_equal(len(utterances), 1)
        assert_equal(len(utterances[0]), 7)

        for i, word in enumerate(utterances[0]):
            assert_equal(words[i].beg, word.beg)
            assert_equal(words[i].end, word.end)

    def test_medial_pause(self):
        # insert a pause into a copy of the word list
        words = self.words[:]
        words[5:] = [Pause('<SIL>', 0.91, 1.42),
                     Word('mat', 1.42, 1.7, ['m', 'ae', 't'], ['m', 'ae', 't'])]

        utterances = list(words_to_utterances(words))

        assert_equal(len(utterances), 2)
        assert_equal(len(utterances[0]), 5)
        assert_equal(len(utterances[1]), 1)

        for i, word in enumerate(utterances[0]):
            assert_equal(words[i].beg, word.beg)
            assert_equal(words[i].end, word.end)

        assert_equal(words[6].beg, utterances[1][0].beg)
        assert_equal(words[6].end, utterances[1][0].end)
        assert_equal(words[6].orthography, utterances[1][0].orthography)
        assert_equal(words[6].phonemic, utterances[1][0].phonemic)
        assert_equal(words[6].phonetic, utterances[1][0].phonetic)

    def test_medial_pause_no_strip(self):
        # insert a pause into a copy of the word list
        words = self.words[:]
        words[5:] = [Pause('<SIL>', 0.91, 1.42),
                     Word('mat', 1.42, 1.7, ['m', 'ae', 't'], ['m', 'ae', 't'])]

        utterances = list(words_to_utterances(words, strip_pauses=False))

        assert_equal(len(utterances), 2)
        assert_equal(len(utterances[0]), 6)
        assert_equal(len(utterances[1]), 1)

        for i, word in enumerate(utterances[0]):
            assert_equal(words[i].beg, word.beg)
            assert_equal(words[i].end, word.end)

    def test_short_medial_pause(self):
        words = self.words[:]
        words[5:] = [Pause('<SIL>', 0.91, 1.0),
                     Word('mat', 1.0, 1.28, ['m', 'ae', 't'], ['m', 'ae', 't'])]

        utterances = list(words_to_utterances(words))

        assert_equal(len(utterances), 1)
        assert_equal(words[5].entry, utterances[0][5].entry)

        for i, word in enumerate(utterances[0]):
            assert_equal(words[i].beg, word.beg)
            assert_equal(words[i].end, word.end)

    def test_multiple_medial_pauses(self):
        words = self.words[:]
        words[5:] = [Pause('<SIL>', 0.91, 1.0),
                     Pause('<SIL>', 1.0, 1.42),
                     Word('mat', 1.42, 1.7, ['m', 'ae', 't'], ['m', 'ae', 't'])]

        utterances = list(words_to_utterances(words))

        assert_equal(len(utterances), 2)
        assert_equal(len(utterances[0]), 5)
        assert_equal(len(utterances[1]), 1)

        for i, word in enumerate(utterances[0]):
            assert_equal(words[i].beg, word.beg)
            assert_equal(words[i].end, word.end)
            assert_equal(words[i].orthography, word.orthography)
            assert_equal(words[i].phonemic, word.phonemic)
            assert_equal(words[i].phonetic, word.phonetic)

        for i, word in enumerate(utterances[1], 7):
            assert_equal(words[i].beg, word.beg)
            assert_equal(words[i].end, word.end)
            assert_equal(words[i].orthography, word.orthography)
            assert_equal(words[i].phonemic, word.phonemic)
            assert_equal(words[i].phonetic, word.phonetic)

    def test_multiple_medial_pauses_no_strip(self):
        words = self.words[:]
        words[5:] = [Pause('<SIL>', 0.91, 1.0),
                     Pause('<SIL>', 1.0, 1.42),
                     Word('mat', 1.42, 1.7, ['m', 'ae', 't'], ['m', 'ae', 't'])]

        utterances = list(words_to_utterances(words, strip_pauses=False))

        assert_equal(len(utterances), 2)
        assert_equal(len(utterances[0]), 7)
        assert_equal(len(utterances[1]), 1)

        for i, word in enumerate(utterances[0]):
            assert_equal(words[i].beg, word.beg)
            assert_equal(words[i].end, word.end)

        for i, word in enumerate(utterances[1], 7):
            assert_equal(words[i].beg, word.beg)
            assert_equal(words[i].end, word.end)

    def test_multiple_short_medial_pauses(self):
        words = self.words[:]
        words[3:] = [Pause('<VOCNOISE>', 0.59, 0.65),
                     Word('on', 0.65, 0.77, ['aa', 'n'], ['aa', 'n']),
                     self.words[4],
                     Pause('<SIL>', 0.91, 1.35),
                     Word('mat', 1.35, 1.63, ['m', 'ae', 't'], ['m', 'ae', 't'])]

        utterances = list(words_to_utterances(words))

        assert_equal(len(utterances), 1)
        assert_equal(words[3].entry, utterances[0][3].entry)
        assert_equal(words[6].entry, utterances[0][6].entry)

        for i, word in enumerate(utterances[0]):
            assert_equal(words[i].beg, word.beg)
            assert_equal(words[i].end, word.end)

    def test_sep_arg(self):
        words = self.words[:]
        words[5:] = [Pause('<SIL>', 0.91, 1.0),
                     Word('mat', 1.0, 1.28, ['m', 'ae', 't'], ['m', 'ae', 't'])]

        utterances = list(words_to_utterances(words, sep=0.08))

        assert_equal(len(utterances), 2)
        assert_equal(len(utterances[0]), 5)
        assert_equal(len(utterances[1]), 1)

        for i, word in enumerate(utterances[0]):
            assert_equal(words[i].beg, word.beg)
            assert_equal(words[i].end, word.end)
            assert_equal(words[i].orthography, word.orthography)
            assert_equal(words[i].phonemic, word.phonemic)
            assert_equal(words[i].phonetic, word.phonetic)

        assert_equal(words[6].beg, utterances[1][0].beg)
        assert_equal(words[6].end, utterances[1][0].end)
        assert_equal(words[6].orthography, utterances[1][0].orthography)
        assert_equal(words[6].phonemic, utterances[1][0].phonemic)
        assert_equal(words[6].phonetic, utterances[1][0].phonetic)
