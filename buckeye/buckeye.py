from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from bisect import bisect_left
from cStringIO import StringIO
from os.path import basename, splitext, join

import glob
import re
import wave
import zipfile

from .containers import Word, Pause, LogEntry, Phone, Utterance


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
    """Iterable of Track instances for the subfiles of one speaker
    (s0101a.zip, s0101b.zip, ...). Also includes metadata for that
    speaker.

    Arguments:
        zpath:      path to a zipped speaker archive (s01.zip, ...)
        load_wavs:  if True, the wav files in the archive are read into
                    Track instances, in addition to the text annotations.
                    Default is False.

    Attributes:
        name:       the speaker's code in the Buckeye Corpus ('s01', ...)
        path:       path to the zipped speaker archive
        sex:        'f' or 'm' for the sex of the speaker
        age:        'o' or 'y' for the age of the speaker (old or young)
        interviewer:'f' or 'm' for the sex of the speaker's interviewer
        tracks:     list of Track instances containing corpus data
                    (as read from s0101a.zip, s0101b.zip, ...)
    """

    def __init__(self, zpath, load_wavs=False):
        self.name = splitext(basename(zpath))[0]
        self.path = zpath

        self.sex = SPEAKERS[self.name][0]
        self.age = SPEAKERS[self.name][1]
        self.interviewer = SPEAKERS[self.name][2]

        self.tracks = []

        zfile = zipfile.ZipFile(zpath)

        for subzip in sorted(zfile.namelist()):
            if re.match(TRACK_RE, subzip):
                track_contents = zipfile.ZipFile(StringIO(zfile.read(subzip)))
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
    """Container holding the processed annotation data, and optionally
    the wav file, for one subfile (s0101a.zip, ...).

    Arguments:
        path:       relative path to a track inside a zipped speaker archive
                    ('s0101a.zip', ...)
        contents:   ZipFile instance for the zipped track archive
                    (s0101a.zip, ...)
        load_wav:   if True, the wav file will be read into the Track
                    instance in addition to the text annotation data.
                    Default is False.

    Attributes:
        name:       name of the track file ('s0101a', ...)
        path:       relative path to the track in the zipped speaker archive
        words:      list of Word instances, as processed from a .words file.
                    Generated using process_words().
        phones:     list of Phone instances, as processed from a .phones file.
                    Generated using process_phones().
        log:        list of LogEntry instances, as processed from a .log file.
                    Generated using process_logs().
        txt:        list of unaligned turn transcriptions, from a .txt file.
        wav:        if load_wav=True, an open Wave_read instance from the
                    Python wave library for the track .wav file
        log_ends:   list of the end timestamps for each LogEntry, to be used
                    internally by get_logs() method
    """

    def __init__(self, path, contents, load_wav=False):
        self.name = splitext(basename(path))[0]
        self.path = path

        # store text info
        self.words = list(process_words(StringIO(contents.read(self.name+'.words'))))
        self.phones = list(process_phones(StringIO(contents.read(self.name+'.phones'))))
        self.log = list(process_logs(StringIO(contents.read(self.name+'.log'))))
        self.txt = contents.read(self.name+'.txt').splitlines()

        # optionally store the sound file
        if load_wav:
            self.wav = wave.open(StringIO(contents.read(self.name+'.wav')))

        # add references in self.words to the corresponding self.phones
        self.get_all_phones()

        # make a list of the log entry endpoints to quickly search later
        self.log_ends = [l.end for l in self.log]

    def __repr__(self):
        return 'Track("{}")'.format(self.path)

    def __str__(self):
        return '<Track {}>'.format(self.name)

    def clip_wav(self, clip, beg, end):
        """Extracts a clip from the track .wav file.
        From: https://github.com/serapio/kwaras/blob/master/process/web.py

        Arguments:
            clip:       path and filename to write the sound clip to
            beg:        timestamp in the track .wav file where the clip
                        to be extracted begins
            end:        timestamp in the track .wav file where the clip
                        to be extracted ends

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

    def get_all_phones(self):
        """Finds the slice of Phone instances in self.phones that belong to
        of each Word instance in this track. Adds a list of references in
        each Word instance to its matching Phone instances as the word's
        `phones' attribute.

        Each Word instance will also have a `misaligned' attribute that is
        False if the list of matching Phone instances corresponds to the
        word's phonetic transcription in its `phonetic' attribute, True if
        it does not, or None if the get_all_phones() method has not been
        called.

        The boundaries for the phone entries in the .phones files don't
        always line up exactly with the word boundaries in the .words files.
        This method treats a phone as belonging to a word if at least half
        of the phone overlaps with the word. The method checks for B_TRANS,
        E_TRANS, VOCNOISE, or LAUGH tokens that halfway overlap with the
        word, and excludes them from the list of Phone references.
        """

        phone_mids = [p.beg + 0.5 * p.dur for p in self.phones]
        for word in self.words:
            left = bisect_left(phone_mids, word.beg)
            right = bisect_left(phone_mids, word.end)

            phones = self.phones[left:right]

            # 21 tracks have a B_TRANS or E_TRANS marker that overlaps a word
            # 3 tracks have overlapping VOCNOISE and 1 has overlapping LAUGH
            if (len(phones) != len(word.phonetic) and
                    len(word.phonetic) > 0 and len(phones) > 0):
                if phones[0].seg in ('{B_TRANS}', 'VOCNOISE', 'LAUGH'):
                    left = left + 1
                    phones = self.phones[left:right]

                if phones[-1].seg == '{E_TRANS}':
                    right = right - 1
                    phones = self.phones[left:right]

            # 52 close transcriptions in .words files start with a silence
            # word.misaligned will be marked True

            word.phones = phones

    def get_logs(self, beg, end):
        """Returns all log entries within the times given, including
        entries that partially overlap with the given times.

        Arguments:
            beg:        log entries that begin after (exclusive) or
                        overlap with this time will be returned
            end:        log entries that begin at or after this time
                        will not be returned

        Returns:
            List of references to LogEntry instances in this track that
            are within the times given.
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
    """Generator that takes a path to a folder containing compressed Buckeye
    Corpus speaker archives and yields Speaker instances.

    Arguments:
        path:           path to a directory containing all of the zipped
                        speaker archives (s01.zip, s02.zip, s03.zip, ...)
        load_wavs:      if True, wav files are read into the Track instances
                        that are referenced in the yielded Speaker instances.
                        Default is False.
    """

    paths = sorted(glob.glob(join(path, 's[0-4][0-9].zip')))

    for path in paths:
        yield Speaker(path, load_wavs)

