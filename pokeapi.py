import requests
import json
import os
import math
import random
from enum import Enum

VERSION = "4b"

POKEFILE = "pokeapi/pokefile.json"
POKE_PREFIX = "pokeapi/poke"

START_TOKEN = "<|startoftext|>"
END_TOKEN = "<|endoftext|>"
GPT2_SIMPLE_SAMPLE_DIVIDER = '====================\n'

INDENT = 4

base_url = "https://pokeapi.co/api/v2/"
pokemon_path = base_url + "pokemon/"
param_limit = "limit"
KEY_URL = "url"
KEY_SPECIES = "species"
KEY_NAME = "name"
KEY_TYPE = "type"
KEY_LANGUAGE = "language"


# Encoded indexes
class EncodedIndex(Enum):
    NAME = 0
    CATEGORY = 1
    TYPES = 2
    ABILITIES = 3
    MOVES = 4
    HEIGHT = 5
    WEIGHT = 6
    COLOR = 7
    SHAPE = 8
    HABITAT = 9
    DESCRIPTION = 10

    def label(self, field_text):
        type_to_label = {
            EncodedIndex.TYPES: "Type: {}",
            EncodedIndex.ABILITIES: "Abilities: {}",
            EncodedIndex.MOVES: "Moves: {}",
            EncodedIndex.HEIGHT: "Height: {}",
            EncodedIndex.WEIGHT: "Weight: {}",
            EncodedIndex.COLOR: "Color: {}",
            EncodedIndex.SHAPE: "Shape {}",
            EncodedIndex.HABITAT: "Habitat: {}"
        }
        if self in type_to_label:
            return type_to_label[self].format(field_text)
        return field_text


def get_pokemon():
    outfile = open(POKEFILE, "w")

    all_pokes_response = requests.get(pokemon_path, {param_limit: 1500})
    all_pokes_data = all_pokes_response.json()
    outfile.write(json.dumps(all_pokes_data, indent=INDENT))
    count = all_pokes_data["count"]
    print("wrote master list of pokemon to '" + POKEFILE + "', count=" + str(count))
    results = all_pokes_data["results"]

    error_count = 0
    for i in range(0, count):
        filename = POKE_PREFIX + str(i) + ".json"
        existing_data = os.path.exists(filename)
        changed = False
        try:
            if os.path.exists(filename):
                file = open(filename, "r")
                file_text = file.read()
                poke_data = json.loads(file_text)
                # print("pokemon " + str(i) + "is cached as " + filename)
            else:
                changed = True
                url = results[i].get(KEY_URL)
                poke_response = requests.get(url)
                poke_data = poke_response.json()
                print("got pokemon " + str(i) + " from endpoint " + url)

            # Get flavour texts
            species_data = poke_data[KEY_SPECIES]
            if KEY_URL in species_data.keys():
                # Need to retrieve
                url = species_data[KEY_URL]
                species_response = requests.get(url)
                print("got species for " + str(i) + " from " + url)
                species_data = species_response.json()
                poke_data[KEY_SPECIES] = species_data
                changed = True

            if changed:
                file = open(filename, "w")
                file.write(json.dumps(poke_data, indent=INDENT))
                print("wrote pokemon to file " + filename)

            # Abilities?
            # Moves?

        except (ConnectionError, ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError) as e:
            error_count = error_count + 1
            print("connection error om pokemon " + str(i) + "attempting to continue...")
        except json.JSONDecodeError as e:
            os.remove(filename)
            print("removed " + filename + ", bad json: " + str(e))
    num_complete = min(count, 893) - error_count  # above 893 is variations right now
    print("Now have " + str(num_complete) + " pokemon, " + str(error_count) + " errors.")
    return num_complete


