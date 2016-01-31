"""Classes and functions to read and loop through the Buckeye Corpus.

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


import bisect
import glob
import io
import os.path
import re
import wave
import zipfile

from .containers import Word, Pause, LogEntry, Phone


SPEAKERS = {'s01': ('f', 'y', 'f'), 's02': ('f', 'o', 'm'),
            's03': ('m', 'o', 'm'), 's04': ('f', 'y', 'f'),
            's05': ('f', 'o', 'f'), 's06': ('m', 'y', 'f'),
            's07': ('f', 'o', 'f'), 's08': ('f', 'y', 'f'),
            's09': ('f', 'y', 'f'), 's10': ('m', 'o', 'f'),
            's11': ('m', 'y', 'm'), 's12': ('f', 'y', 'm'),
            's13': ('m', 'y', 'f'), 's14': ('f', 'o', 'f'),
            's15': ('m', 'y', 'm'), 's16': ('f', 'o', 'm'),
            's17': ('f', 'o', 'm'), 's18': ('f', 'o', 'f'),
            's19': ('m', 'o', 'f'), 's20': ('f', 'o', 'f'),
            's21': ('f', 'y', 'm'), 's22': ('m', 'o', 'f'),
            's23': ('m', 'o', 'm'), 's24': ('m', 'o', 'm'),
            's25': ('f', 'o', 'm'), 's26': ('f', 'y', 'f'),
            's27': ('f', 'o', 'm'), 's28': ('m', 'y', 'm'),
            's29': ('m', 'o', 'f'), 's30': ('m', 'y', 'm'),
            's31': ('f', 'y', 'm'), 's32': ('m', 'y', 'f'),
            's33': ('m', 'y', 'f'), 's34': ('m', 'y', 'm'),
            's35': ('m', 'o', 'm'), 's36': ('m', 'o', 'f'),
            's37': ('f', 'y', 'm'), 's38': ('m', 'o', 'm'),
            's39': ('f', 'y', 'm'), 's40': ('m', 'y', 'f')}


TRACK_RE = r's[0-4][0-9]/s[0-4][0-9]0[0-6][ab]\.zip'


class Speaker(object):
    """Iterable of Track instances for one Buckeye speaker, with metadata.

    Use Speaker.from_zip(path) to initialize a Speaker from a single zip file.

    Parameters
    ----------
    name : str
        Code-name for the speaker in the Buckeye Corpus (e.g., 's01').

    tracks : list of Track
        Track instances containing the annotations and recordings for this
        speaker, as read from e.g. s0101a.zip, s0101b.zip, etc.

    Attributes
    ----------
    name : str
        Code-name for the speaker in the Buckeye Corpus (e.g., 's01').

    sex : str
        Sex of the speaker ('f' for female or 'm' for male)

    age : str
        Age of the speaker ('o' for older than 40, 'y' for younger)

    interviewer : str
        Sex of the person who interviewed the speaker ('f' or 'm')

    tracks : list of Track
        Track instances containing the annotations and recordings for this
        speaker, as read from e.g. s0101a.zip, s0101b.zip, etc.

    """

    def __init__(self, name, tracks):
        self.name = name
        self.sex, self.age, self.interviewer = SPEAKERS[self.name]
        self.tracks = tracks

    @classmethod
    def from_zip(cls, path, load_wavs=False):
        """Return a Speaker instance from a zip file.

        Parameters
        ----------
        path : str
            Path to a zipped speaker archive (e.g., 's01.zip').

        load_wavs : bool, optional
            If True, the .wav files in the archive are read into the Track
            instances, in addition to the text annotations. Default is False.

        Returns
        -------
        Speaker

        """

        name = os.path.splitext(os.path.basename(path))[0]

        tracks = []

        speaker = zipfile.ZipFile(path)

        for path in sorted(speaker.namelist()):
            if re.match(TRACK_RE, path):
                data = zipfile.ZipFile(io.BytesIO(speaker.read(path)))
                tracks.append(Track.from_zip(path, data, load_wavs))

        speaker.close()

        return cls(name, tracks)

    def __iter__(self):
        return iter(self.tracks)

    def __getitem__(self, i):
        return self.tracks[i]

    def __repr__(self):
        return 'Speaker("{}")'.format(self.name)

    def __str__(self):
        return '<Speaker {} ({}, {})>'.format(self.name, self.sex, self.age)


class Track(object):
    """Corpus data from one track archive file (e.g., s0101a.zip).

    Use Track.from_zip(path) to initialize a Track from a single zip file.

    Parameters
    ----------
    name : str
        Name of the track file (e.g., 's0101a')

    words : str or file
        Path to the .words file associated with this track (e.g.,
        's0101a.words'), or an open file(-like) object.

    phones : str or file
        Path to the .phones file associated with this track (e.g.,
        's0101a.phones'), or an open file(-like) object.

    log : str or file
        Path to the .log file associated with this track (e.g.,
        's0101a.log'), or an open file(-like) object.

    txt : str or file
        Path to the .txt file associated with this track (e.g.,
        's0101a.txt'), or an open file(-like) object.

    wav : str or file, optional
        Path to the .wav file associated with this track (e.g.,
        's0101a.wav'), or an open file(-like) object.

    Attributes
    ----------
    name : str
        Name of the track file (e.g., 's0101a')

    words : list of Word and Pause
        Chronological list of Word and Pause instances that are
        constructed from the .words file in this track.

    phones : list of Phone
        Chronological list of Phone instances that are constructed from
        the .phones file in this track.

    log : list of LogEntry
        Chronological list of LogEntry instances that are constructed from
        the .log file in this track.

    txt : list of str
        Chronological list of transcriptions of each turn from the .txt
        file in this track (not time-aligned).

    wav : wave.Wave_read
        An open wave.Wave_read instance for the .wav file in this track.
        If this track was constructed with `load_wav=False`, this
        attribute is not present.

    """

    def __init__(self, name, words, phones, log, txt, wav=None):
        self.name = name

        # read and store text info
        if not hasattr(words, 'readline'):
            words = io.open(words, encoding='latin-1')

        self.words = list(process_words(words))
        words.close()

        if not hasattr(phones, 'readline'):
            phones = io.open(phones, encoding='latin-1')

        self.phones = list(process_phones(phones))
        phones.close()

        if not hasattr(log, 'readline'):
            log = io.open(log, encoding='latin-1')

        self.log = list(process_logs(log))
        log.close()

        if not hasattr(txt, 'readline'):
            txt = io.open(txt, encoding='latin-1')

        self.txt = txt.read().splitlines()
        txt.close()

        # optionally store the sound file
        if wav is not None:
            self.wav = wave.open(wav)

        # add references in self.words to the corresponding self.phones
        self._set_phones()

        # make a list of the log entry timestamps to quickly search later
        self._log_begs = [l.beg for l in self.log]
        self._log_ends = [l.end for l in self.log]

    def __repr__(self):
        return 'Track("{}")'.format(self.name)

    def __str__(self):
        return '<Track {}>'.format(self.name)

    @classmethod
    def from_zip(cls, path, data=None, load_wav=False):
        """Return a Track instance from a zip file.

        Parameters
        ----------
        path : str
            Path to a zipped track archive (e.g., 's01/s0101a.zip').

        data : zipfile.ZipFile, optional
            ZipFile instance containing track data, required if `path`
            points to a zipped archive nested inside another archive. Default
            is None.

        load_wav : bool, optional
            If True, the .wav file will be read into the Track instance, in
            addition to the text annotations. Default is False.

        Returns
        -------
        Track

        """

        if data is None:
            data = zipfile.ZipFile(path)

        name = os.path.splitext(os.path.basename(path))[0]

        words = io.StringIO(data.read(name + '.words').decode('latin-1'))
        phones = io.StringIO(data.read(name + '.phones').decode('latin-1'))
        log = io.StringIO(data.read(name + '.log').decode('latin-1'))
        txt = io.StringIO(data.read(name + '.txt').decode('latin-1'))

        if load_wav:
            wav = io.BytesIO(data.read(name + '.wav'))

        else:
            wav = None

        return cls(name, words, phones, log, txt, wav)

    def _set_phones(self):
        """
        Private method used to add references in each Word and Pause
        instance to the corresponding Phone instances in this track.

        Notes
        -----
        A Phone is counted as belonging to a Word or Pause if at least
        half of the Phone's duration occurs between the `beg` and `end`
        timestamps of the Word or Pause.

        """

        phone_mids = [p.beg + 0.5 * p.dur for p in self.phones]

        for word in self.words:
            left = bisect.bisect_left(phone_mids, word.beg)
            right = bisect.bisect_left(phone_mids, word.end)

            word._phones = self.phones[left:right]

    def clip_wav(self, clip, beg, end):
        """Write a new .wav file containing a clip from this track.

        Parameters
        ----------
        clip : str
            Path to the new .wav file.

        beg : float
            Time in the track .wav file where the clip should begin.

        end : float
            Time in the track .wav file where the clip should end.

        Returns
        -------
        None

        """

        framerate = self.wav.getframerate()
        length = end - beg

        frames = int(round(length * framerate))
        beg_frame = int(round(beg * framerate))

        wav_out = wave.open(clip, 'wb')

        wav_out.setparams(self.wav.getparams())
        self.wav.setpos(beg_frame)
        wav_out.writeframes(self.wav.readframes(frames))

        wav_out.close()

    def get_logs(self, beg, end):
        """Return log entries that overlap with a given interval.

        The interval does not include the log entry boundaries. For
        example, calling `get_logs(1.5, 2)` will not return a log entry
        that extends from 1.25 seconds to 1.5 seconds, or one that
        extends from 2 seconds to 2.5 seconds.

        Parameters
        ----------
        beg : float
            Beginning of the interval.

        end : float
            End of the interval.

        Returns
        -------
        logs : list of LogEntry
            List of references to the LogEntry instances in this track
            that overlap with the interval given by `[beg, end]`.

        """

        left_idx = bisect.bisect(self._log_ends, beg)
        right_idx = bisect.bisect_left(self._log_begs, end)

        return self.log[left_idx:right_idx]


def corpus(path, load_wavs=False):
    """Yield Speaker instances from a folder of zipped speaker archives.

    Parameters
    ----------
    path : str
        Path to a directory containing all of the zipped speaker archives
        in the Buckeye Corpus (s01.zip, s02.zip, ..., s40.zip).

    load_wavs : bool, optional
        If True, the .wav files are read into the Track instances in the
        yielded Speaker instances. Default is False.

    Yields
    ------
    Speaker
        One Speaker instance for each zipped speaker archive in the
        folder given by `path`.

    """

    paths = sorted(glob.glob(os.path.join(path, 's[0-4][0-9].zip')))

    for path in paths:
        yield Speaker.from_zip(path, load_wavs)


def process_logs(logs):
    """Yield LogEntry instances from a .log file in the Buckeye Corpus.

    Parameters
    ----------
    logs : file-like
        Open file-like object created from a .log file in the Buckeye
        Corpus.

    Yields
    ------
    LogEntry
        One LogEntry instance for each entry in the .log file, in
        chronological order.

    """

    # skip the header
    line = logs.readline()

    while not line.startswith('#'):
        if line == '':
            raise EOFError

        line = logs.readline()

    line = logs.readline()

    # iterate over entries
    previous = 0.0
    while line != '':
        try:
            time, color, entry = line.split(None, 2)
            entry = entry.strip()

        except ValueError:
            if line == '\n':
                line = logs.readline()
                continue

            time, color = line.split()
            entry = None

        time = float(time)
        yield LogEntry(entry, previous, time)

        previous = time
        line = logs.readline()


def process_phones(phones):
    """Yield Phone instances from a .phones file in the Buckeye Corpus.

    Parameters
    ----------
    phones : file-like
        Open file-like object created from a .phones file in the Buckeye
        Corpus.

    Yields
    ------
    Phone
        One Phone instance for each entry in the .phones file, in
        chronological order.

    """

    # skip the header
    line = phones.readline()

    while not line.startswith('#'):
        if line == '':
            raise EOFError

        line = phones.readline()

    line = phones.readline()

    # iterate over entries
    previous = 0.0
    while line != '':
        try:
            time, color, phone = line.split(None, 2)

            if '+1' in phone:
                phone = phone.replace('+1', '')

            if ';' in phone:
                phone = phone.split(';')[0]

            phone = phone.strip()

        except ValueError:
            if line == '\n':
                line = phones.readline()
                continue

            time, color = line.split()
            phone = None

        time = float(time)
        yield Phone(phone, previous, time)

        previous = time
        line = phones.readline()


def process_words(words):
    """Yield Word and Pause instances from a .words file.

    Parameters
    ----------
    words : file-like
        Open file-like object created from a .words file in the Buckeye
        Corpus.

    Yields
    ------
    Word, Pause
        One Word or Pause instance for each entry in the .words file, in
        chronological order. Entries that begin with '{' or '<' are
        yielded as Pause instances. All other entries are yielded as Word
        instances.

    """

    # skip the header
    line = words.readline()

    while not line.startswith('#'):
        if line == '':
            raise EOFError

        line = words.readline()

    line = words.readline()

    # iterate over entries
    previous = 0.0
    while line != '':
        fields = [l.strip() for l in line.strip().split(';')]

        try:
            word, phonemic, phonetic, pos = fields
            phonemic = phonemic.split()
            phonetic = phonetic.split()

        except ValueError:
            if line == '\n':
                line = words.readline()
                continue

            # 22 entries have missing fields, including 11 CUTOFF, ERROR, and
            # E_TRANS entries
            if len(fields) == 2:
                word, pos = fields
                phonemic = None

            elif len(fields) == 3:
                word, phonemic, pos = fields
                phonemic = phonemic.split()

            phonetic = None

        # s1801a has a missing newline in the first entry, with SIL and
        # B_TRANS on the same line with the same timestamp
        time, color, word = (w.strip() for w in word.split(None, 2))

        time = float(time)

        # 1603b starts at -1.0s, and 2801a has one line that has a timestamp
        # that precedes the timestamp on the previous line
        # for these entries, the misaligned attribute will be set to True

        if word.startswith('<') or word.startswith('{'):
            yield Pause(word, previous, time)

        else:
            yield Word(word, previous, time, phonemic, phonetic, pos)

        previous = time
        line = words.readline()