def process_logs(logs):
    """Generator that takes a Buckeye .log corpus file and yields LogEntry
    instances in the order that they appear.

    Arguments:
        logs:       open file(-like) instance created from a .log file in
                    the Buckeye Corpus

    Yields:
        LogEntry instances for each sequential entry in the .log file
    """

    # skip the header
    line = logs.readline()
    while not line.startswith('#'):
        if line == '':
            raise EOFError
        line = logs.readline()

    line = logs.readline()
    if line == '\n':
        line = logs.readline()

    previous = 0.0
    while line != '':
        try:
            time, color, entry = line.split(None, 2)
        except ValueError:
            if line == '\n':
                line = logs.readline()
                continue
            time, color = line.split()
            entry = ''

        time = float(time)
        yield LogEntry(entry.strip(), previous, time)
        previous = time
        line = logs.readline()

def process_phones(phones):
    """Generator that takes a Buckeye .phones corpus file and yields Phone
    instances in the order that they appear.

    Arguments:
        phones:     open file(-like) instance created from a .phones file
                    in the Buckeye Corpus

    Yields:
        Phone instances for each sequential entry in the .phones file
    """

    # skip the header
    line = phones.readline()
    while not line.startswith('#'):
        if line == '':
            raise EOFError
        line = phones.readline()

    line = phones.readline()
    if line == '\n':
        line = phones.readline()

    # iterate over entries
    previous = 0.0
    while line != '':
        try:
            time, color, phone = line.split(None, 2)
        except ValueError:
            if line == '\n':
                line = phones.readline()
                continue
            time, color = line.split()
            phone = ''

        if '"' in phone:
            phone = phone.replace('"', '')
        if '+1' in phone:
            phone = phone.replace('+1', '')
        if ';' in phone:
            phone = phone.split(';')[0]

        time = float(time)
        yield Phone(phone.strip(), previous, time)

        previous = time
        line = phones.readline()

