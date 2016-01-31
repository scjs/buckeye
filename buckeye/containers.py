"""Classes to store and manipulate entries in the Buckeye Corpus.

References
----------
Pitt, M.A., Dilley, L., Johnson, K., Kiesling, S., Raymond, W., Hume, E.
 and Fosler-Lussier, E. (2007) Buckeye Corpus of Conversational Speech
 (2nd release) [www.buckeyecorpus.osu.edu] Columbus, OH: Department of
 Psychology, Ohio State University (Distributor).

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


SYLLABIC = {'aa', 'ae', 'ay', 'aw', 'ao', 'oy', 'ow', 'eh', 'ey', 'ah', 'uw',
            'uh', 'ih', 'iy', 'er', 'el', 'em', 'en', 'eng', 'aan', 'aen',
            'ayn', 'awn', 'aon', 'oyn', 'own', 'ehn', 'eyn', 'ahn', 'uwn',
            'uhn', 'ihn', 'iyn'}


class Word(object):
    """A word entry in the Buckeye Corpus.

    Parameters
    ----------
    orthography : str
        Written form of the word, or another label for this entry.

    beg : float
        Timestamp where the word begins.

    end : float
        Timestamp where the word ends.

    phonemic : list of str, optional
        Transcription of the word's dictionary or citation form. Default
        is None.

    phonetic : list of str, optional
        Close phonetic transcription of the word. Default is None.

    pos : str, optional
        Part of speech. Default is None.

    Attributes
    ----------
    orthography
    beg
    end
    phonemic
    phonetic
    pos
    dur
    phones
    misaligned

    """

    def __init__(self, orthography, beg, end,
                 phonemic=None, phonetic=None, pos=None):
        self._orthography = orthography
        self._beg = beg
        self._end = end
        self._phonemic = phonemic
        self._phonetic = phonetic
        self._pos = pos

        self._phones = None

    def __repr__(self):
        return 'Word({}, {}, {}, {}, {}, {})'.format(repr(self._orthography),
                                                     self._beg, self._end,
                                                     repr(self._phonemic),
                                                     repr(self._phonetic),
                                                     repr(self._pos))

    def __str__(self):
        return '<Word "{}" at {}>'.format(self._orthography, self._beg)

    @property
    def orthography(self):
        """Written form of the word, or another label for this entry."""
        return self._orthography

    @property
    def phonemic(self):
        """Transcription of the word's dictionary or citation form."""
        return self._phonemic

    @property
    def phones(self):
        """List of Phone instances that correspond to the word."""
        return self._phones

    @property
    def phonetic(self):
        """Close phonetic transcription of the word."""
        return self._phonetic

    @property
    def pos(self):
        """Part of speech."""
        return self._pos

    @property
    def misaligned(self):
        """A flag for whether there is an obvious issue with the
        time-alignment of this word. True if `dur` can be calculated but
        is negative, or if the Phones that correspond to this word's
        timestamps don't match up with the given close phonetic
        transcription in `phonetic`. Otherwise False."""

        if self.dur is not None and self.dur < 0:
            return True

        if self._phones is None:
            return False

        if self._phonetic is None:
            return True

        if len(self._phones) != len(self._phonetic):
            return True

        for i, j in zip(self._phones, self._phonetic):
            if i.seg != j:
                return True

        return False

    @property
    def beg(self):
        """Timestamp where the word begins."""
        return self._beg

    @property
    def end(self):
        """Timestamp where the word ends."""
        return self._end

    @property
    def dur(self):
        """Duration of the word."""
        try:
            return self._end - self._beg

        except TypeError:
            raise AttributeError('Duration is not available if beg and end '
                                 'are not numeric types')

    def syllables(self, phonetic=False):
        """Return the number of syllabic segments in the word.

        Syllabic segments are listed in `buckeye.containers.SYLLABIC`.

        Parameters
        ----------
        phonetic : bool, optional
            If True, the number of syllabic segments in the `phones`
            attribute is returned. (If `phones` is None, the `phonetic`
            attribute is used.) If False, the number of syllabic
            segments in the `phonemic` attribute is returned instead.
            Default is False.

        Returns
        -------
        syllables : int
            The number of syllabic segments in the specified attribute.

        """

        if phonetic:
            if self._phones is not None:
                transcription = [phone.seg for phone in self._phones]

            else:
                transcription = self._phonetic

        else:
            transcription = self._phonemic

        try:
            return sum(1 for seg in transcription if seg in SYLLABIC)

        except TypeError:
            return None


