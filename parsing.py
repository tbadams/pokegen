import pokeapi
from pokeapi import EncodedIndex, START_TOKEN, END_TOKEN, GPT2_SIMPLE_SAMPLE_DIVIDER
# import gpt_2_simple as gpt2
import os


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

def map_samples_to_fields(samples, field):
    return list(map(lambda sample: sample.get_valid_field(field.value).strip(), samples))


class SampleReport:
    def __init__(self, data, filename):
        super().__init__()
        self.data = data
        self.perfect = True
        self.field_counts = []
        for l in range(len(EncodedIndex)):
            instance_count = len(data.get(l, []))
            self.field_counts.append(instance_count)
            if instance_count is not 1:
                self.perfect = False

# todo use field not index
    def has_valid_field(self, index):
        return index in self.data and len(self.data[index]) == 1

    def get_valid_field(self, index):  # no validation
        return self.get_cols(index)[0]

    def is_field_unique(self, field, values):
        if self.has_valid_field(field.value):
            field_value_tokens = self.get_valid_field(field.value).strip().upper()
            return field_value_tokens not in (pos_dup.strip().upper() for pos_dup in values) \
                   and field_value_tokens is not ''
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
    CHECK_FIELDS = (EncodedIndex.NAME, EncodedIndex.CATEGORY, EncodedIndex.SHAPE, EncodedIndex.HABITAT)

    def __init__(self, samples, entries=None):
        self.samples = samples
        if entries is None:
            entries = []
        self.entries = entries

    def perfect(self):
        return list(filter(lambda sample: sample.perfect, self.samples))

    def have_missing_fields(self):
        return list(filter(lambda sample: len(sample.get_missing_fields()) > 0, self.samples))

    def have_extra_fields(self):
        return list(filter(lambda sample: len(sample.get_extra_fields()) > 0, self.samples))

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

    def get_garbage_fields_count(self):
        return sum(list(map(lambda s: len(s.get_cols(None)), self.samples)))

    def unique(self, field, values=None):
        if values is None:
            entry_field_values = list(map(lambda entry: entry.get_field(field), self.entries))
            values = list(filter(lambda sam: isinstance(sam, str), entry_field_values))
        return list(filter(lambda sample: sample.is_field_unique(field, values), self.samples))

    def have_invalid_field_values(self):
        return list(filter(lambda sample: len(sample.get_cols(None)) > 0, self.samples))

    def field_is_singular(self, field):
        return list(filter(lambda sample: sample.has_valid_field(field.value), self.samples))

    def field_is_missing(self, field):
        return list(filter(lambda sample: len(sample.get_cols(field.value)) < 1, self.samples))

    def field_has_extras(self, field):
        return list(filter(lambda sample: len(sample.get_cols(field.value)) > 1, self.samples))

    def field_is_empty(self, field):
        return list(filter(lambda s: s.get_valid_field(field) is '', self.field_is_singular(field)))

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
        str_template = "{}: {}, "
        strout = ""
        for i_field in range(len(EncodedIndex)):
            field = EncodedIndex(i_field)
            strout = strout + field.name + ": "
            strout = strout + str_template.format("unique", self.ratio_str(len(self.unique(field))))
            strout = strout + str_template.format("valid", self.ratio_str(len(self.field_is_singular(field))))
            strout = strout + str_template.format("missing", self.ratio_str(len(self.field_is_missing(field))))
            strout = strout + str_template.format("extra", self.ratio_str(len(self.field_has_extras(field))))
            # strout = strout + str_template.format("empty", self.ratio_str(len(self.field_is_empty(field))))
            strout = strout + "\n"
        for field in check_fields:  # print actual uniques
            uniques = self.unique(field)
            unique_field_values = map_samples_to_fields(uniques, field)
            strout = strout + field.name + " - uniques: " + str(unique_field_values) + "\n"

        return strout

    def full_report(self, sep="\n", fields=CHECK_FIELDS, entries=None):
        if entries is None:
            entries = []
        strout = "\n"
        strout = "{}Perfect: {}{}".format(strout, self.ratio_str(len(self.perfect())), sep)
        strout = "{}Incomplete: {}{}".format(strout, self.ratio_str(len(self.have_missing_fields())), sep)
        strout = "{}Have Extras: {}{}".format(strout, self.ratio_str(len(self.have_extra_fields())), sep)
        strout = "{}Contain Garbage: {}{}".format(strout, self.ratio_str(len(self.have_invalid_field_values())), sep)
        strout = "{}Missing Values: {}{}".format(strout, self.get_missing_fields_count(), sep)
        strout = "{}Extra Values: {}{}".format(strout, self.get_extra_fields_count(), sep)
        strout = "{}Garbage Values: {}{}".format(strout, self.get_garbage_fields_count(), sep)
        strout = strout + self.field_nums_report(fields)

        return strout


def decode_file(filename, entries=None):
    def map_to_field(collection, field):
        return list(map(lambda x: x.get_valid_field(field.value).strip(), collection))

    if entries is None:
        entries = []
    with open(filename, "r") as fizz:
        lines = fizz.readlines()
        all_samples = []
        for line in lines:
            if not line.startswith(GPT2_SIMPLE_SAMPLE_DIVIDER):
                # gather info
                linedata = SampleReport(decode(line), filename)
                all_samples.append(linedata)
        return SampleGroupReport(all_samples, entries)


def decode_file_group(filenames, entries=None, to_file=False):
    cumulative_samples = []
    filemap = {}
    for sample_file in filenames:
        report = decode_file(sample_file, entries)
        cumulative_samples.extend(report.samples)
        filemap[sample_file] = report
        report_text = report.full_report()
        if to_file:
            cur_path = os.path.dirname(os.path.realpath(__file__))
            report_filepath = os.path.join(cur_path, "reports", os.path.split(sample_file)[1])
            with open(report_filepath, "w") as report_file:
                report_file.write(report_text)
                print("wrote report to {}".format(report_filepath))
        else:
            print("{}: {}".format(sample_file, report_text))
    cumulative_report = SampleGroupReport(cumulative_samples, entries)
    return filemap


entries = pokeapi.get_pokedex_entries()  # prerequisite pokedata
# get files to report on
dir_path = os.path.dirname(os.path.realpath(__file__))
target_path = "/out/gpoke4a/"
f = []
for (dirpath, dirnames, filenames) in os.walk(dir_path + target_path):
    full_filenames = []
    for fn in filenames:
        if fn.endswith("txt"):
            full_filenames.append(os.path.join(dirpath, fn))
    f.extend(full_filenames)
    break
all_reports = decode_file_group(f, entries)


