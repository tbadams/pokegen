import pokeapi

import random

NUM_DUPLICATES = 2
VERSION = "4b"

random.seed(802)  # arbitrary
entries = pokeapi.get_pokedex_entries()
names = pokeapi.get_pokemon_names(entries)
encoded_entries = pokeapi.get_encoded(entries, NUM_DUPLICATES)

pokeapi.lines_to_file("poke_names" + VERSION, names)  # write names
pokeapi.write_display_entries(entries, "poke_dex", VERSION)
# Actual gen data
pokeapi.get_stats("encoded data", encoded_entries)
pokeapi.lines_to_file("poke_data", encoded_entries)
pokeapi.lines_to_file("poke_data" + VERSION, encoded_entries)
