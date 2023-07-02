# Dado-Midi Create
Crea Midi file di 9 misure variando scala nota di base, random pattern e altro
## Graphical Interface - tkinter
##	Midi-Mido interface

![image DadoCrea](.DadoCrea.png)

Create MIDI file type 1, Use 5 channel

Create 10 tracks: Track0, Bass, Piano, Voice1, Voice2 and 5 for Drum

Maximum number of Measures = 9

Fixed data: 4/4 (numerator=4, denominator=4)

Minimum note length = 1/8

Maximum note length = 8/8

## Parameters

Tempo = BPM
 
Scale = Choice between some types of scales
 
Key = Choice of the basic note (tonic) (between 0 and 11)
 
Agreement = for each measure you can select the degree of respect to the base note in the different chords.
 
Chords can consist of 1 to 4 notes
 
For each note of the chord you can choose the octave and the degree (distance from tonic = 0)
 
View PianoRoll (track muting)

Editing Pattern Length and Height Note

Randomly selects Rhythmic and Melodic patterns from (few) stored patterns

It takes patterns from the grid and returns to different pattern

# Thanks
**Phython** community who have put their software and advice online.

Special thanks to the authors of **Mido** who made the possibility of creating music software using python.

