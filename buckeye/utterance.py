from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .containers import Word, Pause


class Utterance(object):
    """Container for a list of entries, such as Word and Pause instances,
    that make up an utterance in the speech corpus.

    Arguments:
        words:      optional ordered iterable of Word and Pause instances.
                    Entries can also be appended individually using the
                    append() method.

    Properties:
        beg:        beginning time of the first word in the utterance
        end:        ending time of the last word in the utterance
        dur:        time from the beginning to the end of the utterance,
                    or None if the duration cannot be calculated
    """

    def __init__(self, words=None):
        self.__beg = None
        self.__end = None

        self.__previous = 0.0

        if words is None:
            self.__words = []

        else:
            for word in words:
                self.__check_word_timestamps(word)

                if word.end is not None:
                    self.__previous = word.end

                elif word.beg is not None:
                    self.__previous = word.beg

            self.__words = words
            self.update_timestamps()

    def __repr__(self):
        return 'Utterance({})'.format(repr(self.words()))

    def __str__(self):
        utt = []

        for word in self.__words:
            if hasattr(word, 'orthography'):
                utt.append(word.orthography)

            else:
                utt.append(word.entry)

        return '<Utterance "{}">'.format(' '.join(utt))

    @property
    def beg(self):
        return self.__beg

    @property
    def end(self):
        return self.__end

    @property
    def dur(self):
        try:
            return self.__end - self.__beg

        except TypeError:
            return None

    def words(self):
        return self.__words

    def __check_word_timestamps(self, word):
        if not hasattr(word, 'beg') or not hasattr(word, 'end'):
            raise TypeError('object must have beg and end attributes'
                            ' to append to Utterance')

        if word.beg is not None and word.beg < self.__previous:
            raise ValueError('Word beg timestamp: {0} is before last '
                             'Utterance timestamp: {1}'
                             .format(str(word.beg), str(self.__previous)))

        if word.end is not None and word.end < self.__previous:
            raise ValueError('Word end timestamp: {0} is before last '
                             'Utterance timestamp: {1}'
                             .format(str(word.end), str(self.__previous)))

        if (word.end is not None and word.beg is not None and
                word.beg > word.end):
            raise ValueError('Word beg timestamp: {0} is after Word '
                             'end timestamp: {1}'
                             .format(str(word.beg), str(word.end)))

    def append(self, word):
        """Appends an instance to the list of entries in this utterance, and
        updates the utterance `beg', `end', and `dur' properties.
        """

        self.__check_word_timestamps(word)
        self.__words.append(word)

        if word.end is not None:
            self.__previous = word.end

        elif word.beg is not None:
            self.__previous = word.beg

        self.update_timestamps()

    def __iter__(self):
        return iter(self.__words)

    def __getitem__(self, i):
        return self.__words[i]

    def __len__(self):
        return len(self.__words)

    def speech_rate(self, use_phonetic=True, no_syllables='raise'):
        """Returns the number of syllabic segments per second in this
        utterance.

        There may be pauses at the beginning or end of an utterance
        that you do not want to include when calculating the speech
        rate of the utterance. To ignore any pauses at the beginning
        or end, use `no_syllables='squeeze'`. To remove them from the
        utterance, use `utterance.strip()`.

        Arguments:
            use_phonetic:   if True, this method counts syllables in each
                            entry's phonetic transcription, using the
                            `phones` or `phonetic` attribute. If False,
                            this method counts syllables in each
                            entry's `phonemic' attribute instead.
                            Defaults to True.

            no_syllables:   must be one of `'zero'`, `'squeeze'`, or
                            `'raise'`. Defaults to `'raise'`.

                            If `'zero'`, any instances in the utterance
                            without a `syllables` attribute are treated
                            as having zero syllables for the speech
                            rate calculation.

                            If `'squeeze`', the same behavior as
                            `'zero'`, plus any instances at the
                            beginning or end of the utterance with no
                            `syllables` attribute are ignored while
                            summing the total utterance duration.

                            If `'raise'`, a ValueError is raised if the
                            utterance includes any instances without a
                            `syllables` attribute.
        """

        if no_syllables not in {'zero', 'squeeze', 'raise'}:
            raise ValueError('"no_syllables" argument must be one of "zero", '
                             '"squeeze", or "raise"')

        if self.dur is None:
            raise TypeError('cannot calculate speech rate if Utterance '
                            'duration is None')

        if not self.__words:
            return 0.0

        syllable_count = 0

        for word in self.__words:
            if hasattr(word, 'syllables'):
                syllable_count += word.syllables(use_phonetic)

            elif no_syllables == 'raise':
                raise ValueError('all objects in Utterance must have a '
                                 '"syllables" attribute to calculate speech '
                                 'rate')

        if no_syllables == 'squeeze':
            beg = next(word.beg for word in self.__words
                       if hasattr(word, 'syllables'))

            end = next(word.end for word in reversed(self.__words)
                       if hasattr(word, 'syllables'))

            return float(syllable_count) / float(end - beg)

        else:
            return float(syllable_count) / float(self.dur)

    def strip(self):
        """Strips all non-Word instances, or Word instances where the
        duration is not positive, from the left and right edges of the
        list of entries in this Utterance instance.
        """

        try:
            left = next(i for i in self
                        if isinstance(i, Word) and
                        i.dur is not None and i.dur > 0)

            right = next(i for i in reversed(self.__words)
                         if isinstance(i, Word) and
                         i.dur is not None and i.dur > 0)

            left_idx = self.__words.index(left)
            right_idx = self.__words.index(right) + 1

            self.__words = self.__words[left_idx:right_idx]

        except StopIteration:
            self.__words = []

        self.update_timestamps()

        return self

    def update_timestamps(self):
        """Resets the `beg' and `end' properties of this Utterance instance
        to the beginning timestamp of the first entry and the ending
        timestamp of the final entry, respectively. If a timestamp is None, or
        if there are no entries in the list, `beg' and/or `end' will be set to
        None instead. This method also resets the `dur' property of the
        Utterance instance based on the new `beg' and `end' values.
        """

        try:
            self.__beg = self.__words[0].beg
            self.__end = self.__words[-1].end
        except IndexError:
            self.__beg = None
            self.__end = None

        return self


