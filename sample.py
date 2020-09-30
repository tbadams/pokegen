from collections import defaultdict, OrderedDict
from pokeapi import EncodedIndex
import math
import os
from os import path
from util import get_length_stats


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
        filename_no_extension = path.splitext(self.filename)[0]
        info = filename_no_extension.split("_")
        try:
            self.run = info[0]
            self.rounds = int(info[1])
            self.time = info[2]
            # self.filename is not "poke_data.txt"
            temp_numeric = info[3][len("temp"):]
            self.temp = float(temp_numeric)
            self.k = int(info[4][len("k"):])
            self.p = float(info[5][len("p"):])
        except (IndexError, ValueError) as e:
            # TODO sorry
            self.run = ""
            self.rounds = 0
            self.time = 0
            self.temp = 0.0
            self.k = 0
            self.p = 0.0
            # print("unexpected filename format: " + self.filename + ", " + str(e))

    def has_valid_field(self, field):
        index = field.value
        return index in self.data and len(self.data[index]) == 1

    def get_valid_field(self, field):  # no validation
        return self.get_cols(field)[0]

    def is_field_unique(self, field, values):
        for value in self.get_cols(field):
            if value not in values:
                return True

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

    def get_cols(self, field):
        if field is None:
            return self.data.get(None, [])
        return self.data.get(field.value, [])

    def field_print(self, field, value_sep=" / "):

        return value_sep.join(list(filter(lambda col: len(col.strip()) > 0, self.get_cols(field))))

    def quick_print(self, sep="|", value_sep=" / ", fields=None):
        if fields is None:
            fields = list(EncodedIndex)
        out_lst = []
        for field in fields:
            field_text = self.field_print(field, value_sep)
            if len(field_text) > 0:
                out_lst.append(field.label(field_text))
        return sep.join(out_lst)


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

    def unique(self, field):
        values = self.entries[field]
        return SampleGroupReport(list(filter(lambda sample: sample.is_field_unique(field, values), self.samples)),
                                 self.entries)

    def to_unique_field_entries(self):
        unique_field_map = {}
        for field in list(EncodedIndex):
            unique_field_map[field] = set()
        for s in self.samples:
            for field in list(EncodedIndex):
                for value in s.get_cols(field):
                    unique_field_map[field].add(value)
        return unique_field_map

    def have_invalid_field_values(self):
        return list(filter(lambda sample: len(sample.get_cols(None)) > 0, self.samples))

    def field_is_singular(self, field):
        return list(filter(lambda sample: sample.has_valid_field(field), self.samples))

    def field_is_missing(self, field):
        return list(filter(lambda sample: len(sample.get_cols(field)) < 1, self.samples))

    def field_has_extras(self, field):
        return list(filter(lambda sample: len(sample.get_cols(field)) > 1, self.samples))

    def field_is_empty(self, field):
        return list(filter(lambda s: s.get_valid_field(field) is '', self.field_is_singular(field)))

    def get_field_length_stats(self, field):
        return get_length_stats(None, self.get_field_values(field, False))

    def get_field_values(self, field, as_set=True, strip=True):
        values = []
        for s in self.samples:
            values.extend(s.get_cols(field))
        if strip:
            values = [value.strip() for value in values]
        if as_set:
            return set(values)
        else:
            return values


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
            unique_field_values = uniques.get_field_values(field)
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
    def quick_print(s):
        return s.quick_print()

    @staticmethod
    def print(s):
        return "{}\n".format(s.quick_print(sep="\n", value_sep="\n"))

    @staticmethod
    def report_unique_factory(field):
        return lambda sr: sr.ratio_str(len(sr.unique(field)))

    @staticmethod
    def overfit_focus(sample):
        return sample.k is 0 and math.isclose(0, sample.p, rel_tol=0.001)
