"""Container for a chunk of speech bounded by long pauses.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .containers import Pause


class Utterance(object):
    """Iterable of Word and Pause instances comprising one chunk of speech.

    Parameters
    ----------
    words : list of Word and Pause, optional
        List of Word and Pause instances that comprise one speech chunk.
        Default is None.

    Attributes
    ----------
    beg
    end
    dur
    words

    """

    def __init__(self, words=None):
        if words is None:
            self._words = []
            return

        words = sorted(words, key=lambda word: float(word.beg))

        for word in words:
            if float(word.beg) > float(word.end):
                raise ValueError('Reversed items in utterance')

        for left, right in zip(words, words[1:]):
            if float(left.end) > float(right.beg):
                raise ValueError('Overlapping items in utterance')

        self._words = words

    def __repr__(self):
        return 'Utterance({})'.format(repr(self.words))

    def __str__(self):
        utt = []

        for word in self._words:
            if hasattr(word, 'orthography'):
                utt.append(word.orthography)

            elif hasattr(word, 'entry'):
                utt.append(word.entry)

            else:
                utt.append(str(word))

        return '<Utterance "{}">'.format(' '.join(utt))

    @property
    def beg(self):
        """Timestamp where the first item in the utterance begins."""
        try:
            return self._words[0].beg

        except IndexError:
            raise AttributeError('Utterance is empty')

    @property
    def end(self):
        """Timestamp where the last item in the utterance ends."""
        try:
            return self._words[-1].end

        except IndexError:
            raise AttributeError('Utterance is empty')

    @property
    def dur(self):
        """Duration of the utterance."""
        try:
            return self._words[-1].end - self._words[0].beg

        except IndexError:
            raise AttributeError('Utterance is empty')

    @property
    def words(self):
        """Chronological list of Word and Pause instances in this utterance."""
        return self._words

    def append(self, item):
        """Append an instance to this utterance.

        Parameters
        ----------
        word : Word or Pause instance
            Instance with `beg` and `end` attributes to be appended to this
            utterance.

        Returns
        -------
        None

        """

        beg = float(item.beg)
        end = float(item.end)

        if beg > end:
            raise ValueError('Item beg timestamp: {0} is after item end '
                             'timestamp: {1}'.format(str(item.beg), str(item.end)))

        for word in self._words:
            if float(word.beg) > beg and float(word.beg) <= end:
                raise ValueError('Item overlaps with existing items in utterance')

        self._words.append(item)
        self._words = sorted(self._words, key=lambda word: float(word.beg))

    def __iter__(self):
        return iter(self._words)

    def __getitem__(self, i):
        return self._words[i]

    def __len__(self):
        return len(self._words)

    def speech_rate(self, use_phonetic=True, ignore_missing_syllables=False):
        """Return the number of syllables per second in this utterance.

        Parameters
        ----------
        use_phonetic: bool, optional
            If True, this method counts syllables in the close phonetic
            transcriptions of the items in this utterance (see
            `Word.syllables`). If False, use the phonemic transcription to
            count syllables instead. Default is True.

        ignore_missing_syllables : bool, optional
            If True, then items in the utterance without a `syllables`
            property will be counted as having zero zyllables when this
            method is called. If False, a ValueError will be raised if
            the utterance includes any items without a `syllables`
            property. Default is False.

        Returns
        -------
        rate : float
            The number of syllabic segments per second over the items in
            this utterance.

        """

        if not self._words:
            raise ValueError('Utterance is empty')

        syllable_count = 0

        for word in self._words:
            if hasattr(word, 'syllables'):
                syllable_count += word.syllables(use_phonetic)

            elif not ignore_missing_syllables:
                raise ValueError('All objects in Utterance must have a '
                                 'syllables property to calculate speech '
                                 'rate')

        return float(syllable_count) / float(self.dur)


def words_to_utterances(words, sep=0.5, strip_pauses=True):
    """Yield Utterance instances from iterable of Word and Pause instances.

    Generator that takes an iterable of Word and Pause instances, such as
    process_words(), and packs them into Utterance instances.

    A new Utterance is created at the start of the iterable passed to
    words_to_utterances(), and then whenever there is a sequence of Pause
    instances that add up to `sep` seconds or more of duration.

    Parameters
    ----------
    words : iterable object of Word and Pause instances

    sep : float, optional
        If more than `sep` seconds of Pause instances occur consecutively,
        yield the current Utterance instance and initialize a new one with
        no items. Default is 0.5.

    strip_pauses : bool, optional
        If True, then Pause instances are removed from the beginning and end of
        each Utterance before it is yielded. Default is True.

    Yields
    ------
    utt : Utterance
        An Utterance for each sequence of word entries delimited by
        >= `sep` seconds (default 0.5) of Pause instances.

    """

    utt = Utterance()
    pause_duration = 0.0
    pause_count = 0

    for word in words:
        # if this item is a pause token...
        if isinstance(word, Pause):

            # optionally skip it if there are no words in the utterance yet
            if strip_pauses and len(utt) == 0:
                continue

            # if this item doesn't follow another pause, restart the
            # pause duration
            if not pause_count:
                pause_duration = word.dur

            # otherwise, add it to the cumulative pause duration
            else:
                pause_duration += word.dur

            pause_count += 1

        else:
            pause_count = 0

        utt.append(word)

        # if the total pause duration has reached `sep` seconds, return this
        # utterance and start a new one
        if pause_duration >= sep:

            # optionally remove any pauses at the end
            if strip_pauses and pause_count:
                utt._words = utt._words[:-pause_count]

            if len(utt) > 0:
                yield utt

                utt = Utterance()

            pause_duration = 0.0
            pause_count = 0

    # return the last utterance if there is one
    if strip_pauses and pause_count:
        utt._words = utt._words[:-pause_count]

    if len(utt) > 0:
        yield utt