class Pause(object):
    """A non-speech entry in the Buckeye Corpus.

    Some kinds of non-speech entries are: silences, breaths, laughs,
    speech errors, the beginning or end of a track, or others. These are
    all indicated with `{}` or `<>` braces in the transcription file.

    Parameters
    ----------
    entry : str, optional
        A written label for this entry, such as `<SIL>` for a silence.
        Default is None.

    beg : float, optional
        Timestamp where the entry begins. Default is None.

    end : float, optional
        Timestamp where the entry ends. Default is None

    Attributes
    ----------
    entry
    beg
    end
    phones
    dur
    misaligned

    """

    def __init__(self, entry=None, beg=None, end=None):
        self._entry = entry
        self._beg = beg
        self._end = end

        self._phones = None

    def __repr__(self):
        return 'Pause({}, {}, {})'.format(repr(self._entry), self._beg, self._end)

    def __str__(self):
        return '<Pause {} at {}>'.format(self._entry, self._beg)

    @property
    def entry(self):
        """Written label for this entry."""
        return self._entry

    @property
    def misaligned(self):
        """A flag for whether there is an obvious issue with the
        time-alignment of this entry. True if `dur` can be calculated but
        is negative. Otherwise False."""
        if self.dur is not None and self.dur < 0:
            return True

        return False

    @property
    def phones(self):
        """List of Phone instances that correspond to the pause."""
        return self._phones

    @property
    def beg(self):
        """Timestamp where the entry begins."""
        return self._beg

    @property
    def end(self):
        """Timestamp where the entry ends."""
        return self._end

    @property
    def dur(self):
        """Duration of the entry."""
        try:
            return self._end - self._beg

        except TypeError:
            raise AttributeError('Duration is not available if beg and end '
                                 'are not numeric types')


class LogEntry(object):
    """A log entry in the Buckeye Corpus, such as transcriber confidence.

    Parameters
    ----------
    entry : str
        A written label for this entry, such as `<VOICE=creaky>`.

    beg : float, optional
        Timestamp where the entry begins. Default is None.

    end : float, optional
        Timestamp where the entry ends. Default is None.

    Attributes
    ----------
    entry
    beg
    end

    """

    def __init__(self, entry, beg=None, end=None):
        self._entry = entry
        self._beg = beg
        self._end = end

    def __repr__(self):
        return 'LogEntry({}, {}, {})'.format(repr(self._entry),
                                             self._beg, self._end)

    def __str__(self):
        return '<Log "{}" at {}>'.format(self._entry, self._beg)

    @property
    def entry(self):
        """Written label for this entry."""
        return self._entry

    @property
    def beg(self):
        """Timestamp where the entry begins."""
        return self._beg

    @property
    def end(self):
        """Timestamp where the entry ends."""
        return self._end

    @property
    def dur(self):
        """Duration of the entry."""
        try:
            return self._end - self._beg

        except TypeError:
            raise AttributeError('Duration is not available if beg and end '
                                 'are not numeric types')


class Phone(object):
    """A phone entry in the Buckeye Corpus.

    Parameters
    ----------
    seg : str
        Label for the phone (pseudo-ARPABET in the Buckeye Corpus).

    beg : float, optional
        Timestamp where the phone begins. Default is None.

    end : float, optional
        Timestamp where the phone ends. Default is None.

    Attributes
    ----------
    beg
    end
    dur

    """

    def __init__(self, seg, beg=None, end=None):
        self._seg = seg
        self._beg = beg
        self._end = end

    def __repr__(self):
        return 'Phone({}, {}, {})'.format(repr(self._seg), self._beg, self._end)

    def __str__(self):
        return '<Phone [{}] at {}>'.format(self._seg, self._beg)

    @property
    def seg(self):
        """Label for this phone (e.g., using ARPABET transcription)."""
        return self._seg

    @property
    def beg(self):
        """Timestamp where the phone begins."""
        return self._beg

    @property
    def end(self):
        """Timestamp where the phone ends."""
        return self._end

    @property
    def dur(self):
        """Duration of the phone."""
        try:
            return self._end - self._beg

        except TypeError:
            raise AttributeError('Duration is not available if beg and end '
                                 'are not numeric types')
