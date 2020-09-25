import pokeapi
from pokeapi import EncodedIndex, START_TOKEN, END_TOKEN, GPT2_SIMPLE_SAMPLE_DIVIDER
# import gpt_2_simple as gpt2
import os
import math
from enum import Enum
from collections import defaultdict, OrderedDict
import time

REPORTS_DIR = "reports"

class FilenameData(Enum):
    RUN = 0
    ROUNDS = 1
    TIME = 2
    TEMP = 3
    K = 4
    P = 5


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever


def remove_suffix(text, suffix):
    if text.endswith(suffix):
        return text[:len(suffix)]
    return text  # or whatever


def tokenize_encoded_str(encoded_str):
    content = remove_suffix(remove_prefix(encoded_str, START_TOKEN), END_TOKEN)
    fields = content.split("|")
    fields = list(map(lambda f: f.strip(), fields))
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
        self.filename = os.path.basename(filename)

        self.perfect = True
        self.field_counts = []
        for l in range(len(EncodedIndex)):
            instance_count = len(data.get(l, []))
            self.field_counts.append(instance_count)
            if instance_count is not 1:
                self.perfect = False
        info = self.filename.split("_")
        try:
            self.run = info[0]
            self.rounds = int(info[1])
            self.time = int(info[2])
            self.temp = float(info[3][len("temp")])
            self.k = int(info[4][len("k")])
            self.p = float(info[5][len("p")])
        except (IndexError, ValueError) as e:
            # TODO sorry
            self.run = ""
            self.rounds = 0
            self.time = 0
            self.temp = 0.0
            self.k = 0
            self.p = 0.0
            # print("unexpected filename format: " + self.filename + ", " + str(e))

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

    def filename_info(self, enum):
        if enum is FilenameData.RUN:
            return self.run
        elif enum is FilenameData.ROUNDS:
            return self.rounds
        elif enum is FilenameData.TIME:
            return self.time
        elif enum is FilenameData.TEMP:
            return self.temp
        elif enum is FilenameData.K:
            return self.k
        elif enum is FilenameData.P:
            return self.p
        raise TypeError("oops missing enum")

    def field_print(self, field):
        return " / ".join(self.get_cols(field.value))

    def quick_print(self, sep="|"):
        out_lst = []
        for field in list(EncodedIndex):
            out_lst.append(self.field_print(field))
        return sep.join(out_lst)


# name UE type E cat U2E description E, habitat U, shape, color, height, weight
# def viable(self, valentries, must_be_unique=(EncodedIndex.NAME, EncodedIndex.CATEGORY), must_be_present=(EncodedIndex.TYPES, EncodedIndex.CATEGORY, EncodedIndex.DESCRIPTION)):
#     for unique_field in must_be_unique:
#         if not self.is_field_unique(field, )


class SampleGroupReport:
    CHECK_FIELDS = (
        EncodedIndex.NAME, EncodedIndex.CATEGORY, EncodedIndex.SHAPE, EncodedIndex.HABITAT, EncodedIndex.TYPES,
        EncodedIndex.COLOR)

    def __init__(self, samples, entries):
        self.samples = samples
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
            entry_field_values = map_samples_to_fields(self.entries.samples, field)
            values = list(filter(lambda sam: isinstance(sam, str), entry_field_values))
        return SampleGroupReport(list(filter(lambda sample: sample.is_field_unique(field, values), self.samples)),
                                 self.entries)

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

    def average_field_length(self, field):
        lengths = filter(lambda s: len(s), map_samples_to_fields(self.samples, field))

    def __len__(self):
        return len(self.samples)

    def count(self):
        return len(self)

    def filter(self, func):
        return SampleGroupReport(list(filter(func, self.samples)), self.entries)

    def map(self, func):
        return list(map(func, self.samples))

    def multi_filter(self, *args):
        filtered_output = [[]] * len(args)
        for sample in self.samples:
            for predicate_index, predicate in enumerate(args):
                if predicate(sample):
                    filtered_output[predicate_index].append(sample)
        return filtered_output

    def get_permutation(self, run="gpoke4a", temp=0.7, k=0, p=0.0, delta=0.001):
        return self.filter(lambda s: run == s.run
                                     and (math.isclose(temp, s.temp, rel_tol=delta)
                                          and (k == s.k)
                                          and (math.isclose(p, s.p, rel_tol=delta))))

    def partition(self, map_func):
        lst_dict = defaultdict(list)
        for s in self.samples:
            lst_dict[map_func(s)].append(s)
        out_dict = OrderedDict()
        for rounds in sorted(lst_dict.keys()):
            out_dict[rounds] = SampleGroupReport(lst_dict[rounds], self.entries)
        return out_dict

    def poor_plot(self, report_func, title=None):
        out = []
        if title is not None:
            out.append(title)
        permutations = self.partition(SgrUtil.non_rounds)
        for permutation, permutation_report in permutations.items():
            permutation_out = [str(permutation)]
            permutations_at_step = permutation_report.partition(SgrUtil.rounds)
            for permutation_step, permutation_at_step_report in permutations_at_step.items():
                permutation_out.append(str(permutation_step) + " : " + report_func(permutation_at_step_report))
            out.append(", ".join(permutation_out))
        return "\n".join(out)

    def sorted(self):
        return sorted(self.samples, key=lambda s: (s.run, s.temp, s.k, s.p, s.time, s.rounds))

    def ratio_str(self, number, total=None):
        if total is None:
            total = self.count()
        return "{0:}/{1:} ({2:0.2f}%)".format(number, total, (number / total) * 100)

    def field_nums_report(self, check_fields=CHECK_FIELDS, sep="\n"):
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
            strout = strout + sep
        for field in check_fields:  # print actual uniques
            uniques = self.unique(field)
            unique_field_values = map_samples_to_fields(uniques.samples, field)
            strout = strout + field.name + " - uniques: " + str(unique_field_values) + "\n"

        return strout

    def to_field_values(self, field):
        return map_samples_to_fields(self.samples, field)

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
        strout = strout + self.field_nums_report(fields, sep=sep)

        return strout

    def mons(self):
        text = "\n".join(self.map(SgrUtil.print))
        return text


