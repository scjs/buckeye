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

from bisect import bisect_left
from io import BytesIO, StringIO
from os.path import basename, splitext, join

import glob
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

PAUSE_RE = re.compile('(<|>|{|}|TRANS|SIL|IVER|ERROR|CUTOFF|'
                      'EXCLUDE|VOCNOISE|NOISE|UNKNOWN|LAUGH)')

TRACK_RE = re.compile('s[0-4][0-9]/s[0-4][0-9]0[0-6][ab].zip')


class Speaker(object):
    """Iterable of Track instances for one Buckeye speaker, with metadata.

    Parameters
    ----------
    path : str
        Path to a zipped speaker archive (e.g., 's01.zip').

    load_wavs : bool, optional
        If True, the .wav files in the archive are read into the Track
        instances, in addition to the text annotations. Default is False.

    Attributes
    ----------
    name : str
        Code-name for the speaker in the Buckeye Corpus (e.g., 's01').

    path : str
        Path to the zipped speaker archive.

    sex : str
        Sex of the speaker ('f' for female or 'm' for male)

    age : str
        Age of the speaker ('o' for older than 40, 'y' for younger)

    interviewer : str
        Sex of the person who interviewed the speaker ('f' or 'm')

    tracks : list of Track
        Track instances containing the corpus data, as read from
        e.g. s0101a.zip, s0101b.zip, etc.

    """

    def __init__(self, path, load_wavs=False):
        self.name = splitext(basename(path))[0]
        self.path = path

        self.sex, self.age, self.interviewer = SPEAKERS[self.name]

        self.tracks = []

        zfile = zipfile.ZipFile(path)

        for subzip in sorted(zfile.namelist()):
            if re.match(TRACK_RE, subzip):
                track_contents = zipfile.ZipFile(BytesIO(zfile.read(subzip)))
                track = Track(subzip, track_contents, load_wavs)
                self.tracks.append(track)

        zfile.close()

    def __iter__(self):
        return iter(self.tracks)

    def __getitem__(self, i):
        return self.tracks[i]

    def __repr__(self):
        return 'Speaker("{}")'.format(self.path)

    def __str__(self):
        return '<Speaker {} ({}, {})>'.format(self.name, self.sex, self.age)


class Track(object):
    """Corpus data from one track archive file (e.g., s0101a.zip).

    Parameters
    ----------
    path : str
        Path to a zipped track archive (e.g., 's01/s0101a.zip').

    contents : file-like
        Open file-like object of track data.

    load_wav : bool, optional
        If True, the .wav file will be read into the Track instance, in
        addition to the text annotations. Default is False.

    Attributes
    ----------
    name : str
        Name of the track file (e.g., 's0101a')

    path : str
        Path to the zipped track archive.

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

    def __init__(self, path, contents, load_wav=False):
        self.name = splitext(basename(path))[0]
        self.path = path

        # read and store text info
        words = contents.read(self.name + '.words').decode('cp1252')
        phones = contents.read(self.name + '.phones').decode('cp1252')
        log = contents.read(self.name + '.log').decode('cp1252')
        txt = contents.read(self.name + '.txt').decode('cp1252')

        self.words = list(process_words(StringIO(words)))
        self.phones = list(process_phones(StringIO(phones)))
        self.log = list(process_logs(StringIO(log)))
        self.txt = txt.splitlines()

        # optionally store the sound file
        if load_wav:
            wav = contents.read(self.name + '.wav')
            self.wav = wave.open(BytesIO(wav))

        # add references in self.words to the corresponding self.phones
        self._set_phones()

        # make a list of the log entry endpoints to quickly search later
        self.log_ends = [l.end for l in self.log]

    def __repr__(self):
        return 'Track("{}")'.format(self.path)

    def __str__(self):
        return '<Track {}>'.format(self.name)

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
            left = bisect_left(phone_mids, word.beg)
            right = bisect_left(phone_mids, word.end)

            phones = self.phones[left:right]

            # 21 tracks have a B_TRANS or E_TRANS marker that overlaps a word
            # 3 tracks have overlapping VOCNOISE and 1 has overlapping LAUGH
            if (hasattr(word, 'phonetic') and word.phonetic and phones and
                    len(word.phonetic) != len(phones)):
                if phones[0].seg in ('{B_TRANS}', 'VOCNOISE', 'LAUGH'):
                    left = left + 1
                    phones = self.phones[left:right]

                if phones[-1].seg == '{E_TRANS}':
                    right = right - 1
                    phones = self.phones[left:right]

            # 52 close transcriptions in .words files start with a silence
            # word.misaligned will be marked True

            word.phones = phones

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
        """Return log entries within, or overlapping with, the given times.

        Parameters
        ----------
        beg : float
            Log entries that begin after or overlap with this time will
            be included in the returned list.

        end : float
            Log entries that end before or overlap with this time will be
            included in the returned list.

        Returns
        -------
        logs : list of LogEntry
            List of references to the LogEntry instances in this track
            that are within the given times.

        """

        # returns all log intervals that overlap with the times given
        logs = []

        log_idx = bisect_left(self.log_ends, beg)

        try:
            if self.log[log_idx].end == beg:
                log_idx += 1

        except IndexError:
            # the log tier ends before the beg time
            return logs

        while log_idx + 1 < len(self.log) and self.log[log_idx].beg < end:
            logs.append(self.log[log_idx])
            log_idx += 1

        return logs


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

    paths = sorted(glob.glob(join(path, 's[0-4][0-9].zip')))

    for path in paths:
        yield Speaker(path, load_wavs)

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
                phonemic = phonetic = None

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
