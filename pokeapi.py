import requests
import json
import os
import math
import random
from enum import Enum

VERSION = "3c"

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
        if field is EncodedIndex.NAME:
            return self.display_name
        elif field is EncodedIndex.CATEGORY:
            return self.category
        elif field is EncodedIndex.TYPES:
            return self.type1, self.type2
        elif field is EncodedIndex.CATEGORY:
            return self.abilities
        elif field is EncodedIndex.MOVES:
            return self.moves
        elif field is EncodedIndex.HEIGHT:
            return self.height_dm
        elif field is EncodedIndex.WEIGHT:
            return self.weight_hg
        elif field is EncodedIndex.COLOR:
            return self.color
        elif field is EncodedIndex.SHAPE:
            return self.shape
        elif field is EncodedIndex.HABITAT:
            return self.habitat
        elif field is EncodedIndex.DESCRIPTION:
            return self.descriptions

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

    def to_str_lines(self):
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


def write_encoding_template(num_fields=10, num_lines=10000):
    fields = []
    for i in range(num_fields):
        out = ""
        if i < 10:
            out = out + "0"
        fields.append(out + str(i))
    random.shuffle(fields)

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


def tokenize_encoded_str(encoded_str):
    def remove_prefix(text, prefix):
        if text.startswith(prefix):
            return text[len(prefix):]
        return text  # or whatever

    def remove_suffix(text, suffix):
        if text.endswith(suffix):
            return text[:len(suffix)]
        return text  # or whatever

    content = remove_suffix(remove_prefix(encoded_str, START_TOKEN), END_TOKEN)
    fields = content.split("|")
    fields.sort()
    return fields


def append_to_dict(d, idx, thing):
    if idx not in d:
        d[idx] = []
    d[idx].append(thing)


def decode(encoded_str):
    fields = tokenize_encoded_str(encoded_str)
    data = {}
    for field in fields:
        index_str = field[0:2]
        try:
            index = int(index_str)
            field_content = field[2:]
            append_to_dict(data, index, field_content)
        except (ValueError, TypeError) as e:
            append_to_dict(data, None, field)
    return data


class SampleReport:
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.perfect = True
        self.field_counts = []
        for l in range(len(EncodedIndex)):
            instance_count = len(data.get(l, []))
            self.field_counts.append(instance_count)
            if instance_count is not 1:
                self.perfect = False

    def has_valid_field(self, index):
        return index in self.data and len(self.data[index]) == 1

    def get_valid_field(self, index):  # no validation
        return self.get_cols(index)[0]

    def is_field_unique(self, field, values):
        if self.has_valid_field(field.value):
            field_value_tokens = self.get_valid_field(field.value).strip().upper()
            return field_value_tokens not in (pos_dup.strip().upper() for pos_dup in values)
        return False

    def get_missing_fields(self):
        missing_fields = []
        for ie in range(len(EncodedIndex)):
            if self.field_counts[ie] == 0:
                missing_fields.append(EncodedIndex(ie))
        return missing_fields

    def get_extra_fields(self):
        extra_fields = []
        for ie in range(len(EncodedIndex)):
            field_count = self.field_counts[ie]
            if field_count > 1:
                for num_times in range(field_count - 1):
                    extra_fields.append(EncodedIndex(ie))
        return extra_fields

    def get_cols(self, index):
        return self.data.get(index, [])


