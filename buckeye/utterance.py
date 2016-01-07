"""Container for a chunk of speech bounded by long pauses.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .containers import Word, Pause


class Utterance(object):
    """Iterable of Word and Pause instances comprising one chunk of speech.

    Parameters
    ----------
    words : list of Word and Pause, optional
        List of Word and Pause instances that comprise one speech chunk.
        Default is None.

    Attributes
    ----------
    words

    Container for a list of entries, such as Word and Pause instances,
    that make up an utterance in the speech corpus.

    """

    def __init__(self, words=None):
        if words is None:
            self.__words = []
            return

        try:
            words = sorted(words, key=lambda x: float(x.beg))

            flipped = [True for w in words if float(w.beg) > float(w.end)]

            overlap = [True for w1, w2 in zip(words, words[1:])
                       if float(w1.end) > float(w2.beg)]

        except (AttributeError, TypeError, ValueError):
            raise TypeError('All items in utterance must have numeric '
                            'beg and end attributes')

        if flipped:
            raise ValueError('Reversed items in utterance')

        if overlap:
            raise ValueError('Overlapping items in utterance')

        self.__words = words

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

    def beg(self):
        """Timestamp where the first item in the utterance begins."""
        try:
            return self.__words[0].beg

        except IndexError:
            raise IndexError('Utterance is empty')

    def end(self):
        """Timestamp where the last item in the utterance ends."""
        try:
            return self.__words[-1].end

        except IndexError:
            raise IndexError('Utterance is empty')

    def dur(self):
        """Duration of the utterance."""
        try:
            return self.__words[-1].end - self.__words[0].beg

        except IndexError:
            raise IndexError('Utterance is empty')

    def words(self):
        """Chronological list of Word and Pause instances in this utterance."""
        return self.__words

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

        try:
            beg = float(item.beg)
            end = float(item.end)

        except (AttributeError, TypeError, ValueError):
            raise TypeError('Item must have numeric beg and end attributes '
                            'to append to Utterance')

        if beg > end:
            raise ValueError('Item beg timestamp: {0} is after item end '
                             'timestamp: {1}'.format(str(item.beg), str(item.end)))

        for word in self.__words:
            if float(word.beg) > beg and not float(word.beg) > end:
                raise ValueError('Item overlaps with existing items in utterance')

        self.__words.append(item)
        self.__words = sorted(self.__words, key=lambda x: float(x.beg))

    def __iter__(self):
        return iter(self.__words)

    def __getitem__(self, i):
        return self.__words[i]

    def __len__(self):
        return len(self.__words)

    def speech_rate(self, use_phonetic=True, no_syllables='raise'):
        """Return the number of syllables per second in this utterance.

        There may be pauses at the beginning or end of an utterance
        that you do not want to include when calculating the speech
        rate of the utterance. To ignore any pauses at the beginning
        or end, use `no_syllables='squeeze'`. To remove them from the
        utterance, use `utterance.strip()`.

        Parameters
        ----------
        use_phonetic: bool, optional
            If True, this method counts syllables in the close phonetic
            transcriptions of the items in this utterance (see
            `Word.syllables`). If False, use the phonemic attribute to
            count syllables instead. Default is True.

        no_syllables : {'zero', 'squeeze', 'raise'}
            If 'zero', any items in the utterance without a
            `syllables` property are treated as having zero syllables
            for the speech rate calculation. Default is 'zero'.

            If 'squeeze`, the same behavior as 'zero', plus any items
            at the beginning or end of the utterance with no `syllables`
            attribute are ignored while summing the total utterance
            duration.

            If 'raise', a ValueError is raised if the utterance includes
            any items without a `syllables` attribute.

        Returns
        -------
        rate : float
            The number of syllabic segments per second over the items in
            this utterance.

        """

        if no_syllables not in {'zero', 'squeeze', 'raise'}:
            raise ValueError('"no_syllables" argument must be one of "zero", '
                             '"squeeze", or "raise"')

        if not self.__words:
            raise ValueError('Utterance is empty')

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
            return float(syllable_count) / float(self.dur())

    def strip(self):
        """Strip items that are not Words, or Words where the duration
        is not positive, from the left and right edges of the utterance.
        """

        try:
            left = next(i for i in self if isinstance(i, Word) and i.dur > 0)

            right = next(i for i in reversed(self.__words)
                         if isinstance(i, Word) and i.dur > 0)

            left_idx = self.__words.index(left)
            right_idx = self.__words.index(right) + 1

            self.__words = self.__words[left_idx:right_idx]

        except StopIteration:
            self.__words = []

        return self


def words_to_utterances(words, sep=0.5):
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

    Yields
    ------
    utt : Utterance
        An Utterance for each sequence of word entries delimited by
        >= `sep` seconds (default 0.5) of Pause instances. Pause instances,
        or Word instances with invalid timestamps, are removed from the
        beginning and ends of the list of items in each Utterance.

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
