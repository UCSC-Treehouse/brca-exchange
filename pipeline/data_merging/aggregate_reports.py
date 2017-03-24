#!/usr/bin/env python
"""
this scripts takes the enigma variant list and merge vcf files in a folder into
the exisitng enigma variants:
"""
import argparse
import os
import vcf
import logging
import csv
from variant_merging import (
     associate_chr_pos_ref_alt_with_item,
     BIC_FIELDS,
     COLUMN_SOURCE,
     COLUMN_GENE,
     COLUMN_GENOMIC_HGVS,
     COLUMN_VCF_CHR,
     COLUMN_VCF_POS,
     COLUMN_VCF_REF,
     COLUMN_VCF_ALT,
     CLINVAR_FIELDS,
     EX_LOVD_FIELDS,
     ESP_FIELDS,
     EXAC_FIELDS,
     FIELD_DICT,
     ENIGMA_FILE,
     GENOME1K_FIELDS,
     LOVD_FIELDS
     )


def write_reports_tsv(filename, columns, ready_files_dir):
    reports_output = open(filename, "w")

    reports_files = [ready_files_dir + r for r in get_reports_files(ready_files_dir)]

    reports = aggregate_reports(reports_files, columns)

    reports_output.write("\t".join(columns)+"\n")

    for report in reports:
        if len(report) != len(columns):
            raise Exception("mismatching number of columns in head and row")
        for ii in range(len(report)):
            if type(report[ii]) == list:
                comma_delimited_string = ",".join(str(xx) for xx in report[ii])
                report[ii] = comma_delimited_string
            elif type(report[ii]) == int:
                report[ii] = str(report[ii])
        reports_output.write("\t".join(report)+"\n")

    reports_output.close()

    print "final number of reports: %d" % len(reports)
    print "Done"


def aggregate_reports(reports_files, columns):
    # Gathers all reports from an input directory, normalizes them, and combines them into a single list.
    reports = []

    for file in reports_files:
        file_reports = normalize_reports(file, columns)
        print "finished normalizing %s" % (file)
        reports = reports + file_reports

    return reports


def get_reports_files(input_directory):
    return [f for f in os.listdir(input_directory) if os.path.isfile(os.path.join(input_directory, f)) and "ready" in f or "ENIGMA_combined_with_bx_ids" in f]


def normalize_reports(file, columns):
    filename, file_extension = os.path.splitext(file)
    if file_extension == ".vcf":
        reports = normalize_vcf_reports(file, columns, filename, file_extension)
    elif file_extension == ".tsv":
        if "ENIGMA" not in filename.upper():
            raise Exception("ERROR: received tsv file that is not for ENIGMA: %s" % (filename))
        reports = normalize_enigma_tsv_reports(file, columns, filename, file_extension)
    for report in reports:
        if len(report) != len(columns):
            report += [DEFAULT_CONTENTS] * len(FIELD_DICT[source])
    for report in reports:
        if len(report) != len(columns):
            raise Exception("mismatching number of columns in head and row")
    return reports


def normalize_vcf_reports(file, columns, filename, file_extension):
    reports = []
    reader = vcf.Reader(open(file, "r"), strict_whitespace=True)
    count = 0
    source_suffix = "ready.vcf"
    source = os.path.basename(file)[:-len(source_suffix)]
    for record in reader:
        count += 1
        genome_coor = ("chr" + str(record.CHROM) + ":g." + str(record.POS) + ":" +
                       record.REF + ">" + str(record.ALT[0]))

        report = associate_chr_pos_ref_alt_with_item(record, len(columns), source, genome_coor)
        for key, value in FIELD_DICT[source].iteritems():
            try:
                column_name = key + "_" + source
                column_index = columns.index(column_name)
                report[column_index] = record.INFO[value]
            except KeyError:
                # if source == "BIC":
                    # variants[genome_coor].append(DEFAULT_CONTENTS)
                    # logging.debug("Could not find value %s for source %s in variant %s, inserting default content %s instead.", value, source, DEFAULT_CONTENTS)
                # else:
                    # raise Exception("There was a problem appending a value for %s to variant %s" % (value, variants[genome_coor]))
                raise Exception("WARNING: Key error with report: %s \n\nError on value: %s \n\n Error in record.INFO: %s \n\nNeeds attn." % (report, value, record.INFO))
        reports.append(report)
    return reports


def normalize_enigma_tsv_reports(file, columns, filename, file_extension):
    reports = []
    enigma_columns = ''
    enigma_file = open(file, 'r')
    line_num = 0
    enigma_column_indexes_in_columns = {}
    for line in enigma_file:
        line_num += 1
        if line_num == 1:
            enigma_columns = line.strip().split("\t")
            enigma_columns = [c + "_ENIGMA" for c in enigma_columns if c != "Genomic_Coordinate"]
            enigma_columns.insert(COLUMN_SOURCE, "Source")
            enigma_columns.insert(COLUMN_GENOMIC_HGVS, "Genomic_Coordinate")
            enigma_columns.insert(COLUMN_VCF_CHR, "Chr")
            enigma_columns.insert(COLUMN_VCF_POS, "Pos")
            enigma_columns.insert(COLUMN_VCF_REF, "Ref")
            enigma_columns.insert(COLUMN_VCF_ALT, "Alt")
            for key, value in enumerate(enigma_columns):
                enigma_column_indexes_in_columns[key] = value
        else:
            items = line.strip().split("\t")
            items.insert(COLUMN_SOURCE, "ENIGMA")
            v = items[COLUMN_GENOMIC_HGVS].replace("-", "").replace("chr", "").replace(">", ":")
            (chrom, pos, ref, alt) = v.split(":")
            items.insert(COLUMN_VCF_CHR, chrom)
            items.insert(COLUMN_VCF_POS, pos)
            items.insert(COLUMN_VCF_REF, ref)
            items.insert(COLUMN_VCF_ALT, alt)
            for ii in range(len(items)):
                if items[ii] is None or items[ii] == '':
                    items[ii] = '-'
            report = ['-'] * len(columns)
            for key, value in enigma_column_indexes_in_columns.iteritems():
                report[columns.index(value)] = items[key]
            reports.append(report)
    enigma_file.close()
    return reports


if __name__ == "__main__":
    main()