category_overrides = {
    "meltan": "Hex Nut Pokémon",
    "melmetal": "Hex Nut Pokémon",
    "grookey": "Chimp Pokémon",
    "thwackey": "Beat Pokémon",
    "rillaboom": "Drummer Pokémon",
    "scorbunny": "Rabbit Pokémon",
    "raboot": "Rabbit Pokémon",
    "cinderace": "Striker Pokémon",
    "sobble": "Water Lizard Pokémon",
    "drizzile": "Water Lizard Pokémon",
    "inteleon": "Secret Agent Pokémon",
    "skwovet": "Cheeky Pokémon",
    "greedent": "Greedy Pokémon",
    "rookidee": "Tiny Bird Pokémon",
    "corvisquire": "Raven Pokémon",
    "corviknight": "Raven Pokémon",
    "blipbug": "Larva Pokémon",
    "dottler": "Radome Pokémon",
    "orbeetle": "Seven Spot Pokémon",
    "nickit": "Fox Pokémon",
    "thievul": "Fox Pokémon",
    "gossifleur": "Flowering Pokémon",
    "eldegoss": "Cotton Bloom Pokémon",
    "wooloo": "Sheep Pokémon",
    "dubwool": "Sheep Pokémon",
    "chewtle": "Snapping Pokémon",
    "drednaw": "Bite Pokémon",
    "yamper": "Puppy Pokémon",
    "boltund": "Dog Pokémon",
    "rolycoly": "Coal Pokémon",
    "carkol": "Coal Pokémon",
    "coalossal": "Coal Pokémon",
    "applin": "Apple Core Pokémon",
    "flapple": "Apple Wing Pokémon",
    "appletun": "Apple Nectar Pokémon",
    "silicobra": "Sand Snake Pokémon",
    "sandaconda": "Sand Snake Pokémon",
    "cramorant": "Gulp Pokémon",
    "arrokuda": "Rush Pokémon",
    "barraskewda": "Skewer Pokémon",
    "toxel": "Baby Pokémon",
    "toxtricity": "Punk Pokémon",
    "sizzlipede": "Radiator Pokémon",
    "centiskorch": "Radiator Pokémon",
    "clobbopus": "Tantrum Pokémon",
    "grapploct": "Tantrum Pokémon",
    "sinistea": "Black Tea Pokémon",
    "polteageist": "Black Tea Pokémon",
    "hatenna": "Calm Pokémon",
    "hattrem": "Serene Pokémon",
    "hatterene": "Silent Pokémon",
    "impidimp": "Wily Pokémon",
    "morgrem": "Devious Pokémon",
    "grimmsnarl": "Bulk Up Pokémon",
    "obstagoon": "Blocking Pokémon",
    "perrserker": "Viking Pokémon",
    "cursola": "Coral Pokémon",
    "sirfetch": "Wild Duck Pokémon",
    "mr": "Comedian Pokémon",
    "runerigus": "Grudge Pokémon",
    "milcery": "Cream Pokémon",
    "alcremie": "Cream Pokémon",
    "falinks": "Formation Pokémon",
    "pincurchin": "Sea Urchin Pokémon",
    "snom": "Worm Pokémon",
    "frosmoth": "Frost Moth Pokémon",
    "stonjourner": "Big Rock Pokémon",
    "eiscue": "Penguin Pokémon",
    "indeedee": "Emotion Pokémon",
    "morpeko": "Two-Sided Pokémon",
    "cufant": "Copperderm Pokémon",
    "copperajah": "Copperderm Pokémon",
    "dracozolt": "Fossil Pokémon",
    "arctozolt": "Fossil Pokémon",
    "dracovish": "Fossil Pokémon",
    "arctovish": "Fossil Pokémon",
    "duraludon": "Alloy Pokémon",
    "dreepy": "Lingering Pokémon",
    "drakloak": "Caretaker Pokémon",
    "dragapult": "Stealth Pokémon",
    "zacian": "Warrior Pokémon",
    "zamazenta": "Warrior Pokémon",
    "eternatus": "Gigantic Pokémon",
    "kubfu": "Wushu Pokémon",
    "urshifu": "Wushu Pokémon",
    "zarude": "Rogue Monkey Pokémon"

}  # dataset missing some fields


