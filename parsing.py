from pokeapi import EncodedIndex, START_TOKEN, END_TOKEN, GPT2_SIMPLE_SAMPLE_DIVIDER
import os
import math
import time
from sample import SampleReport, SampleGroupReport

REPORTS_DIR = "reports"


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


# name UE type E cat U2E description E, habitat U, shape, color, height, weight
# def viable(self, valentries, must_be_unique=(EncodedIndex.NAME, EncodedIndex.CATEGORY), must_be_present=(EncodedIndex.TYPES, EncodedIndex.CATEGORY, EncodedIndex.DESCRIPTION)):
#     for unique_field in must_be_unique:
#         if not self.is_field_unique(field, )


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


class SgrUtil:

    @staticmethod
    def filename(s):
        return s.filename

    @staticmethod
    def quick_print(s):
        return s.quick_print()

    @staticmethod
    def overfit_focus(sample):
        return sample.k is 0 and math.isclose(0, sample.p, rel_tol=0.001)


def filter_ks_and_ps(sgr):
    return sgr.filter(lambda s: s.filename.c)


def report_unique_factory(field):
    return lambda sr: sr.ratio_str(len(sr.unique(field)))


def report_field_length_stats_factory(field):
    return lambda sample_report: str(sample_report.get_field_length_stats(field))


def parse_outputs(*dirs, fname_filter=None, sample_filter=None, file_reports=False, mons_reports=False):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    f = []
    # get files to report on
    for target_path in dirs:
        for (dirpath, dirnames, filenames) in os.walk(dir_path + target_path):
            full_filenames = []
            for fn in filenames:
                if os.path.basename(fn).startswith("gpoke") and fn.endswith(".txt"):
                    full_filenames.append(os.path.join(dirpath, fn))
            f.extend(full_filenames)
            break
    if fname_filter is not None:
        unfiltered_count = len(f)
        f = list(filter(fname_filter, f))
        print("Filtered from {} to {} files.".format(unfiltered_count, len(f)))
    # get real data, for duplicate checking
    training_data = decode_file("poke_data.txt")

    tempstart = time.time()
    all_reports = decode_file_group(f, training_data.to_unique_field_entries(), file_reports)
    if sample_filter is not None:
        unfiltered_count = all_reports.count()
        all_reports = all_reports.filter(sample_filter)
        print("Filtered from {} to {} samples.".format(unfiltered_count, all_reports.count()))
    if mons_reports:
        write_mons(all_reports)
    for check_field in [EncodedIndex.NAME, EncodedIndex.CATEGORY, EncodedIndex.HABITAT, EncodedIndex.DESCRIPTION]:
        print(check_field)
        print(all_reports.poor_plot(report_unique_factory(check_field)))

    print("total time {} for {} samples".format(time.time() - tempstart, all_reports.count()))
    # print(all_reports.full_report())
    # for rounds, sr in all_reports.partition(lambda s: s.rounds).items():
    #     uniques = sr.unique(EncodedIndex.NAME)
    #     print(str(rounds) + " : " + sr.ratio_str(len(uniques), sr.count()) + " " + ", ".join(
    #         uniques.to_field_values(EncodedIndex.NAME)))
    # print("\n".join(all_reports.filter(lambda s:  s.rounds == 3000).unique(EncodedIndex.NAME).map(lambda s: s.quick_print())))
    # vanilla_temps = sorted(list(filter(lambda s: s, all_reports
    return all_reports

parse_outputs("/out/gpoke4a/", "/out/gpoke4b/", "/out/gpoke4c/", sample_filter=SgrUtil.overfit_focus)
