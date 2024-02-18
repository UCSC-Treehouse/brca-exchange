#!/usr/bin/env python
# coding: utf-8

import itertools
import argparse
import csv
from collections import OrderedDict
import math
import numpy as np
import pandas as pd

#import gnomad.variant_scoring.constants as cnts
#from common import config, hgvs_utils, variant_utils, utils
#from data_merging.brca_pseudonym_generator import _normalize_genomic_fnc

GNOMAD_V2_CODE_ID = "Provisional_code_GnomAD"
GNOMAD_V3_CODE_ID = "Provisional_code_GnomADv3"
POPFREQ_CODE_ID = "Provisional_evidence_code_popfreq"
POPFREQ_CODE_DESCR = "Provisional_evidence_code_description_popfreq"

FAIL_INSUFFICIENT_READ_DEPTH = "No code is met for population data (read depth)"
FAIL_VCF_FILTER_FLAG = "No code is met for population data (VCF filter flag)"
FAIL_NEEDS_REVIEW = "No code is met (needs review)"
BA1 = "BA1 (met)"
BS1 = "BS1 (met)"
BS1_SUPPORTING = "BS1_Supporting (met)"
NO_CODE = "No code is met for population data (below threshold)"
NO_CODE_NON_SNV = "No code is met for population data (indel)"
PM2_SUPPORTING = "PM2_Supporting (met)"

READ_DEPTH_THRESHOLD_FREQUENT_VARIANT = 20
READ_DEPTH_THRESHOLD_RARE_VARIANT = 25

BA1_MSG = "The highest non-cancer, non-founder population filter allele frequency in gnomAD v2.1 (exomes only, non-cancer subset, read depth ≥20) or gnomAD v3.1 (non-cancer subset, read depth ≥20) is %s in the %s population, which is above the ENIGMA BRCA1/2 VCEP threshold (>0.001) for BA1 (BA1 met)."
BS1_MSG = "The highest non-cancer, non-founder population filter allele frequency in gnomAD v2.1 (exomes only, non-cancer subset, read depth ≥20) or gnomAD v3.1 (non-cancer subset, read depth ≥20) is %s in the %s population, which is above the ENIGMA BRCA1/2 VCEP threshold (>0.0001) for BS1, and below the BA1 threshold (>0.001) (BS1 met)."
BS1_SUPPORTING_MSG = "The highest non-cancer, non-founder population filter allele frequency in gnomAD v2.1 (exomes only, non-cancer subset, read depth ≥20) or gnomAD v3.1 f(non-cancer subset, read depth ≥20) is %s in the %s population which is within the ENIGMA BRCA1/2 VCEP threshold (>0.00002 to ≤ 0.0001) for BS1_Supporting (BS1_Supporting met)."
PM2_SUPPORTING_MSG = "This variant is absent from gnomAD v2.1 (exomes only, non-cancer subset, read depth ≥25) and gnomAD v3.1 (non-cancer subset, read depth ≥25) (PM2_Supporting met)."
NO_CODE_MSG = "This variant is present in gnomAD v2.1 (exomes only, non-cancer subset) or gnomAD v3.1 (non-cancer subset) but is below the ENIGMA BRCA1/2 VCEP threshold >0.00002 for BS1_Supporting (PM2_Supporting, BS1, and BA1 are not met)."
NO_CODE_NON_SNV_MSG = "This [insertion/deletion/large genomic rearrangement] variant was not observed in gnomAD v2.1 (exomes only, non-cancer subset) or gnomAD v3.1 (non-cancer subset), but PM2_Supporting was not applied since recall is suboptimal for this type of variant (PM2_Supporting not met)."
FAIL_NEEDS_REVIEW_MSG = "No code is met (variant needs review)"
FAIL_NEEDS_SOFTWARE_REVIEW_MSG = "No code is met (variant needs software review)"
FAIL_INSUFFICIENT_READ_DEPTH_MSG = "This variant is present in gnomAD v2.1 (exomes only, non-cancer subset) or gnomAD v3.1 (non-cancer subset) but is not meeting the specified read depths threshold ≥20 (PM2_Supporting, BS1, and BA1 are not met)."
FAIL_VCF_FILTER_FLAG_MSG = "This variant is present in gnomAD v2.1 (exomes only, non-cancer subset) or gnomAD v3.1 (non-cancer subset) but was flagged as suspect by gnomAD"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default="built_final.tsv",
                        help="Input file with variant data")
    parser.add_argument("-o", "--output", default="built_with_popfreq.tsv",
                        help="Output file with new columns")
    parser.add_argument("-d", "--data_dir", default="./processed_brca",
                        help="Directory with the processed files")
    parser.add_argument("-r", "--resource_dir", default="BRCAExchange/resources",
                        help="Pipeline resources")
    args = parser.parse_args()
    return(args)