def process_words(words):
    """Generator that takes a Buckeye .words corpus file and yields Word
    instances in the order that they appear.

    Non-word entries (such as `B_TRANS' entries) are also yielded as Word
    instances. Use words_to_utterances() or another function to convert
    these to Pause instances instead.

    Arguments:
        words:      open file(-like) instance created from a .words file
                    in the Buckeye Corpus

    Yields:
        Word instances for each sequential entry in the .words file.
    """

    # skip the header
    line = words.readline()
    while not line.startswith('#'):
        if line == '':
            raise EOFError
        line = words.readline()

    line = words.readline()
    if line == '\n':
        line = words.readline()

    # iterate over entries
    previous = 0.0
    while line != '':
        try:
            word, phonemic, phonetic, pos = (l.strip() for l in line.strip().split(';'))
        except ValueError:
            # 22 entries have missing fields, including
            # 11 CUTOFF, ERROR, E_TRANS entries
            fields = [l.strip() for l in line.strip().split(';')]
            if len(fields) == 2:
                word, pos = fields
                phonemic, phonetic = '', ''
            elif len(fields) == 3:
                word, phonemic, pos = fields
                phonetic = ''
            elif line == '\n':
                line = words.readline()
                continue

        # s1801a has a missing newline in the first entry, with SIL and
        # B_TRANS on the same line with the same timestamp
        time, color, word = (w.strip() for w in word.split(None, 2))

        if '"' in word:
            word = word.replace('"', '')

        time = float(time)

        # 1603b starts at -1.0s, and 2801a has one line that has a
        # timestamp that precedes the timestamp on the previous line
        # word.misaligned will be marked as True

        yield Word(word, previous, time, phonemic.split(), phonetic.split(), pos)
        previous = time
        line = words.readline()

def words_to_utterances(words):
    """Generator that takes an iterable of Word instances, such as
    process_words(), and yields Utterance instances containing lists
    of Word and Pause instances.

    Non-word entries such as `B_TRANS' and `SIL', interviewer speech,
    vocal noise or speech errors, etc., are replaced by Pause instances
    in the Utterance. A new Utterance is created at the start of the
    iterable passed to words_to_utterances(), and then whenever there
    is a sequence of non-word entries that add up to 0.5 seconds or more
    of duration.

    Arguments:
        words:      iterable of only Word instances

    Yields:
        Utterance instances for each sequence of word entries delimited by
        >= 0.5 seconds of non-word entries. Non-word entries, or word
        entries with invalid timestamps, are stripped from the beginning
        and end of the words list belonging to each yielded Utterance.
    """

    utt = Utterance()
    pause_duration = 0.0
    pause = False
    for word in words:
        # if this item is a pause token (or a bad Word entry)...
        if re.match(PAUSE_RE, word.orthography) or not word.phonetic:
            # skip it if there are no words in the utterance yet
            if len(utt) == 0:
                continue

            # if this item doesn't follow another pause,
            # restart the cumulative pause duration
            if not pause:
                pause_duration = word.dur

            # if this item does follow another pause,
            # add it to the cumulative pause duration
            else:
                pause_duration += word.dur

            # append this item as a pause
            pause = True
            utt.append(Pause(word.orthography, word.beg, word.end))

        # if this is not a pause token, append this item as a word
        else:
            pause = False
            utt.append(word)

        # if the total pause duration has reached 500 ms,
        # return this utterance and start a new one
        if pause_duration >= 0.5:
            yield utt.strip()
            utt = Utterance()
            pause_duration = 0.0

    # return the last utterance if there is one
    if len(utt) > 0:
        yield utt.strip()
