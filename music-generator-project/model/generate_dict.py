from collections import Counter
import pickle
import glob
import utils
import time

def extract_events(input_path, emotion, chord=True):
    note_items, tempo_items = utils.read_items(input_path)
    note_items = utils.quantize_items(note_items)
    max_time = note_items[-1].end
    if chord:
        chord_items = utils.extract_chords(note_items)
        items = chord_items + tempo_items + note_items
    else:
        items = tempo_items + note_items
    groups = utils.group_items(items, max_time)
    events = utils.item2event(groups, emotion)
    return events

all_elements= []
for midi_file in glob.glob("../dataset/*.midi", recursive=True):
    emotion = midi_file.split("\\")[1].split("_")[0]
    events = extract_events(midi_file, emotion)  
    print("Creating event for: ", midi_file)
    for event in events:
        element = '{}_{}'.format(event.name, event.value)
        all_elements.append(element)

counts = Counter(all_elements)
event2word = {c: i for i, c in enumerate(counts.keys())}
word2event = {i: c for i, c in enumerate(counts.keys())}
pickle.dump((event2word, word2event), open('train-checkpoint-chord/dictionary.pkl', 'wb'))
print("=================================================")
print("Generating dict completed at: ", time.strftime("%H:%M:%S"))
print("=================================================")