def read_flags(flag_data):
    flags = {}
    for row in flag_data:
        flags[row["ID"]] = row
    return(flags)
    

def var_obj_to_name(v):
    return '-'.join(str(x) for x in [v.chr, v.pos, v.ref, v.alt])

def var_name_to_obj(v):
    a = v.split('-')
    return variant_utils.VCFVariant(a[0], int(a[1]), a[2], a[3])


csep = '-'
def add_name_col(dfx: pd.DataFrame):
    dfx['var_name'] = (dfx['contigName'].apply(str) + csep +
                       (dfx['start']).apply(str) +
                       csep + dfx['referenceAllele'] + csep + dfx['alternateAlleles'])
    return dfx

def estimate_coverage(start, end, chrom, df_cov):
    positions = list(range(start, end+1))
    coverage_this_chrom = df_cov.loc[df_cov["chrom"] == int(chrom)]
    positions_this_variant = coverage_this_chrom[coverage_this_chrom["pos"].isin(positions)]
    meanval = positions_this_variant["mean"].mean()
    medianval = positions_this_variant["median"].median()
    return(meanval, medianval)


def add_filter_flag_col(df, cols):
    df['vcf_filter_flag'] = df['filters'].apply(
        lambda filt_el: len(set(filt_el.split(';')).intersection(cols)) > 0)


def add_final_code_column(df):
    success_codes = set(['BA1', 'BS1', 'pm2_supporting'])
    dq_failure_codes = set(['fail_insufficient_read_depth', 'fail_vcf_filter_flag', 'need_review'])
    CODE_MISSING = 'code_missing'
    
    def is_both_sources(dfg):
        return len(dfg) > 1

    def set_final_code(dfg):
        if len(dfg) == 1:
            return dfg['evidence_code'].iloc[0]
        elif len(dfg) == 2:
            # we have data from both v2 and v3
            c1 = dfg['evidence_code'].iloc[0]
            c2 = dfg['evidence_code'].iloc[1]

            if (c1 in dq_failure_codes and c2 == CODE_MISSING) or (c2 in dq_failure_codes and c1 == CODE_MISSING):
                return CODE_MISSING
            
            if c1 in dq_failure_codes and c2 in dq_failure_codes:
                return "fail_both"
            
            if (c1 == 'pm2_supporting' and c2 == CODE_MISSING) or (c2 == 'pm2_supporting' and c1 == CODE_MISSING):
                return CODE_MISSING

            if c1 == CODE_MISSING and c2 == CODE_MISSING:
                return CODE_MISSING
            
            if c2 in success_codes and c1 not in success_codes:
                return c2
            if c1 in success_codes and c2 not in success_codes:
                return c1

            assert c1 in success_codes and c2 in success_codes
            
            if c1 == c2:
                return c1
            else:
                return "contradictory_results"

        raise ValueError("some duplicate variants per source?")

    v2_and_v3 = df.groupby('var_name').apply(is_both_sources)
    per_variant_code = df.groupby('var_name').apply(set_final_code)

    return df.merge(pd.DataFrame({'in_v2_and_v3' : v2_and_v3, 'final_code': per_variant_code}).reset_index(), how='left')


def extract_variant_scoring_data(df_cov2, df_cov3, df_var2, df_var3, read_depth_thresh, resource_dir):
    agg_v2 = process_v2(df_var2, df_cov2, read_depth_thresh, resource_dir)
    agg_v3 = process_v3(df_var3, df_cov3, read_depth_thresh)

    df_overall = pd.concat([agg_v2, agg_v3]).reset_index(drop=True)

    # running the actual scoring algorithm and the combined data
    df_overall['evidence_code'] = df_overall.apply(determine_evidence_code_per_variant, axis=1)
    df_overall = add_final_code_column(df_overall)

    return df_overall.sort_values('var_name')