class PokedexEntry:
    #  category
    #  egg_groups
    def __init__(self, data, language="en"):
        self.name = data[KEY_NAME]
        self.height_dm = data["height"]
        self.weight_hg = data["weight"]
        types = data["types"]
        self.type1 = types[0][KEY_TYPE][KEY_NAME]
        if len(types) > 1:
            self.type2 = types[1][KEY_TYPE][KEY_NAME]
        else:
            self.type2 = None
        self.moves = []
        for move in data["moves"]:
            self.moves.append(move["move"][KEY_NAME])  # TODO display
            # for vgd in move["version_group_details"]:

        # abilities
        self.abilities = []
        for ability in data["abilities"]:
            self.abilities.append(ability["ability"][KEY_NAME])  # TODO display name
        # held items

        # species stuff
        species_data = data[KEY_SPECIES]
        missing = []

        color = species_data["color"]
        if color is not None:
            self.color = color[KEY_NAME]
        else:
            self.color = None
            missing.append("color")

        habitat = species_data["habitat"]
        if habitat is not None:
            self.habitat = habitat[KEY_NAME]
        else:
            self.habitat = None
            missing.append("habitat")

        shape = species_data["shape"]
        if shape is not None:
            self.shape = shape[KEY_NAME]
        else:
            self.shape = None
            missing.append("shape")

        # self.egg_groups

        self.display_name = None
        for localized_name in species_data["names"]:
            if localized_name[KEY_LANGUAGE][KEY_NAME] == language:
                self.display_name = localized_name[KEY_NAME]
        if self.display_name is None:
            self.display_name = data[KEY_NAME].capitalize()
        if self.display_name == "Mr":
            self.display_name = "Mr. Rime"

        self.category = None
        for genus in species_data["genera"]:
            if genus[KEY_LANGUAGE][KEY_NAME] == language:
                self.category = genus["genus"]
        if self.category is None:
            self.category = category_overrides[self.name]

        self.descriptions = []
        for flavor in species_data["flavor_text_entries"]:
            if flavor[KEY_LANGUAGE][KEY_NAME] == language:
                flavor_text = flavor["flavor_text"].replace("\f", " ").replace("\n", " ").replace("  ", " ")
                if flavor_text not in self.descriptions:
                    self.descriptions.append(flavor_text)

        # validation
        if len(self.descriptions) == 0:
            raise TypeError("At least one description required.")

        if len(missing) > 0:
            print(self.name + " is missing " + ", ".join(missing))

    def category_str(self):
        if self.category is None:
            return ""
        return self.category

    def types_str(self):
        if self.type2 is not None:
            return self.type1 + " " + self.type2
        return self.type1

    def height_str(self):
        return str(math.floor(self.height_dm / 10)) + "." + str(self.height_dm % 10) + " m"

    def weight_str(self):
        return str(math.floor(self.weight_hg / 10)) + "." + str(self.weight_hg % 10) + " kg"

    def description(self):
        return random.choice(self.descriptions)
        # out = ""
        # for text in self.descriptions:
        #     out = out + text + " "
        # return out

    def moves_str(self):
        return ", ".join(random.choices(self.moves, k=min(4, len(self.moves))))

    def color_str(self):
        if self.color is not None:
            return self.color
        return ""

    def shape_str(self):
        if self.shape is not None:
            return self.shape
        return ""

    def habitat_str(self):
        if self.habitat is not None:
            return self.habitat
        return ""

    def get_field(self, field):
        field_value = None
        if field is EncodedIndex.NAME:
            field_value = self.display_name
        elif field is EncodedIndex.CATEGORY:
            field_value = self.category
        elif field is EncodedIndex.TYPES:
            field_value = self.types_str()
        elif field is EncodedIndex.CATEGORY:
            field_value = ", ".join(self.abilities)
        elif field is EncodedIndex.MOVES:
            field_value = ", ".join(self.moves)
        elif field is EncodedIndex.HEIGHT:
            field_value = self.height_str()
        elif field is EncodedIndex.WEIGHT:
            field_value = self.weight_str()
        elif field is EncodedIndex.COLOR:
            field_value = self.color
        elif field is EncodedIndex.SHAPE:
            field_value = self.shape
        elif field is EncodedIndex.HABITAT:
            field_value = self.habitat
        elif field is EncodedIndex.DESCRIPTION:
            field_value = self.description()
        if field_value is None:
            return ""
        return field_value


    def encode(self):
        fields = ["00{}".format(self.display_name),
                  "01{}".format(self.category_str()),
                  "02{}".format(self.types_str()),
                  "03{}".format(", ".join(self.abilities)),
                  "04{}".format(self.moves_str()),
                  "05{}".format(self.height_str()),
                  "06{}".format(self.weight_str()),
                  "07{}".format(self.color_str()),
                  "08{}".format(self.shape_str()),
                  "09{}".format(self.habitat_str()),
                  "10{}".format(self.description())]
        random.shuffle(fields)
        return START_TOKEN + "|".join(fields) + END_TOKEN

    def to_str_lines(self): # TODO de-duplicate
        out = [
            "/========\\",
            self.display_name]
        if self.category is not None:
            out.append(self.category)
        out.extend([
            "Type: " + self.types_str(),
            "Abilities: {}".format(", ".join(self.abilities)),
            "Moves: {}".format(self.moves_str()),
            "Height: " + self.height_str(),
            "Weight: " + self.weight_str()])
        if self.color is not None:
            out.append("Color: " + self.color)
        if self.shape is not None:
            out.append("Shape: " + self.shape)
        if self.habitat is not None:
            out.append("Habitat: " + self.habitat)
        out.extend([
            # "Name: " + self.name.capitalize(),
            "",
            self.description(),
            "\\========/>"
        ])

        # validate
        for k in range(len(out)):
            line = out[k]
            if line is None:
                raise TypeError("None not allowed in lines for " + self.name + ": " + " ".join(out[:k]))

        # new lines
        for k in range(len(out)):
            out[k] = out[k] + "\n"

        return out

    def __str__(self) -> str:
        out = ""
        lines = self.to_str_lines()
        for line in lines:
            out = out + line + "\n"
        return out


