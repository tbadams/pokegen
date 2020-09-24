import pokeapi

import random

random.seed(802)  # arbitrary
entries = pokeapi.get_pokedex_entries()
names = pokeapi.get_pokemon_names(entries)

# Encode and duplicate entries to avoid overfitting
NUM_DUPLICATES = 2
encoded_entries = []
for entry in entries:
    for j in range(NUM_DUPLICATES):
        encoded_entries.append(entry.encode() + "\n")
random.shuffle(encoded_entries)  # shuffle to try and avoid it seeing large scale pattern

pokeapi.lines_to_file("poke_names" + pokeapi.VERSION, names)  # write names
pokeapi.write_display_entries(entries, "poke_dex")
# Actual gen data
pokeapi.get_stats("encoded data", encoded_entries)
pokeapi.lines_to_file("poke_data", encoded_entries)
pokeapi.lines_to_file("poke_data" + pokeapi.VERSION, encoded_entries)