def initialize_output_file(input_file, output_filename):
    """
    Create an empty output file with the new columns
    """
    new_columns = [GNOMAD_V2_CODE_ID, GNOMAD_V3_CODE_ID, 
                   POPFREQ_CODE_ID, POPFREQ_CODE_DESCR]
    input_header_row = input_file.fieldnames
    output_header_row = input_header_row + new_columns
    output_file = csv.DictWriter(open(output_filename,"w"), fieldnames=output_header_row,
                                 delimiter = '\t')
    output_file.writeheader()
    return(output_file)

def field_defined(field):
    """
    Return a binary value indicating whether or not this variant has the popmax FAF defined
    """
    return(field != "-")

def analyze_one_dataset(faf95_popmax_str, faf95_population, allele_count, is_snv,
                        mean_read_depth, median_read_depth, vcf_filter_flag, debug=True):
    #
    # Get the coverage data.  Rule out error conditions: low coverage, VCF filter flag.
    read_depth = min(mean_read_depth, median_read_depth)
    if pd.isna(read_depth):
        read_depth = 0
    rare_variant = False
    if field_defined(faf95_popmax_str):
        faf = float(faf95_popmax_str)
        if pd.isna(faf):
            rare_variant = True
        elif faf <= 0.00002:
            rare_variant = True
    else:
        faf = None
        rare_variant = True
    if rare_variant and read_depth < READ_DEPTH_THRESHOLD_RARE_VARIANT:
        return(FAIL_INSUFFICIENT_READ_DEPTH)
    if (not rare_variant) and read_depth < READ_DEPTH_THRESHOLD_FREQUENT_VARIANT:
        return(FAIL_INSUFFICIENT_READ_DEPTH)
    if vcf_filter_flag:
        return(FAIL_VCF_FILTER_FLAG)
    #
    # Address the cases where FAF is defined, and the variant is a candidate for a
    # evidence code for high population frequency (BA1, BS1, BS1_SUPPORTING)
    if not rare_variant:
        if faf > 0.001:
            return(BA1)
        elif faf >  0.0001:
            return(BS1)
        elif faf > 0.00002:
            return(BS1_SUPPORTING)
    if rare_variant:
        if not field_defined(allele_count):
            return(NO_CODE)
        elif int(allele_count) > 0:
            return(NO_CODE)
        else:
            if is_snv:
                return(PM2_SUPPORTING)
            else:
                return(NO_CODE_NON_SNV)
    return(NEEDS_REVIEW)