def words_to_utterances(words, sep=0.5):
    """Generator that takes an iterable of Word and Pause instances, such as
    process_words(), and packs them into Utterance instances.

    A new Utterance is created at the start of the iterable passed to
    words_to_utterances(), and then whenever there is a sequence of Pause
    instances that add up to `sep` seconds or more of duration.

    Arguments:
        words:      iterable of Word and Pause instances
        sep:        if more than `sep` seconds of Pause instances occur
                    consecutively, yield the current Utterance instance
                    and begin a new one. Defaults to 0.5.

    Yields:
        Utterance instances for each sequence of word entries delimited by
        >= `sep` seconds (default 0.5) of Pause instances. Pause instances, or
        Word instances with invalid timestamps, are stripped from the
        beginning and end of the words list belonging to each yielded
        Utterance.
    """

    utt = Utterance()
    pause_duration = 0.0
    pause = False

    for word in words:
        # if this item is a pause token (or a bad Word entry)...
        if isinstance(word, Pause) or not word.phonetic:

            # skip it if there are no words in the utterance yet
            if len(utt) == 0:
                continue

            # if this item doesn't follow another pause, restart the
            # pause duration
            if not pause:
                pause_duration = word.dur

            # otherwise, add it to the cumulative pause duration
            else:
                pause_duration += word.dur

            pause = True

        else:
            pause = False

        utt.append(word)

        # if the total pause duration has reached `sep` seconds, return this
        # utterance and start a new one
        if pause_duration >= sep:
            yield utt.strip()

            utt = Utterance()
            pause_duration = 0.0

    # return the last utterance if there is one
    if len(utt) > 0:
        yield utt.strip()
