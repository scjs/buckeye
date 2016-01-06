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
    phones : list of Phone
        List of Phone instances with timestamps for the close phonetic
        transcription of the word.

    misaligned

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
        """Written form of the word, or another label for this entry."""
        return self.__orthography

    @property
    def phonemic(self):
        """Transcription of the word's dictionary or citation form."""
        return self.__phonemic

    @property
    def phonetic(self):
        """Close phonetic transcription of the word."""
        return self.__phonetic

    @property
    def pos(self):
        """Part of speech."""
        return self.__pos

    @property
    def misaligned(self):
        """A flag for whether there is an obvious issue with the
        time-alignment of this word. True if `dur` can be calculated but
        is negative, or if the Phones that correspond to this word's
        timestamps don't match up with the given close phonetic
        transcription in `phonetic`. Otherwise False."""

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
        """Timestamp where the word begins."""
        return self.__beg

    @property
    def end(self):
        """Timestamp where the word ends."""
        return self.__end

    @property
    def dur(self):
        """Duration of the word, or None if it cannot be calculated."""
        try:
            return self.__end - self.__beg

        except TypeError:
            return None

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
    phones : list of Phone
        List of Phone instances with timestamps for the close phonetic
        transcription of the word.
    dur
    misaligned

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
        """Written label for this entry."""
        return self.__entry

    @property
    def misaligned(self):
        """A flag for whether there is an obvious issue with the
        time-alignment of this entry. True if `dur` can be calculated but
        is negative. Otherwise False."""
        if self.dur is not None and self.dur < 0:
            return True

        return False

    @property
    def beg(self):
        """Timestamp where the entry begins."""
        return self.__beg

    @property
    def end(self):
        """Timestamp where the entry ends."""
        return self.__end

    @property
    def dur(self):
        """Duration of the entry, or None if it cannot be calculated."""
        try:
            return self.__end - self.__beg

        except TypeError:
            return None


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
        """Written label for this entry."""
        return self.__entry

    @property
    def beg(self):
        """Timestamp where the entry begins."""
        return self.__beg

    @property
    def end(self):
        """Timestamp where the entry ends."""
        return self.__end

    @property
    def dur(self):
        """Duration of the entry, or None if it cannot be calculated."""
        try:
            return self.__end - self.__beg

        except TypeError:
            return None


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
        """Label for this phone (e.g., using ARPABET transcription)."""
        return self.__seg

    @property
    def beg(self):
        """Timestamp where the phone begins."""
        return self.__beg

    @property
    def end(self):
        """Timestamp where the phone ends."""
        return self.__end

    @property
    def dur(self):
        """Duration of the phone, or None if it cannot be calculated."""
        try:
            return self.__end - self.__beg

        except TypeError:
            return None