def analyze_across_datasets(code_v2, faf_v2, faf_popmax_v2,
                            code_v3, faf_v3, faf_popmax_v3):
    """
    Given the per-dataset evidence codes, generate an overall evidence code
    """
    benign_codes = [BA1, BS1, BS1_SUPPORTING]
    pathogenic_codes = [PM2_SUPPORTING]
    intermediate_codes = [ NO_CODE, NO_CODE_NON_SNV]
    ordered_success_codes = benign_codes + intermediate_codes + pathogenic_codes
    success_codes = set(ordered_success_codes)
    failure_codes = set([FAIL_INSUFFICIENT_READ_DEPTH, FAIL_VCF_FILTER_FLAG])
    ordered_codes = ordered_success_codes + list(failure_codes)

    #
    # First, rule out the case of outright contradictions
    if code_v2 in benign_codes and code_v3 in pathogenic_codes \
       or code_v2 in pathogenic_codes and code_v3 in benign_codes:
        return(FAIL_NEEDS_REVIEW, FAIL_NEEDS_REVIEW_MSG)
    #
    # Next, rule out the case where neither dataset has reliable data.
    # Arbitrarily use the message for v3, as the newer and presumably more robust.
    if code_v2 in failure_codes and code_v3 in failure_codes:
        if code_v3 == FAIL_INSUFFICIENT_READ_DEPTH:
            return(code_v3, FAIL_INSUFFICIENT_READ_DEPTH_MSG)
        else:
            assert(code_v3 == FAIL_VCF_FILTER_FLAG)
            return(code_v3, FAIL_VCF_FILTER_FLAG_MSG)
    #
    # At this point, we can assume that at least one dataset has
    # reliable data.
    #
    # Next, if both datasets point to a pathogenic effect, or
    # if one points to a pathogenic effect and the other an error,
    # then return PM2_SUPPORTING.
    if code_v2 == PM2_SUPPORTING and ordered_codes.index(code_v2) <= ordered_codes.index(code_v3):
        return(PM2_SUPPORTING, PM2_SUPPORTING_MSG)
    elif code_v3 == PM2_SUPPORTING and ordered_codes.index(code_v3) <= ordered_codes.index(code_v2):
        return(PM2_SUPPORTING, PM2_SUPPORTING_MSG)
    #
    # Next, if either dataset has an intermediate effect and the other
    # is not stronger (i.e. is also intermediate, or pathogenic, or failure),
    # return the intermediate effect code.
    if code_v2 in intermediate_codes and ordered_codes.index(code_v2) <= ordered_codes.index(code_v3):
        if code_v2 == NO_CODE:
            return(code_v2, NO_CODE_MSG)
        else:
            assert(code_v2 == NO_CODE_NON_SNV)
            return(code_v2, NO_CODE_NON_SNV_MSG)
    elif code_v3 in intermediate_codes and ordered_codes.index(code_v3) <= ordered_codes.index(code_v2):
        if code_v3 == NO_CODE:
            return(code_v3, NO_CODE_MSG)
        else:
            assert(code_v3 == NO_CODE_NON_SNV)
            return(code_v3, NO_CODE_NON_SNV_MSG)
    #
    # Now, at least one dataset must have a success code.  We can also assume that
    # neither is pathogenic (i.e. boht are benign, intermediate or failure).
    # In this case, identify and return the stronger code.
    print("prior to assertions, codes are", code_v2, code_v3)
    assert(code_v2 in benign_codes or code_v3 in benign_codes)
    assert(code_v2 in benign_codes or code_v2 in intermediate_codes or code_v2 in failure_codes)
    assert(code_v3 in benign_codes or code_v3 in intermediate_codes or code_v3 in failure_codes)
    if code_v3 == BA1:
        return(BA1, BA1_MSG % (faf_v3, faf_popmax_v3))
    elif code_v2 == BA1:
        return(BA1, BA1_MSG % (faf_v2, faf_popmax_v2))
    elif code_v3 == BS1:
        return(BS1, BS1_MSG % (faf_v3, faf_popmax_v3))
    elif code_v2 == BS1:
        return(BS1, BS1_MSG % (faf_v2, faf_popmax_v2))
    elif code_v3 == BS1_SUPPORTING:
        return(BS1, BS1_SUPPORTING_MSG % (faf_v3, faf_popmax_v3))
    elif code_v2 == BS1_SUPPORTING:
        return(BS1, BS1_SUPPORTING_MSG % (faf_v2, faf_popmax_v2))
    #
    # If we get here, there is a hole in the logic
    return(FAIL_NEEDS_REVIEW, FAIL_NEEDS_SOFTWARE_REVIEW_MSG)


def variant_is_flagged(variant_id, flags):
    print("checking", variant_id)
    assert(variant_id in flags)
    variant_flagged = False
    if flags[variant_id]["Filters"] != "PASS":
        variant_flagged = True
    return(variant_flagged)


