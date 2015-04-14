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
        beg:            timestamp where this word begins
        end:            timestamp where this word ends
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
        self.__beg = beg
        self.__end = end
        self.__phonemic = phonemic
        self.__phonetic = phonetic
        self.__pos = pos

        self.__phones = None
        self.__misaligned = False

        try:
            self.__dur = self.__end - self.__beg
            if self.__dur < 0:
                self.__misaligned = True

        except TypeError:
            self.__dur = None

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
    def phones(self):
        return self.__phones

    @phones.setter
    def phones(self, phones):
        self.__phones = phones

        if self.__phonetic is None:
            self.__misaligned = True
        elif len(phones) != len(self.__phonetic):
            self.__misaligned = True
        else:
            for i, j in zip(phones, self.__phonetic):
                if i.seg != j:
                    self.__misaligned = True
                    break
            else:
                if self.__dur > 0 or self.__dur is None:
                    self.__misaligned = False

    @property
    def misaligned(self):
        return self.__misaligned

    @property
    def beg(self):
        return self.__beg

    @property
    def end(self):
        return self.__end

    @property
    def dur(self):
        return self.__dur

    def count_syllables(self, phonetic=False):
        """Returns the number of syllabic segments in the Word instance's
        phonemic attribute.

        Arguments:
            phonetic:   if True, returns the number of syllables in the
                        instance's phonetic attribute. Defaults to False.

        Returns:
            Integer number of syllabic segments in the specified
            transcription attribute.
        """

        if phonetic:
            transcription = self.__phonetic
        else:
            transcription = self.__phonemic

        syllables = 0

        try:
            for segment in transcription:
                if segment in SYLLABIC:
                    syllables += 1
        except TypeError:
            error = 'phonetic' if phonetic else 'phonemic'
            raise AttributeError('cannot count {0} syllables when iterable {0}'
                                 ' transcription is not defined'.format(error))

        return syllables


class Pause(object):
    """Container for data about one pause (such as a silence, breath, laugh,
    or speech error) in a speech corpus.

    Arguments:
        entry:          label for this entry. Defaults to None.
        beg:            timestamp where this entry begins. Defaults to None.
        end:            timestamp where this entry ends. Defaults to None.

    Properties:
        All arguments are stored as read-only properties.
    """

    def __init__(self, entry=None, beg=None, end=None):
        self.__entry = entry
        self.__beg = beg
        self.__end = end

    def __repr__(self):
        return 'Pause({}, {}, {})'.format(repr(self.entry), self.beg, self.end)

    def __str__(self):
        return '<Pause {} at {}>'.format(self.entry, self.beg)

    @property
    def entry(self):
        return self.__entry

    @property
    def beg(self):
        return self.__beg

    @property
    def end(self):
        return self.__end


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
        self.__beg = beg
        self.__end = end

        try:
            self.__dur = self.__end - self.__beg
        except TypeError:
            self.__dur = None

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
        return self.__dur


class Phone(object):
    """Container for data about one segment in a speech corpus.

    Arguments:
        seg:            transcription label for this segment
        beg:            timestamp where this segment begins. Defaults to None.
        end:            timestamp where this segment ends. Defaults to None.

    Propreties:
        All arguments are stored as read-only properties, in addition to
        the following.

        dur:            difference between the beg and end timestamps
                        for this segment, or None if the duration cannot
                        be calculated
    """

    def __init__(self, seg, beg=None, end=None):
        self.__seg = seg
        self.__beg = beg
        self.__end = end

        try:
            self.__dur = self.__end - self.__beg
        except TypeError:
            self.__dur = None

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
        return self.__dur


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

        if words is None:
            self.__words = []
        else:
            self.__words = words
            self.update_timestamps()

        try:
            self.__dur = self.__end - self.__beg
        except TypeError:
            self.__dur = None

    def __repr__(self):
        return 'Utterance({})'.format(repr(self.words()))

    def __str__(self):
        utt = ' '.join([word.orthography for word in self.words()])
        return '<Utterance "{}">'.format(utt)

    @property
    def beg(self):
        return self.__beg

    @property
    def end(self):
        return self.__end

    @property
    def dur(self):
        return self.__dur

    def words(self):
        """Returns the list of entries in this utterance"""

        return self.__words

    def append(self, word):
        """Appends an instance to the list of entries in this utterance,
        and updates the utterance `beg', `end', and `dur' properties.
        The instance must have a `beg' and `end' attribute to be appended.
        """

        if not (hasattr(word, 'beg') and hasattr(word, 'end')):
            raise TypeError('object must have beg and end attributes'
                            ' to append to Utterance')
        self.__words.append(word)
        self.update_timestamps()

    def __iter__(self):
        return iter(self.__words)

    def __getitem__(self, i):
        return self.__words[i]

    def __len__(self):
        return len(self.__words)

    def speech_rate(self, use_phonetic=True):
        """Returns the number of syllabic segments per second in this
        utterance. Before returning, the strip() method is called to
        remove Pause instances or words without a calculable duration
        from the beginning and end of the list of entries.

        Arguments:
            use_phonetic:   if True, this method counts syllables in each
                            entry's `phonetic' attribute. If False, this
                            method counts syllables in each entry's
                            `phonemic' attribute. Defaults to True.
        """

        if len(self.__words) == 0:
            return 0.0
        else:
            self.strip()
            utt_syllables = 0
            for word in self.__words:
                if type(word).__name__ == 'Word':
                    utt_syllables += word.count_syllables(phonetic=use_phonetic)

            return float(utt_syllables) / self.dur

    def strip(self):
        """Strips all non-Word instances, or Word instances where the
        duration is not positive, from the left and right edges of the
        list of entries in this Utterance instance.
        """

        left = next(i for i in self if type(i).__name__ == 'Word' and i.dur > 0)
        right = next(i for i in reversed(self.__words) if type(i).__name__ == 'Word' and i.dur > 0)

        left_idx = self.__words.index(left)
        right_idx = self.__words.index(right) + 1

        self.__words = self.__words[left_idx:right_idx]

        self.update_timestamps()

        return self

    def update_timestamps(self):
        """Resets the `beg' and `end' properties of this Utterance instance
        to the beginning timestamp of the first entry and the ending
        timestamp of the final entry, respectively. If a timestamp is not
        a float or an integer, or if there are no entries in the list,
        `beg' and/or `end' will be set to None instead. This method also
        resets the `dur' property of the Utterance instance based on the
        new `beg' and `end' values.
        """

        try:
            if type(self.__words[0].beg) in (float, int):
                self.__beg = self.__words[0].beg
            else:
                self.__beg = None
        except IndexError:
            self.__beg = None

        try:
            if type(self.__words[-1].end) in (float, int):
                self.__end = self.__words[-1].end
            else:
                self.__end = None
        except IndexError:
            self.__end = None

        try:
            self.__dur = self.__end - self.__beg
        except TypeError:
            self.__dur = None

        return self
