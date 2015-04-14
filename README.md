This repository has Python classes for iterating through the annotations
in the [Buckeye Corpus](http://buckeyecorpus.osu.edu/). They include 
cross-references between the .words, .phones, and .log files, and
can be used to extract sound clips from the .wav files. The docstrings in
`buckeye.py` and `containers.py` describe how to use the classes in more
detail.

The scripts can be installed directly from GitHub with pip using this command:

    pip install git+http://github.com/scjs/buckeye.git

You can also copy the `buckeye/` subdirectory into your working directory, or
put it in your Python path.

### Speaker

A `Speaker` instance is created by pointing to one of the zipped speaker
archives available on the corpus website. These archives have names like
`s01.zip`, `s02.zip`, and `s03.zip`.


```python
import buckeye

speaker = buckeye.Speaker('s01.zip')
```

This will open and process the annotations in each of the sub-archives inside
the speaker archive (the tracks, such as `s0101a` and `s0101b`). If an optional
`load_wavs` argument is set to `True` when creating a `Speaker` instance, the
wav files associated with each track will also be loaded into memory. Otherwise,
only the annotations are loaded.

Each `Speaker` instance has the speaker's code-name, sex, age, and interviewer
sex available as attributes.

```python
print speaker.name, speaker.sex, speaker.age, speaker.interviewer
```
```
s01 f y f
```

The tracks can be accessed through the `tracks` attribute.

```python
print speaker.tracks
```
```
[Track("s01/s0101a.zip"), Track("s01/s0101b.zip"), Track("s01/s0102a.zip"), Track("s01/s0102b.zip"), Track("s01/s0103a.zip")]
```    

The tracks can also be accessed by iterating through the `Speaker` instance.
There is more detail about accessing the annotations below under the heading
**Tracks**.

```python
for track in speaker:
    print track.name,
```
```
s0101a s0101b s0102a s0102b s0103a
```    

The `corpus()` generator function is a convenience for iterating through all of
the speaker archives together. Put all forty speaker archives in one directory,
such as `speakers/`. Create a new generator with this directory as an argument.

```python
corpus = buckeye.corpus('speakers/')
```

The generator will yield the `Speaker` instances in numerical order.

```python
for speaker in corpus:
    print speaker.name,
```
```
s01 s02 s03 s04 s05 s06 s07 s08 s09 s10 s11 s12 s13 s14 s15 s16 s17 s18 s19 s20 s21 s22 s23 s24 s25 s26 s27 s28 s29 s30 s31 s32 s33 s34 s35 s36 s37 s38 s39 s40
```    

If a `corpus()` generator is created with `load_wavs` set to `True`, this
argument will be passed to the `Speaker` instances that it creates. Loading the
`wav` files takes more memory and time than just loading the annotations, so
this option is `False` if not specified.

### Track

Each `Track` instance has `words`, `phones`, `log`, `txt`, and `wav` attributes
that contain the corpus data from one sub-archive.

The `txt` attribute holds a list of speaker turns without timestamps, read from
the `.txt` file in the track.

If `load_wavs` is `True`, the `wav` attribute stores the `.wav` file associated
with the track as a `Wave_read` instance, using the Python `wave` library. If
`load_wavs` is `False` (the default), the `Track` instance will not have a `wav`
attribute.

The `words`, `phones`, and `log` attributes store sequences of `Word`, `Phone`,
`LogEntry` instances, respectively, from the entries in the `.words`, `.phones`,
and `.log` files in the track.

#### Words

For example, the first five entries in the `.words` in the first track of the
first speaker can be retrieved like this:

```python
# store the corpus in a list
corpus_cached = list(buckeye.corpus('speakers/'))

# get the first speaker and the first track for that speaker
speaker = corpus_cached[0]
track = speaker.tracks[0]

# slice the first five words
five_words = track.words[:5]
```

Each entry is stored in a `Word` instance, which has attributes for each
annotation type in the `.words` file (e.g., orthography and phonetic
transcription; see the docstring for `Word` in `containers.py`).

```python
word = track.words[4]

print word.orthography, word.beg, word.end, word.phonemic, word.phonetic, word.pos, word.dur
```
```
okay 32.216575 32.622045 ['ow', 'k', 'ey'] ['k', 'ay'] NN 0.40547
```

The `Word` instance also has references to the `Phone` instances that belong to
the word. When a `Track` instance is created, it calls an internal
`get_all_phones()` method to add these references to each word, based on the
word's timestamps and the timestamps in the track's `.phones` file.

```python
print word.phones
```
```
[Phone('k', 32.216575, 32.376593), Phone('ay', 32.376593, 32.622045)]
```    

```python
for phone in word.phones:
    print phone.seg, phone.beg, phone.end, phone.dur
```
```
k 32.216575 32.376593 0.160018
ay 32.376593 32.622045 0.245452
```

#### Phones

The sequence of entries in the track's `.phones` file (such as `s0101a.phones`)
can also be accessed directly through the `Track` instance's `phones` attribute.
Here are the first five entries in the first `.phones` file.

```python
five_phones = track.phones[:5]

for phone in five_phones:
    print phone.seg, phone.beg, phone.end, phone.dur
```
```
{B_TRANS} 0.0 0.102385 0.102385
SIL 0.102385 4.275744 4.173359
NOISE 4.275744 8.513763 4.238019
IVER 8.513763 32.216575 23.702812
k 32.216575 32.376593 0.160018
```

#### Log

The list of entries in the `.log` file can be accessed the same way.

```python
log = track.log[0]

print log.entry, log.beg, log.end
```
```
<VOICE=modal> 0.0 61.142603
```    

The `get_logs()` method of the `Track` class can be called to retrieve the log
entries that overlap with the given timestamps. For example, the log entries
that overlap with the interval from 60 seconds to 62 seconds can be found like
this:

```python
logs = track.get_logs(60.0, 62.0)

for log in logs:
    print log.entry, log.beg, log.end
```
```
<VOICE=modal> 0.0 61.142603
<VOICE=creaky> 61.142603 61.397647
<VOICE=modal> 61.397647 176.705681
```

#### Wavs

Sound clips can be extracted from each `Track` instance if it is created with
`load_wavs=True`.

```python
speaker = buckeye.Speaker('speakers/s01.zip', load_wavs=True)
track = speaker[0]

track.clip_wav('myclip.wav', 60.0, 62.0)
```

This will create a wav file in the current directory called `myclip.wav` which
contains the sound between 60 and 62 seconds in the track audio.
