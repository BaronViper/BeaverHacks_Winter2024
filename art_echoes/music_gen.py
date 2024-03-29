from krita import Krita
from midiutil import MIDIFile
from mingus.core import scales, chords
from itertools import groupby

# For reference to convert notes to numbers
notes = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
OCTAVES = list(range(11))
NOTES_IN_OCTAVE = len(notes)

def swap_accidentals(note):
    """
    Changes any accidental notes to more common note counterparts.

    :param note: Note to check for swap

    :return: Swapped note
    """
    if note == 'Db':
        return 'C#'
    if note == 'D#':
        return 'Eb'
    if note == 'E#':
        return 'F'
    if note == 'Gb':
        return 'F#'
    if note == 'G#':
        return 'Ab'
    if note == 'A#':
        return 'Bb'
    if note == 'B#':
        return 'C'
    return note

def note_to_number(note: str, octave: int) -> int:
    """
    For converting note letters to numbers

    :param note: Note to convert
    :param octave: Octave of note

    :return: Number corresponding to note
    """

    note = swap_accidentals(note)
    note = notes.index(note)
    note += (NOTES_IN_OCTAVE * octave)
    return note

def number_to_note(num: int) -> str:
    """
    Convert a number to a note. For development purposes.

    :param num: Number to convert to note

    :return: Note derived from number
    """
    num %= 1000
    div = len(notes)
    octave = int(num // div)
    letter = notes[int(num % div)]
    note =  letter + str(octave)
    return note

def key_creator(base_note: str):
    """
    Updates list of notes to only the notes in the given key. This is to be run after the first note of a stroke is determined.

    :param base_note: A note in str version. Refer to function get_song_note output 'note_str'

    :return: None
    """
    note_key = scales.get_notes(base_note)
    return note_key

def get_first_note(x_cor: int, y_cor: int) -> dict:
    """
    Get the first note corresponding to the first coordinate.

    :param x_cor: X-coordinate
    :param y_cor: Y-coordinate

    :return: A dictionary of the note in str and int form, as well as its octave
    """
    x_cor %= 1000
    y_cor %= 1000
    div = 1000 / len(notes)
    start_note = notes[int(x_cor // div)]
    if y_cor in range(250, 750):
        start_octave = 4
    elif y_cor in range(751, 1000):
        start_octave = 5
    else:
        start_octave = 3
    return {"note_num": note_to_number(start_note, start_octave), "note_str": start_note, "octave": start_octave}

def get_note(x_cor: int, y_cor: int, note_set: list) -> dict:
    """
    Get the note corresponding to some specified coordinate AFTER a key has been chosen.

    :param note_set:
    :param x_cor: X-coordinate
    :param y_cor: Y-coordinate

    :return: A dictionary of the note in str and int form, as well as its octave
    """
    x_cor %= 1000
    y_cor %= 1000
    div = 1000 / 7 # notes in a scale
    note = note_set[int(x_cor // div)]
    if y_cor in range(250, 750):
        octave = 4
    elif y_cor in range(751, 1000):
        octave = 5
    else:
        octave = 3
    return {"note_num": note_to_number(note, octave), "note_str": note, "octave": octave}

def tempo_gen(coordinates: list) -> int:
    total_difference = 0
    for n in range(1, len(coordinates)):
        total_difference += coordinates[n][0] - coordinates[n - 1][0]
    total_difference /= len(coordinates)
    return total_difference * -1 + 120

def song_gen(coordinates: list):
    """
    Generate a song from an array of coordinates

    :param coordinates: An array of tuples containing x and y coordinates

    :return: None
    """
    track = 0
    channel = 0
    time = 0  # In beats
    duration = 0.5  # In beats
    tempo = 1200  # In BPM
    volume = 100  # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(1)

    for brush_cor in coordinates:
        first_coordinate = brush_cor[0]
        start_note = get_first_note(first_coordinate[0], first_coordinate[1])
        new_notes = key_creator(start_note["note_str"])

        tempo = int(tempo_gen(brush_cor))

        music_note_array = []
        for x, y in brush_cor:
            music_note_array.append(get_note(x_cor= x, y_cor= y, note_set=new_notes)["note_num"])

        MyMIDI.addTempo(track, time, tempo)

        grouped_music_array = [list(j) for i, j in groupby(music_note_array)]
        current_time = 0
        for note_group in grouped_music_array:
            duration = 1  # Default duration for a single note
            if len(note_group) > 1:
                duration = 1 + len(note_group) / 2000  # Adjusted duration for note groups

            for note in note_group:
                MyMIDI.addNote(track, channel, note, current_time, duration, volume)
                current_time += duration

    with open(Krita.instance().getAppDataLocation() + "/sound_out.mid", "wb") as output_file:
        MyMIDI.writeFile(output_file)

    # Define paths to MIDI and MP3 files
    # midi_file = Krita.instance().getAppDataLocation() + "/sound_out.mid"
    # mp3_file = Krita.instance().getAppDataLocation() + "/sound_out.mp3"
    # print(mp3_file)
    # print(midi_file)
    #
    # # Convert MIDI to MP3
    # fs = FluidSynth()
    # fs.midi_to_audio(midi_file, mp3_file)


# ============= TESTING =============
# import random
#
# total_music = []
# def simulate_cursor_movement(duration):
#     cursor_positions = []
#     for second in range(duration):
#         x = random.randint(-500, 500)
#         y = random.randint(-500, 500)
#         cursor_positions.append((x, y))
#     total_music.append(cursor_positions)
#
# # Simulate cursor movement for 10 seconds
# duration = 10
# simulate_cursor_movement(duration)
# simulate_cursor_movement(duration)
# print(total_music)
# song_gen(total_music)