def load_pokemon_from_file(index):
    filename = POKE_PREFIX + str(index) + ".json"
    file = open(filename, "r")
    file_text = file.read()
    return json.loads(file_text)


def get_pokemon_names(entries):
    pokenames = []
    min_name_length = 9999999
    max_name_length = 0
    total = 0
    for dex_entry in entries:
        display_name = dex_entry.display_name
        pokenames.append(display_name + "\n")
        length_this = len(display_name)
        total = total + length_this
        min_name_length = min(min_name_length, length_this)
        max_name_length = max(max_name_length, length_this)
    print("got names: min={}, max={}, avg={}".format(str(min_name_length), str(max_name_length),
                                                     str(total / len(pokenames))))
    return pokenames


def get_pokedex_entries():
    count = get_pokemon()
    real_count = 893  # after that it's variations right now, dunno how to tell from data.  hyphens maybe.
    entries = []

    print("formatting " + str(count) + " pokemon...")
    for i in range(count):
        entry = PokedexEntry(load_pokemon_from_file(i))
        entries.append(entry)
        # print("formatted " + str(i) + " - " + entry.name)
    return entries


def get_encoded(entries, num_duplicates, shuffle=True):
    # Encode and duplicate entries to avoid overfitting
    encoded_entries = []
    for entry in entries:
        for j in range(num_duplicates):
            encoded_entries.append(entry.encode() + "\n")
    if shuffle:
        random.shuffle(encoded_entries)  # shuffle to try and avoid it seeing large scale pattern
    return encoded_entries


def write_encoding_template(num_fields=10, num_lines=10000):
    fields = []
    for i in range(num_fields):
        out = ""
        if i < 10:
            out = out + "0"
        fields.append(out + str(i))
    random.shuffle(fields)


def get_stats(dataname, lines):
    count = 0
    total_length = 0
    min_length = 9999999
    max_length = 0
    for line in lines:
        count = count + 1
        entry_length = len(str(line))
        total_length = total_length + entry_length
        max_length = max(max_length, entry_length)
        min_length = min(min_length, entry_length)
    print(dataname + ":count - " + str(count) + ", min - " + str(min_length) + ", max - " + str(max_length)
          + ", average length = " + str(total_length / count))


def lines_to_file(filename, lines, extension=".txt"):
    utf8_lines = []
    for k in range(len(lines)):
        utf8_lines.append(lines[k].encode('utf-8'))

    with open(filename + extension, "wb") as afile:
        afile.writelines(utf8_lines)


def write_display_entries(entries, out_filename):
    line_data = []
    for entry in entries:
        line_data.extend(entry.to_str_lines())
        line_data.append("\n")
        # print("wrote " + " - " + entry.name)
    lines_to_file(out_filename, line_data)  # Common name copy for actual use
    lines_to_file(out_filename + VERSION, line_data)  # Versioned name copy for archiving