class SgrUtil:
    @staticmethod
    def rounds(s):
        return s.rounds

    @staticmethod
    def non_rounds(s):
        return (s.run, s.temp, s.k, s.p)

    @staticmethod
    def filename(s):
        return s.filename

    @staticmethod
    def print(s):
        return s.quick_print()

    @staticmethod
    def report_unique_factory(field):
        return lambda sr: sr.ratio_str(len(sr.unique(field)))


def decode_file(filename, entries=None):
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


def decode_file_group(filenames, entries, to_file=False):
    starttime = time.time()
    cumulative_samples = []
    for sample_file in filenames:
        try:
            filestarttime = time.time()
            report = decode_file(sample_file, entries)
            cumulative_samples.extend(report.samples)
            if to_file:
                report_text = report.full_report()
                cur_path = os.path.dirname(os.path.realpath(__file__))
                report_filepath = os.path.join(cur_path, REPORTS_DIR, os.path.split(sample_file)[1])
                with open(report_filepath, "w") as report_file:
                    report_file.write(report_text)
                    print("wrote report to {}".format(report_filepath))
            else:
                print("Parsed {} in {}s".format(sample_file, time.time() - filestarttime))
                # print("{}: {}".format(sample_file, report_text))
        except IndexError as e:
            print("problem reading file: " + str(e))
    print("total decode time: {}".format(time.time() - starttime))
    cumulative_report = SampleGroupReport(cumulative_samples, entries)
    return cumulative_report


def write_mons(report):
    for filename, file_report in report.partition(SgrUtil.filename).items():
        mon_filename = os.path.join(REPORTS_DIR, "mon_{}".format(filename))
        with open(mon_filename, "w") as mon_file:
            mon_file.write(file_report.mons())
            print("wrote mons to {}".format(mon_filename))


# dex_entries = pokeapi.get_pokedex_entries()  # prerequisite pokedata
training_data = decode_file("poke_data.txt")
# get files to report on
dir_path = os.path.dirname(os.path.realpath(__file__))
target_path = "/out/gpoke4a/"
f = []
for (dirpath, dirnames, filenames) in os.walk(dir_path + target_path):
    full_filenames = []
    for fn in filenames:
        # if fn.endswith("temp0.7_k0_p0.0.txt"):
        if fn.endswith(".txt"):
            full_filenames.append(os.path.join(dirpath, fn))
    f.extend(full_filenames)
    break

write_reports = True
tempstart = time.time()
all_reports = decode_file_group(f, training_data, write_reports)
if write_reports:
    write_mons(all_reports)
for check_field in [EncodedIndex.NAME, EncodedIndex.CATEGORY, EncodedIndex.HABITAT, EncodedIndex.DESCRIPTION]:
    print(check_field)
    print(all_reports.poor_plot(SgrUtil.report_unique_factory(check_field)))

print("total time {} for {} samples".format(time.time() - tempstart, all_reports.count()))
# for rounds, sr in all_reports.partition(lambda s: s.rounds).items():
#     uniques = sr.unique(EncodedIndex.NAME)
#     print(str(rounds) + " : " + sr.ratio_str(len(uniques), sr.count()) + " " + ", ".join(
#         uniques.to_field_values(EncodedIndex.NAME)))
# print("\n".join(all_reports.filter(lambda s:  s.rounds == 3000).unique(EncodedIndex.NAME).map(lambda s: s.quick_print())))
# vanilla_temps = sorted(list(filter(lambda s: s, all_reports
