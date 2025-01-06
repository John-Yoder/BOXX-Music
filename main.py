import rtmidi
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF
from pynput import keyboard

# --------------------------------------------
# 1. Define a MIDI note mapping for your keys
# --------------------------------------------
# You can customize these as you wish.
# Here, we're mapping typing keys to MIDI notes
# starting from Middle C (60) on the 'Z' key.

KEY_TO_NOTE = {
    'z': 60,  # C
    's': 61,  # C#
    'x': 62,  # D
    'd': 63,  # D#
    'c': 64,  # E
    'v': 65,  # F
    'g': 66,  # F#
    'b': 67,  # G
    'h': 68,  # G#
    'n': 69,  # A
    'j': 70,  # A#
    'm': 71,  # B
    ',': 72,  # C (one octave above Middle C)
    'l': 73,  # C#
    '.': 74,  # D
    ';': 75,  # D#
    '/': 76,  # E
    # Add more if you want to expand the keyboard range
}

# --------------------------------------------
# 2. Setup MIDI output
# --------------------------------------------
midiout = rtmidi.MidiOut()

# Check available MIDI ports
available_ports = midiout.get_ports()
print("Found MIDI Output Ports:", available_ports)

# Decide which port to open
if available_ports:
    # If there's at least one port, let's open port 0 (which might be loopMIDI if installed).
    print("Opening existing port 0:", available_ports[1])
    midiout.open_port(1)
else:
    # If no ports found, create a virtual port named "TypingKeyboardAsMIDI".
    # Note: On Windows, you typically need a loopback driver like loopMIDI
    # for the virtual port to show up to other applications.
    print("No MIDI ports found. Creating a virtual port named 'TypingKeyboardAsMIDI'.")
    midiout.open_virtual_port("TypingKeyboardAsMIDI")

# Keep track of which notes are "on" to prevent repeated Note On messages
active_notes = set()

# --------------------------------------------
# 3. Define callback functions for key press/release
# --------------------------------------------
def on_press(key):
    """
    Called by pynput when a key is pressed.
    """
    try:
        char = key.char.lower()  # convert to lowercase
    except AttributeError:
        # If it's a special key (Shift, Ctrl, etc.), ignore it
        return

    if char in KEY_TO_NOTE:
        note = KEY_TO_NOTE[char]
        if note not in active_notes:
            # Send Note On (status=0x90 for channel 1, note, velocity)
            midiout.send_message([NOTE_ON, note, 100])
            active_notes.add(note)

def on_release(key):
    """
    Called by pynput when a key is released.
    """
    try:
        char = key.char.lower()
    except AttributeError:
        return

    if char in KEY_TO_NOTE:
        note = KEY_TO_NOTE[char]
        if note in active_notes:
            # Send Note Off (status=0x80 for channel 1, note, velocity=0)
            midiout.send_message([NOTE_OFF, note, 0])
            active_notes.remove(note)

# --------------------------------------------
# 4. Start listening for keyboard input
# --------------------------------------------
print("Starting keyboard-to-MIDI.")
print("Press keys (Z, X, C, etc.) to trigger MIDI notes.")
print("Press Ctrl+C in the console to stop, or close the window.")

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
