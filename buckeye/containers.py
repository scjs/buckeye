from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

SYLLABIC = {'aa', 'ae', 'ay', 'aw', 'ao', 'oy', 'ow', 'eh', 'ey', 'ah', 'uw',
            'uh', 'ih', 'iy', 'er', 'el', 'em', 'en', 'eng', 'aan', 'aen',
            'ayn', 'awn', 'aon', 'oyn', 'own', 'ehn', 'eyn', 'ahn', 'uwn',
            'uhn', 'ihn', 'iyn'}

class Word(object):
    """Container for data about one word (or similar entry) in a speech
    corpus.

    Arguments:
        orthography:    orthography of the word, or another label for
                        this entry
        beg:            timestamp where this word begins. Coerced to float, or
                        None if coercion fails.
        end:            timestamp where this word ends. Coerced to float, or
                        None if coercion fails.
        phonemic:       ordered iterable with the segments in the word's
                        dictionary or citation form. Defaults to None.
        phonetic:       ordered iterable with the segments in a close
                        phonetic transcription of the word. Defaults to
                        None.
        pos:            part of speech of the word. Defaults to None.

    Properties:
        All arguments are stored as read-only properties, in addition to
        the following.

        dur:            time from the beginning to the end of this word,
                        or None if the duration cannot be calculated
        phones:         defaults to None, but may be set to an ordered
                        iterable containing Phone instances that match
                        the segments in this word's phonetic property
        misaligned:     True if `dur' is negative, or if the `seg'
                        properties of the Phone instances in `phones'
                        do not match the word's `phonetic' property.
                        Otherwise False.
    """

    def __init__(self, orthography, beg, end,
                 phonemic=None, phonetic=None, pos=None):
        self.__orthography = orthography

        try:
            self.__beg = float(beg)
        except (TypeError, ValueError):
            self.__beg = None

        try:
            self.__end = float(end)
        except (TypeError, ValueError):
            self.__end = None

        self.__phonemic = phonemic
        self.__phonetic = phonetic
        self.__pos = pos

        self.phones = None

    def __repr__(self):
        return 'Word({}, {}, {}, {}, {}, {})'.format(repr(self.orthography),
                                                     self.beg, self.end,
                                                     repr(self.phonemic),
                                                     repr(self.phonetic),
                                                     repr(self.pos))

    def __str__(self):
        return '<Word "{}" at {}>'.format(self.orthography, self.beg)

    @property
    def orthography(self):
        return self.__orthography

    @property
    def phonemic(self):
        return self.__phonemic

    @property
    def phonetic(self):
        return self.__phonetic

    @property
    def pos(self):
        return self.__pos

    @property
    def misaligned(self):
        if self.dur is not None and self.dur < 0:
            return True

        if self.phones is None:
            return False

        if self.__phonetic is None:
            return True

        if len(self.phones) != len(self.__phonetic):
            return True

        for i, j in zip(self.phones, self.__phonetic):
            if i.seg != j:
                return True

        return False

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

    def syllables(self, phonetic=False):
        """Returns the number of syllabic segments in the Word.

        Arguments:
            phonetic:   if True, returns the number of syllabic
                        segments in the phones attribute (if defined,
                        else uses the phonetic attribute). Defaults to
                        False, which uses the number of syllabic
                        segments in the phonemic attribute instead.

        Returns:
            Integer number of syllabic segments in the specified
            transcription attribute.
        """

        if phonetic:
            if self.phones is not None:
                transcription = [phone.seg for phone in self.phones]

            else:
                transcription = self.__phonetic

        else:
            transcription = self.__phonemic

        try:
            return sum(1 for seg in transcription if seg in SYLLABIC)

        except TypeError:
            return None


class Pause(object):
    """Container for data about one pause (such as a silence, breath, laugh,
    or speech error) in a speech corpus.

    Arguments:
        entry:          label for this entry. Defaults to None.
        beg:            timestamp where this entry begins. Coerced to float,
                        or None if coercion fails. Defaults to None.
        end:            timestamp where this entry ends. Coerced to float, or
                        None if coercion fails. Defaults to None.

    Properties:
        All arguments are stored as read-only properties, in addition to
        the following.

        dur:            time from the beginning to the end of this pause,
                        or None if the duration cannot be calculated
        phones:         defaults to None, but may be set to an ordered
                        iterable containing Phone instances
        misaligned:     True if `dur' is negative, otherwise False.
    """

    def __init__(self, entry=None, beg=None, end=None):
        self.__entry = entry

        try:
            self.__beg = float(beg)
        except (TypeError, ValueError):
            self.__beg = None

        try:
            self.__end = float(end)
        except (TypeError, ValueError):
            self.__end = None

        self.phones = None

    def __repr__(self):
        return 'Pause({}, {}, {})'.format(repr(self.entry), self.beg, self.end)

    def __str__(self):
        return '<Pause {} at {}>'.format(self.entry, self.beg)

    @property
    def entry(self):
        return self.__entry

    @property
    def misaligned(self):
        if self.dur < 0:
            return True

        return False

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


class LogEntry(object):
    """Container for data about one log entry (such as transcriber
    confidence or a phonation annotation) in a speech corpus.

    Arguments:
        entry:          label for this entry
        beg:            timestamp where this entry begins. Defaults to None.
        end:            timestamp where this entry ends. Defaults to None.

    Properties:
        All arguments are stored as read-only properties.
    """

    def __init__(self, entry, beg=None, end=None):
        self.__entry = entry

        try:
            self.__beg = float(beg)
        except (TypeError, ValueError):
            self.__beg = None

        try:
            self.__end = float(end)
        except (TypeError, ValueError):
            self.__end = None

    def __repr__(self):
        return 'LogEntry({}, {}, {})'.format(repr(self.entry),
                                             self.beg, self.end)

    def __str__(self):
        return '<Log "{}" at {}>'.format(self.entry, self.beg)

    @property
    def entry(self):
        return self.__entry

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


class Phone(object):
    """Container for data about one segment in a speech corpus.

    Arguments:
        seg:            transcription label for this segment
        beg:            timestamp where this segment begins. Coerced to float,
                        or None if coercion fails. Defaults to None.
        end:            timestamp where this segment ends. Coerced to float,
                        or None if coercion fails. Defaults to None.

    Propreties:
        All arguments are stored as read-only properties, in addition to
        the following.

        dur:            difference between the beg and end timestamps
                        for this segment, or None if the duration cannot
                        be calculated
    """

    def __init__(self, seg, beg=None, end=None):
        self.__seg = seg

        try:
            self.__beg = float(beg)
        except (TypeError, ValueError):
            self.__beg = None

        try:
            self.__end = float(end)
        except (TypeError, ValueError):
            self.__end = None

    def __repr__(self):
        return 'Phone({}, {}, {})'.format(repr(self.seg), self.beg, self.end)

    def __str__(self):
        return '<Phone [{}] at {}>'.format(self.seg, self.beg)

    @property
    def seg(self):
        return self.__seg

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
