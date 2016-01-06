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