class SampleGroupReport:
    CHECK_FIELDS = (EncodedIndex.NAME, EncodedIndex.CATEGORY, EncodedIndex.SHAPE, EncodedIndex.HABITAT,
                    EncodedIndex.DESCRIPTION)

    def __init__(self, samples, entries=None):
        self.samples = samples
        if entries is None:
            entries = []
        self.entries = entries

    def perfect(self):
        return list(filter(lambda sample: sample.perfect, self.samples))

    def have_missing_fields(self):
        return list(filter(lambda sample: sample.get_missing_fields() > 0, self.samples))

    def have_extra_fields(self):
        return list(filter(lambda sample: sample.get_extra_fields() > 0, self.samples))

    def get_missing_fields_count(self):
        field_sum = 0
        for sample in self.samples:
            field_sum = field_sum + len(sample.get_missing_fields())
        return field_sum

    def get_extra_fields_count(self):
        field_sum = 0
        for sample in self.samples:
            field_sum = field_sum + len(sample.get_extra_fields())
        return field_sum

    def unique(self, field, values=None):
        if values is None:
            entry_field_values = list(map(lambda entry: entry.get_field(field), self.entries))
            values = list(filter(lambda sam: isinstance(sam, str), entry_field_values))
        return list(filter(lambda sample: sample.is_field_unique(field, values), self.samples))

    def field_is_singular(self, field):
        return list(filter(lambda sample: sample.has_valid_field(field.value), self.samples))

    def field_is_missing(self, field):
        return list(filter(lambda sample: len(sample.get_cols(field.value)) < 1, self.samples))

    def field_has_extras(self, field):
        return list(filter(lambda sample: len(sample.get_cols(field.value)) > 1, self.samples))

    def __len__(self):
        return len(self.samples)

    def count(self):
        return len(self)

    def multi_filter(self, *args):
        filtered_output = [[]] * len(args)
        for sample in self.samples:
            for predicate_index, predicate in enumerate(args):
                if predicate(sample):
                    filtered_output[predicate_index].append(sample)
        return filtered_output

    def ratio_str(self, number, total=None):
        if total is None:
            total = self.count()
        return "{0:}/{1:} ({2:0.2f}%)".format(number, total, (number / total) * 100)

    def field_nums_report(self, check_fields=CHECK_FIELDS):
        str_template = "    {}: {},"
        strout = ""
        for field in check_fields:
            strout = strout + field.name + ": "
            strout = strout + str_template.format("unique", self.ratio_str(len(self.unique(field))))
            strout = strout + str_template.format("valid", self.ratio_str(len(self.field_is_singular(field))))
            strout = strout + str_template.format("missing", self.ratio_str(len(self.field_is_missing(field))))
            strout = strout + str_template.format("extra", self.ratio_str(len(self.field_has_extras(field))))
            strout = strout + "\n"
        return strout

    def full_report(self, sep="\n", fields=CHECK_FIELDS, entries=None):
        if entries is None:
            entries = []
        strout = "\n"
        strout = "{}Perfect Samples: {}{}".format(strout, self.ratio_str(len(self.perfect())), sep)
        strout = "{}Missing Fields: {}{}".format(strout, self.get_missing_fields_count(), sep)
        strout = "{}Extra Samples: {}{}".format(strout, self.get_extra_fields_count(), sep)
        # strout = "{}\n".format(strout)
        strout = strout + self.field_nums_report(fields)

        return strout


def decode_file(filename, entries=None):
    def map_to_field(collection, field):
        return list(map(lambda x: x.get_valid_field(field.value).strip(), collection))

    if entries is None:
        entries = []
    check_unique = [EncodedIndex.NAME, EncodedIndex.CATEGORY, EncodedIndex.SHAPE, EncodedIndex.HABITAT,
                    EncodedIndex.DESCRIPTION]
    with open(filename, "r") as fizz:
        perfect_samples = 0
        num_samples = 0
        # unique = {}
        # for field_type in check_unique:
        #     unique[field_type] = []
        lines = fizz.readlines()
        all_samples = []
        for line in lines:
            if not line.startswith(GPT2_SIMPLE_SAMPLE_DIVIDER):
                # gather info
                linedata = SampleReport(decode(line))
                all_samples.append(linedata)

        #         # calculate stats
        #         num_samples = num_samples + 1
        #         if linedata.perfect:
        #             perfect_samples = perfect_samples + 1
        #         for field_type in check_unique:
        #             if linedata.is_field_unique(field_type, pokenames):
        #                 unique[field_type].append(linedata)
        # unique_fielded = {}
        # for field_type in check_unique:
        #     unique_fielded[field_type] = map_to_field(unique[field_type], field_type)
        return SampleGroupReport(all_samples, entries)


def decode_file_group(filenames, entries=None):
    cumulative_samples = []
    for sample_file in filenames:
        report = decode_file(sample_file, entries)
        print("{}: {}".format(sample_file, report.full_report()))
        cumulative_samples.extend(report.samples)
    cumulative_report = SampleGroupReport(cumulative_samples, entries)
    print(cumulative_report.full_report())


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