def analyze_variant(variant, coverage_v2, coverage_v3, flags_v2, flags_v3, debug=True):
    """
    Analyze a single variant, adding the output columns
    """
    # Initialize the output columns with the assumption that the variant isn't observed.
    # This addresses the case where the variant is not in gnomAD at all.
    variant[GNOMAD_V2_CODE_ID] = PM2_SUPPORTING
    variant[GNOMAD_V3_CODE_ID] = PM2_SUPPORTING
    variant[POPFREQ_CODE_ID] = PM2_SUPPORTING
    variant[POPFREQ_CODE_DESCR] = PM2_SUPPORTING_MSG
    is_snv = (variant["Hg38_Start"] == variant["Hg38_End"])
    if debug:
        print("variant is snv:", is_snv)
    if field_defined(variant["Variant_id_GnomAD"]):
        (mean_read_depth, median_read_depth) = estimate_coverage(int(variant["pyhgvs_Hg37_Start"]),
                                                                 int(variant["pyhgvs_Hg37_End"]),
                                                                 int(variant["Chr"]),coverage_v2)
        print("mean read depth", mean_read_depth, "median read depth", median_read_depth)
        if debug:
            print("gnomAD V2 variant", variant["Variant_id_GnomAD"], "popmax", variant["faf95_popmax_exome_GnomAD"],
                  "allele count", variant["Allele_count_exome_GnomAD"], "mean read depth", mean_read_depth,
                  "median read depth", median_read_depth)
        variant[GNOMAD_V2_CODE_ID] = analyze_one_dataset(variant["faf95_popmax_exome_GnomAD"],
                                                         variant["faf95_popmax_population_exome_GnomAD"],
                                                         variant["Allele_count_exome_GnomAD"],
                                                         is_snv, mean_read_depth, median_read_depth,
                                                         variant_is_flagged(variant["Variant_id_GnomAD"], flags_v2))
        if debug:
            print("From gnomAD V2: code ID", variant[GNOMAD_V2_CODE_ID])
    if field_defined(variant["Variant_id_GnomADv3"]):
        (mean_read_depth, median_read_depth) = estimate_coverage(int(variant["Hg38_Start"]),
                                                                 int(variant["Hg38_End"]),
                                                                 int(variant["Chr"]),coverage_v3)
        print("mean read depth", mean_read_depth, "median read depth", median_read_depth)
        if debug:
            print("gnomAD V3 variant", variant["Variant_id_GnomADv3"], "popmax", variant["faf95_popmax_genome_GnomADv3"],
                  "allele count", variant["Allele_count_genome_GnomADv3"], "mean read depth", mean_read_depth,
                  "median read depth", median_read_depth)
        variant[GNOMAD_V3_CODE_ID] = analyze_one_dataset(variant["faf95_popmax_genome_GnomADv3"],
                                                         variant["faf95_popmax_population_genome_GnomADv3"],
                                                         variant["Allele_count_genome_GnomADv3"],
                                                         is_snv, mean_read_depth, median_read_depth,
                                                         variant_is_flagged(variant["Variant_id_GnomADv3"], flags_v3))
        if debug:
            print("From gnomAD V3: code ID", variant[GNOMAD_V3_CODE_ID])
    (variant[POPFREQ_CODE_ID], variant[POPFREQ_CODE_DESCR]) = analyze_across_datasets(variant[GNOMAD_V2_CODE_ID],variant["faf95_popmax_exome_GnomAD"],
                                                                                      variant["faf95_popmax_population_exome_GnomAD"],
                                                                                      variant[GNOMAD_V3_CODE_ID],
                                                                                      variant["faf95_popmax_genome_GnomADv3"],
                                                                                      variant["faf95_popmax_population_genome_GnomADv3"])
    if debug:
        print("consensus code:", variant[POPFREQ_CODE_ID], "msg", variant[POPFREQ_CODE_DESCR])
    return()



def main():
    args = parse_args()
    print(args)
    #cfg_df = config.load_config(gene_config_path)
    df_cov2 = pd.read_parquet(args.data_dir + '/df_cov_v2.parquet')
    df_cov3 = pd.read_parquet(args.data_dir + '/df_cov_v3.parquet')
    flags_v2 = read_flags(csv.DictReader(open(args.data_dir + "/brca.gnomAD.2.1.1.hg19.flags.tsv"), delimiter = "\t"))
    flags_v3 = read_flags(csv.DictReader(open(args.data_dir + "/brca.gnomAD.3.1.1.hg38.flags.tsv"), delimiter = "\t"))
    input_file = csv.DictReader(open(args.input), delimiter = "\t")
    output_file = initialize_output_file(input_file, args.output)
    for variant in input_file:
        analyze_variant(variant, df_cov2, df_cov3, flags_v2, flags_v3)
        output_file.writerow(variant)


if __name__ == "__main__":
    main()

