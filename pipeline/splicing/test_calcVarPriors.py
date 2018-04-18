import unittest
import mock
import calcVarPriors
from calcVarPriors import STD_DONOR_INTRONIC_LENGTH, STD_DONOR_EXONIC_LENGTH, STD_ACC_INTRONIC_LENGTH, STD_ACC_EXONIC_LENGTH
from calcVarPriors import STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH, STD_DE_NOVO_OFFSET
import calcMaxEntScanMeanStd
from calcVarPriorsMockedResponses import brca1Exons, brca2Exons 
from calcVarPriorsMockedResponses import brca1RefSpliceDonorBounds, brca2RefSpliceDonorBounds 
from calcVarPriorsMockedResponses import brca1RefSpliceAcceptorBounds, brca2RefSpliceAcceptorBounds
from calcVarPriorsMockedResponses import variantData

# dictionary containing possible strands for variants
strand = {"minus": "-",
          "plus": "+"}

# dictionary containing possible chromosomes for variants
chromosomes = {"13": "chr13",
               "17": "chr17"}

# dictionary containing possible variant types
varTypes = {"sub": "substitution",
            "ins": "insertion",
            "del": "deletion",
            "delins": "delins"}

# dictionary containing the number of exons for particular genes
numExons = {"BRCA1": 23,
            "BRCA2": 27}

# example donor exon boundaries for BRCA1 and BRCA2
exonDonorBoundsBRCA1 = {"exon16": {"donorStart": 43070930,
                                   "donorEnd": 43070922}}
exonDonorBoundsBRCA2 = {"exon15": {"donorStart": 32356607,
                                   "donorEnd": 32356615}}

# example acceptor exon boundaries for BRCA1 and BRCA2
exonAcceptorBoundsBRCA1 = {"exon21": {"acceptorStart": 43051137,
                                      "acceptorEnd": 43051115}}
exonAcceptorBoundsBRCA2 = {"exon20": {"acceptorStart": 32370936,
                                      "acceptorEnd": 32370958}}

# dictionary containing possible variant locations
variantLocations = {"outBounds": "outside_transcript_boundaries_variant",
                    "inCI": "CI_domain_variant",
                    "inCISpliceDonor": "CI_splice_donor_variant",
                    "inCISpliceAcceptor": "CI_splice_acceptor_variant",
                    "inSpliceDonor": "splice_donor_variant",
                    "inSpliceAcceptor": "splice_acceptor_variant",
                    "inGreyZone": "grey_zone_variant",
                    "afterGreyZone": "after_grey_zone_variant",
                    "inExon": "exon_variant",
                    "inUTR": "UTR_variant",
                    "inIntron": "intron_variant"}

# transcript data to mock response from fetch_gene_coordinates for BRCA1 and BRCA2
transcriptDataBRCA1 = {'bin': '114',
                       'exonEnds': '43045802,43047703,43049194,43051117,43057135,43063373,43063951,43067695,43071238,43074521,43076614,43082575,43091032,43094860,43095922,43097289,43099880,43104261,43104956,43106533,43115779,43124115,43125483,',
                       'exonFrames': '1,0,1,0,0,1,1,0,1,2,1,0,1,1,2,1,0,1,2,2,2,0,-1,',
                       'name': 'NM_007294.3',
                       'txStart': 43044294,
                       'exonCount': 23,
                       'cdsEndStat': 'cmpl',
                       'cdsEnd': 43124096,
                       'score': 0,
                       'name2': 'BRCA1',
                       'strand': '-',
                       'cdsStart': 43045677,
                       'cdsStartStat': 'cmpl',
                       'chrom': 'chr17',
                       'txEnd': 43125483,
                       'exonStarts': '43044294,43047642,43049120,43051062,43057051,43063332,43063873,43067607,43070927,43074330,43076487,43082403,43090943,43091434,43095845,43097243,43099774,43104121,43104867,43106455,43115725,43124016,43125270,'}

transcriptDataBRCA2 = {'bin': '103',
                       'exonEnds': '32315667,32316527,32319325,32325184,32326150,32326282,32326613,32329492,32331030,32333387,32341196,32344653,32346896,32355288,32356609,32357929,32362693,32363533,32370557,32371100,32376791,32379515,32379913,32380145,32394933,32397044,32399672,',
                       'exonFrames': '-1,0,1,1,2,1,0,1,0,1,1,1,1,2,1,0,2,2,0,0,1,0,1,0,1,0,0,',
                       'name': 'NM_000059.3',
                       'txStart': 32315479,
                       'exonCount': 27,
                       'cdsEndStat': 'cmpl',
                       'cdsEnd': 32398770,
                       'score': 0,
                       'name2': 'BRCA2',
                       'strand': '+',
                       'cdsStart': 32316460,
                       'cdsStartStat': 'cmpl',
                       'chrom': 'chr13',
                       'txEnd': 32399672,
                       'exonStarts': '32315479,32316421,32319076,32325075,32326100,32326241,32326498,32329442,32330918,32332271,32336264,32344557,32346826,32354860,32356427,32357741,32362522,32363178,32370401,32370955,32376669,32379316,32379749,32380006,32394688,32396897,32398161,'}

# sample sequence data for BRCA1 and BRCA2
brca1Seq = "GATCTGGAAGAAGAGAGGAAGAG"
brca2Seq = "TGTGTAACACATTATTACAGTGG"

# MaxEntScan score mean and std for donors and acceptors
meanStdDict =  {"donors": {"std": 2.3289956850167082,
                           "mean": 7.9380909090909073},
                "acceptors": {"std": 2.4336623152078452,
                              "mean": 7.984909090909091}}

# possible predicted qualitative ENIGMA classes
enigmaClasses = {"class1": "class_1",
                 "class2": "class_2",
                 "class3": "class_3",
                 "class4": "class_4",
                 "class5": "class_5",
                 "NA": "N/A"}

# possible prior probability of pathogenecity values
priorProbs = {"deNovoLow": 0.02,
              "proteinLow": 0.03,
              "low": 0.04,
              "proteinMod": 0.29,
              "deNovoMod": 0.3,
              "moderate": 0.34,
              "capped": 0.5,
              "deNovoHigh": 0.64,
              "proteinHigh": 0.81,
              "high": 0.97,
              "pathogenic": 0.99,
              "NA": "N/A"}


class test_calcVarPriors(unittest.TestCase):

    def setUp(self):

        self.variant = {"Chr": "13",
                        "Pos": "32314943",
                        "Ref": "A",
                        "Alt": "G",
                        "Gene_Symbol": "BRCA2",
                        "Reference_Sequence": "NM_000059.3",
                        "HGVS_cDNA": "c.-764A>G"}
                  
    def test_checkSequence(self):
        '''Tests that checkSequence function categorized acceptable sequences correctly'''
        # sequence with unacceptable letters
        self.variant["Ref"] = "ATGSFHG"
        self.variant["Alt"] = "AGTHA"
        acceptableRefSeq = calcVarPriors.checkSequence(self.variant["Ref"])
        acceptableAltSeq = calcVarPriors.checkSequence(self.variant["Alt"])
        self.assertFalse(acceptableRefSeq)
        self.assertFalse(acceptableAltSeq)

        # sequence with numbers
        self.variant["Ref"] = "3452345"
        self.variant["Alt"] = "3456324"
        acceptableRefSeq = calcVarPriors.checkSequence(self.variant["Ref"])
        acceptableAltSeq = calcVarPriors.checkSequence(self.variant["Alt"])
        self.assertFalse(acceptableRefSeq)
        self.assertFalse(acceptableAltSeq)

        # blank sequence
        self.variant["Ref"] = ""
        self.variant["Alt"] = ""
        acceptableRefSeq = calcVarPriors.checkSequence(self.variant["Ref"])
        acceptableAltSeq = calcVarPriors.checkSequence(self.variant["Alt"])
        self.assertFalse(acceptableRefSeq)
        self.assertFalse(acceptableAltSeq)

        # sequence with only ATCG
        self.variant["Ref"] = "ATGACG"
        self.variant["Alt"] = "AGTAATA"
        acceptableRefSeq = calcVarPriors.checkSequence(self.variant["Ref"])
        acceptableAltSeq = calcVarPriors.checkSequence(self.variant["Alt"])
        self.assertTrue(acceptableRefSeq)
        self.assertTrue(acceptableAltSeq)

        # sequence containing all possible acceptable bases
        self.variant["Ref"] = "ATGRACYGN"
        self.variant["Alt"] = "YAGRTNAATA"
        acceptableRefSeq = calcVarPriors.checkSequence(self.variant["Ref"])
        acceptableAltSeq = calcVarPriors.checkSequence(self.variant["Alt"])
        self.assertTrue(acceptableRefSeq)
        self.assertTrue(acceptableAltSeq)

    def test_getVarStrand(self):
        '''Tests that variant strand is set correctly based on variant's gene_symbol'''
        self.variant["Gene_Symbol"] = "BRCA1"
        varStrand = calcVarPriors.getVarStrand(self.variant)
        self.assertEquals(varStrand, strand["minus"])

        self.variant["Gene_Symbol"] = "BRCA2"
        varStrand = calcVarPriors.getVarStrand(self.variant)
        self.assertEquals(varStrand, strand["plus"])

    def test_getVarChrom(self):
        '''Tests taht variant chromosome is set correctly based on variant's gene_symbol'''
        self.variant["Gene_Symbol"] = "BRCA1"
        varChrom = calcVarPriors.getVarChrom(self.variant)
        self.assertEquals(varChrom, chromosomes["17"])

        self.variant["Gene_Symbol"] = "BRCA2"
        varChrom = calcVarPriors.getVarChrom(self.variant)
        self.assertEquals(varChrom, chromosomes["13"])

    @mock.patch('calcVarPriors.checkSequence', return_value = True)
    def test_getVarType(self, checkSequence):
        '''
        Tests that variant type is set correctly to substitution, deletion, insertion, or delins based on variant "Ref" and "Alt" values
        '''
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, varTypes["sub"])

        self.variant["Ref"] = "A"
        self.variant["Alt"] = "AAA"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, varTypes["ins"])

        self.variant["Ref"] = "AGT"
        self.variant["Alt"] = "A"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, varTypes["del"])

        self.variant["Ref"] = "AG"
        self.variant["Alt"] = "AGTA"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, varTypes["delins"])

        self.variant["Ref"] = "AGTA"
        self.variant["Alt"] = "AG"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, varTypes["delins"])

        self.variant["Ref"] = "AG"
        self.variant["Alt"] = "GT"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, varTypes["delins"])

    def test_getVarConsequences(self):
        '''
        Tests that:
        1. Variants with non-BRCA1/BRCA2 chromosomes are skipped
        2. Variants with Alt alleles that are not one of the 4 canonical bases are skipped
        '''

        self.variant["Chr"] = ""
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

        self.variant["Chr"] = "41160094"
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

        self.variant["Chr"] = "chr17:g.43008077:TAGG"
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

        self.variant["Chr"] = "13"
        self.variant["Hg38_Start"] = "32339320"
        self.variant["Hg38_End"] = "32339320"
        self.variant["Alt"] = "R"
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

        self.variant["Alt"] = "-"
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

        self.variant["Alt"] = "38413620"
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

    def test_checkWithinBoundaries(self):
        '''
        Tests that positions are correctly identified as in/not in boundaries and that boundaries are inclusive
        '''
        varStrand = strand["plus"]
        boundaryStart = 32357742
        boundaryEnd = 32357780

        # check that last position before boundary start is NOT included
        position = 32357741
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertFalse(withinBoundaries)

        # check that first position after boundary end is NOT included
        position = 32357781
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertFalse(withinBoundaries)

        # check that boundaryStart is included
        position = 32357742
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertTrue(withinBoundaries)

        # check that boundaryEnd is included
        position = 32357780
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertTrue(withinBoundaries)

        # check that position within boundaries is included
        position = 32357758
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertTrue(withinBoundaries)

        varStrand = strand["minus"]
        boundaryStart = 43067695
        boundaryEnd = 43067649

        # check that last position before boundary start is NOT included
        position = 43067696
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertFalse(withinBoundaries)

        # check that first position after boundary end is NOT included
        position = 43067648
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertFalse(withinBoundaries)

        # check that boundaryStart is included
        position = 43067695
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertTrue(withinBoundaries)
        
        # check that boundaryEnd is included
        position = 43067649
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertTrue(withinBoundaries)

        # check that position within boundaries is included
        position = 43067669
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertTrue(withinBoundaries)        

    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_varOutsideBoundariesBRCA1(self, getVarStrand):
        '''Tests that variant outside/inside transcript boundaries are correctly identified for BRCA1'''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"

        # checks for BRCA1 variant outside transcript boundaries
        self.variant["Pos"] = "43044274"
        varOutBounds = calcVarPriors.varOutsideBoundaries(self.variant)
        self.assertTrue(varOutBounds)

        # checks for BRCA1 variant inside transcript boundaries
        self.variant["Pos"] = "43070957"
        varOutBounds = calcVarPriors.varOutsideBoundaries(self.variant)
        self.assertFalse(varOutBounds)

    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_varOutsideBoundariesBRCA2(self, getVarStrand):
        '''Tests that variant outside/inside transcript boundaries are correctly identified for BRCA2'''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"

        # checks for BRCA2 variant outside transcript boundaries
        self.variant["Pos"] = "32315477"
        varOutBounds = calcVarPriors.varOutsideBoundaries(self.variant)
        self.assertTrue(varOutBounds)

        # checks for BRCA2 variant inside transcript boundaries
        self.variant["Pos"] = "32326500"
        varOutBounds = calcVarPriors.varOutsideBoundaries(self.variant)
        self.assertFalse(varOutBounds)
        
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_varInUTRBRCA1(self, varOutsideBoundaries, getVarStrand):
        '''Tests that variants in 5' and 3' UTR are correctly identified for BRCA1'''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        
        # checks for BRCA1 variant in 5' UTR
        self.variant["Pos"] = "43124110"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertTrue(varInUTR)
        
        # checks for BRCA1 variant in 3' UTR
        self.variant["Pos"] = "43045668"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertTrue(varInUTR)

        # checks for BRCA1 variant in exon
        self.variant["Pos"] = "43049184"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertFalse(varInUTR)

        # checks for BRCA1 variant in intron
        self.variant["Pos"] = "43049213"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertFalse(varInUTR)

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_varInUTRBRCA2(self, varOutsideBoundaries, getVarStrand):
        '''Tests that variants in 5' and 3' UTR are correctly identified for BRCA2'''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        
        # checks for BRCA2 variant in 5' UTR
        self.variant["Pos"] = "32316434"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertTrue(varInUTR)
        
        # checks for BRCA2 variant in 3' UTR
        self.variant["Pos"] = "32398781"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertTrue(varInUTR)

        # checks for BRCA2 variant in exon
        self.variant["Pos"] = "32394719"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertFalse(varInUTR)

        # checks for BRCA2 variant in intron
        self.variant["Pos"] = "32396875"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertFalse(varInUTR)

    def test_getExonBoundariesBRCA1(self):
        '''
        Tests that:
        1. Exon boundaries are set correctly for gene on minus strand (BRCA1)
            - checks that exon does not start before it ends
            - next exon does not start before current exon ends
        2. length of varExons matches number of exons for BRCA1
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        varExons = calcVarPriors.getExonBoundaries(self.variant)
        # check correct number of exons
        self.assertEquals(len(varExons), numExons["BRCA1"])
        # because '-' strand gene, checks that exonStart > exonEnd
        for exon in varExons.keys():
            exonBounds = varExons[exon]
            self.assertGreater(exonBounds["exonStart"], exonBounds["exonEnd"])
            currentExonNum = int(exon[4:])
            nextExonNum = str(currentExonNum + 1)
            nextExonKey = "exon" + nextExonNum
            if nextExonNum <= numExons["BRCA1"]:
                nextExonStart = varExons[nextExonKey]["exonStart"]
                # checks that next exon does not start before current exon ends
                self.assertGreater(exonBounds["exonEnd"], nextExonStart)

    def test_getExonBoundariesBRCA2(self):
        '''
        Tests that:
        1. Exon boundaries are set correctly for gene on plus strand (BRCA2)
            - checks that exon does not start before it ends
            - next exon does not start before current exon ends
        2. length of varExons matches number of exons for BRCA2
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        varExons = calcVarPriors.getExonBoundaries(self.variant)
        # check correct number of exons
        self.assertEquals(len(varExons), numExons["BRCA2"])
        # because '+' strand gene, checks that exonEnd > exonStart
        for exon in varExons.keys():
            exonBounds = varExons[exon]
            self.assertGreater(exonBounds["exonEnd"], exonBounds["exonStart"])
            currentExonNum = int(exon[4:])
            nextExonNum = str(currentExonNum + 1)
            nextExonKey = "exon" + nextExonNum
            if nextExonNum <= numExons["BRCA2"]:
                nextExonStart = varExons[nextExonKey]["exonStart"]
                # checks that next exon does not start before current exon ends
                self.assertGreater(nextExonStart, exonBounds["exonEnd"])

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getRefSpliceDonorBoundariesBRCA1(self, getExonBoundaries, getVarStrand):
        '''
        Tests that splice donor boundaries are set correctly for reference transcript (NM_000059.3) and strand (-)
        Uses example boundaries defined at beginning of script
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        spliceDonorBounds = calcVarPriors.getRefSpliceDonorBoundaries(self.variant, STD_DONOR_INTRONIC_LENGTH, STD_DONOR_EXONIC_LENGTH)
        # checks that region after last exon is not considered a splice donor region
        self.assertNotIn("exon24", spliceDonorBounds)
        # to find exon specified in global variables
        exon = exonDonorBoundsBRCA1.keys()[0]
        self.assertEquals(exonDonorBoundsBRCA1[exon]["donorStart"],
                          spliceDonorBounds[exon]["donorStart"])
        self.assertEquals(exonDonorBoundsBRCA1[exon]["donorEnd"],
                          spliceDonorBounds[exon]["donorEnd"])

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getRefSpliceDonorBoundariesBRCA2(self, getExonBoundaries, getVarStrand):
        '''
        Tests that splice donor boundaries are set correctly for reference transcript (NM_000059.3) and strand (+)
        Uses example boundaries defined at beginning of script
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        spliceDonorBounds = calcVarPriors.getRefSpliceDonorBoundaries(self.variant, STD_DONOR_INTRONIC_LENGTH, STD_DONOR_EXONIC_LENGTH)
        # checks that region after last exon is not considered a splice donor region
        self.assertNotIn("exon27", spliceDonorBounds)
        # to find exon specified in global variables
        exon = exonDonorBoundsBRCA2.keys()[0]
        self.assertEquals(exonDonorBoundsBRCA2[exon]["donorStart"],
                          spliceDonorBounds[exon]["donorStart"])
        self.assertEquals(exonDonorBoundsBRCA2[exon]["donorEnd"],
                          spliceDonorBounds[exon]["donorEnd"])

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getSpliceAcceptorBoundariesRefBRCA1(self, getExonBoundaries, getVarStrand):
        '''
        Tests that ref splice acceptor boundaries are set correctly for reference transcript (NM_007294.3) and strand (-)
        Uses example boundaries defined at beginning of script
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        spliceAcceptorBounds = calcVarPriors.getSpliceAcceptorBoundaries(self.variant, STD_ACC_INTRONIC_LENGTH, STD_ACC_EXONIC_LENGTH)
        # checks that region before first exon is not considered a splice acceptor region
        self.assertNotIn("exon1", spliceAcceptorBounds)
        # to find exon specified in global variables
        exon = exonAcceptorBoundsBRCA1.keys()[0]
        self.assertEquals(exonAcceptorBoundsBRCA1[exon]["acceptorStart"],
                          spliceAcceptorBounds[exon]["acceptorStart"])
        self.assertEquals(exonAcceptorBoundsBRCA1[exon]["acceptorEnd"],
                          spliceAcceptorBounds[exon]["acceptorEnd"])

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getSpliceAcceptorBoundariesDeNovoBRCA1(self, getExonBoundaries, getVarStrand):
        '''
        Tests that de novo splice acceptor boundaries are set correctly for reference transcript (NM_007294.3) and strand (-)
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        deNovoSpliceAccBounds = calcVarPriors.getSpliceAcceptorBoundaries(self.variant, STD_ACC_INTRONIC_LENGTH, STD_DE_NOVO_LENGTH)
        expectedDeNovoRegionExon6 = {"acceptorStart": 43104976,
                                     "acceptorEnd": 43104947}
        self.assertEquals(deNovoSpliceAccBounds["exon6"]["acceptorStart"],
                          expectedDeNovoRegionExon6["acceptorStart"])
        self.assertEquals(deNovoSpliceAccBounds["exon6"]["acceptorEnd"],
                          expectedDeNovoRegionExon6["acceptorEnd"])

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getSpliceAcceptorBoundariesRefBRCA2(self, getExonBoundaries, getVarStrand):
        '''
        Tests that ref splice acceptor boundaries are set correctly for reference transcript (NM_000059.3) and strand (+)
        Uses example boundaries defined at beginning of script
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        spliceAcceptorBounds = calcVarPriors.getSpliceAcceptorBoundaries(self.variant, STD_ACC_INTRONIC_LENGTH, STD_ACC_EXONIC_LENGTH)
        # checks that region before first exon is not considered a splice acceptor region
        self.assertNotIn("exon1", spliceAcceptorBounds)
        # to find exon specified in global variables
        exon = exonAcceptorBoundsBRCA2.keys()[0]
        self.assertEquals(exonAcceptorBoundsBRCA2[exon]["acceptorStart"],
                          spliceAcceptorBounds[exon]["acceptorStart"])
        self.assertEquals(exonAcceptorBoundsBRCA2[exon]["acceptorEnd"],
                          spliceAcceptorBounds[exon]["acceptorEnd"])

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getSpliceAcceptorBoundariesDeNovoBRCA2(self, getExonBoundaries, getVarStrand):
        '''
        Tests that de novo splice acceptor boundaries are set correctly for reference transcript (NM_000059.3) and strand (+)
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        deNovoSpliceAccBounds = calcVarPriors.getSpliceAcceptorBoundaries(self.variant, STD_ACC_INTRONIC_LENGTH, STD_DE_NOVO_LENGTH)
        expectedDeNovoRegionExon8 = {"acceptorStart": 32329423,
                                     "acceptorEnd": 32329452}
        self.assertEquals(deNovoSpliceAccBounds["exon8"]["acceptorStart"],
                          expectedDeNovoRegionExon8["acceptorStart"])
        self.assertEquals(deNovoSpliceAccBounds["exon8"]["acceptorEnd"],
                          expectedDeNovoRegionExon8["acceptorEnd"])
        
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_varInExonBRCA1(self, varOutsideBoundaries, getExonBoundaries, getVarStrand):
        '''Tests that variant is correctly identified as inside or outside an exon for BRCA1'''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"

        # checks BRCA1 5' exon boundary (last base in intron)
        self.variant["Pos"] = "43104957"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)

        # checks BRCA1 5' exon boundary (first base in exon)
        self.variant["Pos"] = "43104956"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # checks BRCA1 3' exon boundary (last base in exon)
        self.variant["Pos"] = "43067608"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # checks BRCA1 3' exon boundary (first base in intron)
        self.variant["Pos"] = "43067607"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)
        
        # checks BRCA1 variant inside an exon
        self.variant["Pos"] = "43049176"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # checks BRCA1 variant outside an exon
        self.variant["Pos"] = "43045827"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_varInExonBRCA2(self, varOutsideBoundaries, getExonBoundaries, getVarStrand):
        '''Tests that variant is correctly identified as inside or outside an exon for BRCA2'''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"

        # checks BRCA2 5' exon boundary (last base in intron)
        self.variant["Pos"] = "32357741"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)

        # checks BRCA2 5' exon boundary (first base in exon)
        self.variant["Pos"] = "32357742"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # checks BRCA2 3' exon boundary (last base in exon)
        self.variant["Pos"] = "32370557"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # checks BRCA2 3' exon boundary (first base in intron)
        self.variant["Pos"] = "32370558"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)
        
        # checks BRCA2 variant inside an exon
        self.variant["Pos"] = "32398201"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # cehcks BRCA2 variant outside an exon
        self.variant["Pos"] = "32396873"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getVarExonNumberSNSBRCA1(self, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that exon number is set correctly for minus strand (BRCA1) variant in exon'''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"

        # variant position in exon 13
        self.variant["Pos"] = "43082564"
        print self.variant
        varExonNum = calcVarPriors.getVarExonNumberSNS(self.variant)
        self.assertEquals(varExonNum, "exon13")

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getVarExonNumberSNSBRCA2(self, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that exon number is set correctly for plus strand (BRCA2) variant in exon'''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"

        # variant position in exon 4
        self.variant["Pos"] = "32325166"
        varExonNum = calcVarPriors.getVarExonNumberSNS(self.variant)
        self.assertEquals(varExonNum, "exon4")
        
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca1RefSpliceDonorBounds)
    def test_varInSpliceRegionDonorBRCA1Ref(self, getRefDonorBoundaries):
        '''
        Tests that:
        1. Variant is correctly identified as in or NOT in a splice donor region 
           for multiple positions across multiple exons in BRCA1
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        donor = True
        deNovo = False

        #checks that 7th base in intron is NOT counted as in splice donor
        self.variant["Pos"] = "43063326"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceDonor)
        
        # checks that first base in intron counted as in splice donor
        self.variant["Pos"] =  "43097243"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that middle base in intron counted as in splice donor
        self.variant["Pos"] = "43095842"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that last base in intron counted as in splice donor
        self.variant["Pos"] = "43091429"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that first base in exon counted as in splice donor
        self.variant["Pos"] = "43090946"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that middle base in exon counted as in splice donor
        self.variant["Pos"] = "43082405"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that last base in exon counted as in splice donor
        self.variant["Pos"] = "43076488"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that 4th to last base in exon is NOT counted as in splice donor
        self.variant["Pos"] = "43057055"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceDonor)

        # checks that region after exon 24 is  NOT counted as in splice donor
        self.variant["Pos"] = "43044294"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceDonor)

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    def test_varInSpliceRegionDonorBRCA1DeNovoTrue(self, getExonBoundaries, varInExon):
        '''Tests that function correctly identifies if variant is IN a de novo splice region for minus strand gene (BRCA1)'''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        donor = True
        deNovo = True

        # checks that variant in an exon is marked as being in a de novo splice donor region
        self.variant["Pos"] = "43104232"
        inDeNovoDonorRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inDeNovoDonorRegion)

        # checks that variant in intronic portion of reference splice donor is marked as being in a de novo splice donor region
        self.variant["Pos"] = "43104117"
        inDeNovoDonorRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inDeNovoDonorRegion)

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    def test_varInSpliceRegionDonorBRCA1DeNovoFalse(self, getExonBoundaries, varInExon):
        '''Tests that function correctly identifies if variant is NOT IN a de novo splice region for minus strand gene (BRCA1)'''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        donor = True
        deNovo = True

        # checks that variant in an intron is NOT marked as being in a de novo splice donor region
        self.variant["Pos"] = "43104101"
        inDeNovoDonorRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inDeNovoDonorRegion)

    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca1RefSpliceDonorBounds)
    def test_getVarSpliceRegionBoundsDonorBRCA1(self, varInSpliceRegion, getRefSpliceDonorBoundaries):
        '''
        Tests that:
        1. Function returns correct donor boundaries for a given variant (genomic position)
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        donor = True
        deNovo = False
    
        # checks that variant in exon 16 splice donor region boundaries are returned correctly
        self.variant["Pos"] = "43070925"
        spliceDonorRegion = calcVarPriors.getVarSpliceRegionBounds(self.variant, donor=donor, deNovo=deNovo)
        self.assertEquals(spliceDonorRegion["exonName"], "exon16")
        self.assertEquals(exonDonorBoundsBRCA1["exon16"]["donorStart"], spliceDonorRegion["donorStart"])
        self.assertEquals(exonDonorBoundsBRCA1["exon16"]["donorEnd"], spliceDonorRegion["donorEnd"])

    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca2RefSpliceDonorBounds)
    def test_varInSpliceRegionDonorBRCA2Ref(self, getRefSpliceDonorBoundaries):
        '''
        Tests that:
        1. Variant is correctly identified as in or NOT in a splice donor region 
           for multiple positions across multiple exons in BRCA2
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        donor = True
        deNovo = False

        # checks that 7th base in intron is NOT counted as in splice donor
        self.variant["Pos"] = "32363540"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceDonor)

        # checks that first base in intron counted as in splice donor
        self.variant["Pos"] = "32329493"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that middle base in intron counted as in splice donor
        self.variant["Pos"] = "32331033"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that last base in intron counted as in splice donor
        self.variant["Pos"] = "32333393"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that first base in exon counted as in splice donor
        self.variant["Pos"] = "32341194"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that middle base in exon counted as in splice donor
        self.variant["Pos"] = "32344652"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that last base in exon counted as in splice donor
        self.variant["Pos"] = "32346896"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that 4th to last base in exon is NOT counted as in splice donor
        self.variant["Pos"] = "32370554"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceDonor)

        # checks that region after  exon 27 is NOT counted as in splice donor
        self.variant["Pos"] = "32399672"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceDonor)

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    def test_varInSpliceRegionDonorBRCA2DeNovoTrue(self, getExonBoundaries, varInExon):
        '''Tests that function correctly identifies if variant is IN a de novo splice region for plus strand gene (BRCA2)'''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        donor = True
        deNovo = True

        # checks that variant in an exon is marked as being in a de novo splice donor region
        self.variant["Pos"] = "32379784"
        inDeNovoDonorRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inDeNovoDonorRegion)

        # checks that variant in intronic portion of reference splice donor is marked as being in a de novo splice donor region
        self.variant["Pos"] = "32379914"
        inDeNovoDonorRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inDeNovoDonorRegion)

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    def test_varInSpliceRegionDonorBRCA2DeNovoFalse(self, getExonBoundaries, varInExon):
        '''Tests that function correctly identifies if variant is NOT IN a de novo splice region for pluis strand gene (BRCA2)'''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        donor = True
        deNovo = True

        # checks that variant in an intron is NOT marked as being in a de novo splice donor region
        self.variant["Pos"] = "32379743"
        inDeNovoDonorRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inDeNovoDonorRegion)

    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca2RefSpliceDonorBounds)
    def test_getVarSpliceRegionBoundsDonorBRCA2(self, varInSpliceRegion, getRefSpliceDonorBoundaries):
        '''
        Tests that:
        1. Function returns correct donor boundaries for a given variant (genomic position) 
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        donor = True
        deNovo = False

        # checks that variant in exon 16 splice donor region boundaries are returned correctly
        self.variant["Pos"] = "32356608"
        spliceDonorRegion = calcVarPriors.getVarSpliceRegionBounds(self.variant, donor=donor, deNovo=deNovo)
        self.assertEquals(spliceDonorRegion["exonName"], "exon15")
        self.assertEquals(exonDonorBoundsBRCA2["exon15"]["donorStart"], spliceDonorRegion["donorStart"])
        self.assertEquals(exonDonorBoundsBRCA2["exon15"]["donorEnd"], spliceDonorRegion["donorEnd"])

    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    def test_varInSpliceRegionAcceptorBRCA1(self, getSpliceAcceptorBoundaries):
        '''
        Tests that:
        1. Variant is correctly identified as in or NOT in a splice acceptor region
           uses multiple positions across multiple exons for BRCA1
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        donor = False
        deNovo = False

        # checks that -21st base in intron is NOT counted as in splice acceptor
        self.variant["Pos"] = "43067716"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceAcceptor)
        
        # checks that first base in intron counted as in splice acceptor
        self.variant["Pos"] = "43124135"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that middle base in intron counted as in splice acceptor
        self.variant["Pos"] = "43115787"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that last base in intron counted as in splice acceptor
        self.variant["Pos"] = "43106534"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that first base in exon counted as in splice acceptor
        self.variant["Pos"] = "43104956"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that middle base in exon counted as in splice acceptor
        self.variant["Pos"] = "43104260"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that last base in exon counted as in splice acceptor
        self.variant["Pos"] = "43099878"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that 4th base in exon is NOT counted as in splice acceptor
        self.variant["Pos"] = "43063948"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceAcceptor)

        # checks that region before exon 1 is NOT counted as in splice acceptor
        self.variant["Pos"] = "431254483"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceAcceptor)

    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    def test_getVarSpliceRegionBoundsAcceptorBRCA1(self, varInSpliceRegion, getSpliceAcceptorBoundaries):
        '''
        Tests that:
        1. Function returns correct donor boundaries for a given variant (genomic position) 
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        donor = False
        deNovo = False

        # checks that variant in exon 21 splice acceptor region boundaries are returned correctly
        self.variant["Pos"] = "43051117"
        spliceAccRegion = calcVarPriors.getVarSpliceRegionBounds(self.variant, donor=donor, deNovo=deNovo)
        self.assertEquals(spliceAccRegion["exonName"], "exon21")
        self.assertEquals(exonAcceptorBoundsBRCA1["exon21"]["acceptorStart"], spliceAccRegion["acceptorStart"])
        self.assertEquals(exonAcceptorBoundsBRCA1["exon21"]["acceptorEnd"], spliceAccRegion["acceptorEnd"])

    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    def test_varInSpliceRegionAcceptorBRCA2(self, getSpliceAcceptorBoundaries):
        '''
        Tests that:
        1. Variant is correctly identified as in or NOT in a splice acceptor region
           uses multiple positions across multiple exons for BRCA2
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        donor = False
        deNovo = False

        # checks that -21st base in intron is NOT counted as in splice acceptor
        self.variant["Pos"] = "32357721"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceAcceptor)

        # checks that first base in intron counted as in splice acceptor
        self.variant["Pos"] = "32316402"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that middle base in intron counted as in splice acceptor
        self.variant["Pos"] = "32319069"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that last base in intron counted as in splice acceptor
        self.variant["Pos"] = "32325075"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that first base in exon counted as in splice acceptor
        self.variant["Pos"] = "32326101"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that middle base in exon counted as in splice acceptor
        self.variant["Pos"] = "32326243"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that last base in exon counted as in splice acceptor
        self.variant["Pos"] = "32326501"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that 4th base in exon is NOT counted as in splice acceptor
        self.variant["Pos"] = "32362526"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceAcceptor)

        # checks that region before exon 1 is NOT counted as in splice acceptor
        self.variant["Pos"] = "32315479"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceAcceptor)

    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    def test_getVarSpliceRegionBoundsAcceptorBRCA2(self, varInSpliceRegion, getSpliceAcceptorBoundaries):
        '''
        Tests that:
        1. Function returns correct donor boundaries for a given variant (genomic position) 
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        donor = False
        deNovo = False

        # checks that variant in exon 20 splice acceptor region boundaries are returned correctly
        self.variant["Pos"] = "32370948"
        spliceAccRegion = calcVarPriors.getVarSpliceRegionBounds(self.variant, donor=donor, deNovo=deNovo)
        self.assertEquals(spliceAccRegion["exonName"], "exon20")
        self.assertEquals(exonAcceptorBoundsBRCA2["exon20"]["acceptorStart"], spliceAccRegion["acceptorStart"])
        self.assertEquals(exonAcceptorBoundsBRCA2["exon20"]["acceptorEnd"], spliceAccRegion["acceptorEnd"])

    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    def test_varInCIDomainEnigmaBRCA1(self, getVarStrand, varInExon):
        '''Tests that variant is correctly identified as in or NOT in CI domain in BRCA1 as defined by ENIGMA rules'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks variant in BRCA 1 RING domain is identified as in ENIGMA CI domain
        self.variant["Pos"] = "43124089"
        inEnigmaCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inEnigmaCI)

        # checks variant in BRCA1 BRCT domain is identified as in ENIGMA CI domain
        self.variant["Pos"] = "43070945"
        inEnigmaCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inEnigmaCI)

        # checks variant NOT in BRCA1 CI domain is NOT identified as in ENIGMA CI domain
        self.variant["Pos"] = "43097274"
        inEnigmaCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertFalse(inEnigmaCI)
        
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    def test_varInCIDomainEnigmaBRCA2(self, getVarStrand, varInExon):
        '''Tests that variant is correctly identified as in or NOT in CI domain in BRCA2 as defined by ENIGMA rules'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks variant in BRCA2 DNB domain is identified as in ENIGMA CI domain
        self.variant["Pos"] = "32379809"
        inEnigmaCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inEnigmaCI)

        # checks variant NOT in BRCA2 CI domain is NOT identified as in ENIGMA CI domain
        self.variant["Pos"] = "32398354"
        inEnigmaCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertFalse(inEnigmaCI)

    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    def test_varInCIDomainPriorsBRCA1(self, getVarStrand, varInExon):
        '''Tests that variant is correctly identified as in or NOT in CI domain in BRCA1 as defined by PRIORS webiste'''
        boundaries = "priors"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks variant in BRCA1 initiation domain is identified as in PRIORS CI domain
        self.variant["Pos"] = "43124096"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inPriorsCI)

        # checks variant in BRCA1 RING domain is identified as in PRIORS CI domain
        self.variant["Pos"] = "43115746"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inPriorsCI)

        # checks variant in BRCA1 BRCT domain is identified as in PRIORS CI domain
        self.variant["Pos"] = "43057092"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inPriorsCI)

        # checks that variant NOT in BRCA1 CI domain is NOT identified as in PRIORS CI domain
        self.variant["Pos"] = "43124090"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertFalse(inPriorsCI)
        
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    def test_varInCIDomainPriorsBRCA2(self, getVarStrand, varInExon):
        '''Tests that variant is correctly identified as in or NOT in CI domain in BRCA2 as defined by PRIORS webiste'''
        boundaries = "priors"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks variant in BRCA2 initiation domain is identified as in PRIORS CI domain
        self.variant["Pos"] = "32316462"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inPriorsCI)

        # checks variant in BRCA2 PALB2 domain is identified as in PRIORS CI domain
        self.variant["Pos"] = "32319092"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inPriorsCI)

        # checks variant in BRCA2 DNB domain is identified as in PRIORS CI domain
        self.variant["Pos"] = "32362561"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inPriorsCI)

        # checks variant in TR2/RAD5 domain is identified as in PRIORS CI domain
        self.variant["Pos"] = "32398406"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inPriorsCI)

        # checks that variant NOT in BRCA2 CI domain is NOT identified as in PRIORS CI domain
        self.variant["Pos"] = "32336283"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertFalse(inPriorsCI)

    def test_varInGreyZone(self):
        '''Tests that variant is correctly identified as in the grey zone'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks that BRCA1 variant is NOT considered in grey zone
        self.variant["Pos"] = "43045708"
        inGreyZone = calcVarPriors.varInGreyZone(self.variant)
        self.assertFalse(inGreyZone)

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks that variant before the BRCA2 grey zone is NOT identified as in BRCA2 grey zone
        self.variant["Pos"] = "32398437"
        inGreyZone = calcVarPriors.varInGreyZone(self.variant)
        self.assertFalse(inGreyZone)

        # checks that variant in BRCA2 grey zone is identified as in BRCA2 grey zone
        self.variant["Pos"] = "32398459"
        inGreyZone = calcVarPriors.varInGreyZone(self.variant)
        self.assertTrue(inGreyZone)
        
    def test_varAfterGreyZoneBRCA1(self):
        '''Tests that variant in BRCA1 is NOT considered as after the grey zone'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks that BRCA1 variant is NOT considered after grey zone
        self.variant["Pos"] = "43045689"
        afterGreyZone = calcVarPriors.varAfterGreyZone(self.variant)
        self.assertFalse(afterGreyZone)

    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = True)
    def test_varAfterGreyZoneFalseBRCA2(self, varInUTR, varInGreyZone):
        '''Tests that variant in BRCA2 is correctly identified as NOT after the grey zone'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        self.variant["Pos"] = "32398459"
        afterGreyZone = calcVarPriors.varAfterGreyZone(self.variant)
        self.assertFalse(afterGreyZone)
        
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    def test_varAfterGreyZoneFalseBRCA2(self, varInUTR, varInGreyZone):
        '''Tests that variant after BRCA2 grey zone is correctly identified as after the grey zone'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        
        self.variant["Pos"] = "32398489"
        afterGreyZone = calcVarPriors.varAfterGreyZone(self.variant)
        self.assertTrue(afterGreyZone)

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = True)
    def test_getVarLocationOutBounds(self, varOutsideBoundaries):
        '''Tests that variants outside transcript boundaries are correctly identified as outside transcript boundaries'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        boundaries = "enigma"
        
        # BRCA1 variant outside transcript boundaries (before txn start)
        self.variant["Pos"] = "43125600"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["outBounds"])

        # BRCA1 variant outside transcript boundaries (after txn end)
        self.variant["Pos"] = "43044000"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["outBounds"])

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        boundaries = "enigma"
        
        # BRCA2 variant outside transcript boundaries (before txn start)
        self.variant["Pos"] = "32315300"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["outBounds"])

        # BRCA2 variant outside transcript boundaries (after txn end)
        self.variant["Pos"] = "32399800"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["outBounds"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = True)
    def test_getVarLocationCIDomain(self, varOutsideBoundaries, varInExon, varInSpliceRegion, varInCIDomain):
        '''
        Tests that variants in either PRIORS or ENIGMA CI domain and NOT in a splice region are
        identified as in CI domain
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        boundaries = "enigma"
        
        # BRCA1 variant in middle of ENIGMA CI domain
        self.variant["Pos"] = "43063930"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCI"])

        # BRCA1 variant in middle of PRIORS CI domain
        boundaries = "priors"
        self.variant["Pos"] = "43106502"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCI"])
        
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        boundaries = "enigma"
        
        # BRCA2 variant in middle of ENIGMA CI domain
        self.variant["Pos"] = "32376714"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCI"])

        # BRCA2 variant in middle of PRIORS CI domain
        boundaries = "priors"
        self.variant["Pos"] = "32363207"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCI"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = True)
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca1RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    def test_getVarLocationCIDomainSpliceRegionBRCA1(self, varOutsideBoundaries, varInExon, varInCIDomain,
                                                     getRefSpliceDonorBoundaries, getSpliceAcceptorBoundaries):
        '''
        Tests that BRCA1 variants in either PRIORS or ENIGMA CI domains AND in splice region are
        correctly identified as in CI domain splice region
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
                
        # BRCA1 variant in ENIGMA CI domain splice donor region
        boundaries = "enigma"
        self.variant["Pos"] = "43104868"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCISpliceDonor"])
        
        # BRCA1 variant in PRIORS CI domain splice donor region
        boundaries = "priors"
        self.variant["Pos"] = "43106456"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCISpliceDonor"])

        # BRCA1 variant in ENIGMA CI domain splice acceptor region
        boundaries = "enigma"
        self.variant["Pos"] = "43063373"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCISpliceAcceptor"])

        # BRCA1 variant in PRIORS CI domain splice acceptor region
        boundaries = "priors"
        self.variant["Pos"] = "43057135"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCISpliceAcceptor"])
        
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = True)
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca2RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    def test_getVarLocationCIDomainSpliceRegionBRCA2(self, varOutsideBoundaries, varInExon, varInCIDomain,
                                                     getRefSpliceDonorBoundaries, getSpliceAcceptorBoundaries):
        '''
        Tests that BRCA2 variants in either PRIORS or ENIGMA CI domains AND in splice region are
        correctly identified as in CI domain splice region
        '''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # BRCA2 variant in ENIGMA CI splice donor region
        boundaries = "enigma"
        self.variant["Pos"] = "32357929"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCISpliceDonor"])

        # BRCA2 variant in PRIORS CI splice donor region
        boundaries = "priors"
        self.variant["Pos"] = "32316527"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCISpliceDonor"])

        # BRCA2 variant in ENIGMA CI splice acceptor region
        boundaries = "enigma"
        self.variant["Pos"] = "32376670"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCISpliceAcceptor"])

        # BRCA2 variant in PRIORS CI splice acceptor region
        boundaries = "priors"
        self.variant["Pos"] = "32363179"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCISpliceAcceptor"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca1RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    def test_getVarLocationSpliceRegionBRCA1(self, varOutsideBoundaries, getExonBoundaries, getRefSpliceDonorBoundaries,
                                             getSpliceAcceptorBoundaries):
        '''Tests that BRCA1 variants in splice regions are correctly identified as in splice regions'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        boundaries = "enigma"
        
        # BRCA1 variant in splice donor region
        self.variant["Pos"] = "43074331"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inSpliceDonor"])
        
        # BRCA1 variant in splice acceptor region
        self.variant["Pos"] = "43082575"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inSpliceAcceptor"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca2RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    def test_getVarLocationSpliceRegionBRCA2(self, varOutsideBoundaries, getExonBoundaries, getRefSpliceDonorBoundaries,
                                             getSpliceAcceptorBoundaries):
        '''Tests that BRCA1 variants in splice regions are correctly identified as in splice regions'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        boundaries = "enigma"
        
        # BRCA2 variant in splice donor region
        self.variant["Pos"] = "32333388"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inSpliceDonor"])
        
        # BRCA2 variant in splice acceptor region
        self.variant["Pos"] = "32329443"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inSpliceAcceptor"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    def test_getVarLocationInExon(self, varOutsideBoundaries, varInExon, varInSpliceRegion, varInCIDomain):
        '''Tests that variants in exons are correctly identified as in exons'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        boundaries = "enigma"

        # BRCA1 variant in exon
        self.variant["Pos"] = "43071220"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inExon"])
        
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        boundaries = "enigma"

        # BRCA2 variant in exon
        self.variant["Pos"] = "32336289"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inExon"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInUTR', return_value = True)
    def test_getVarLocationInUtrBRCA1(self, varOutsideBoundaries, getExonBoundaries, varInSpliceRegion, varInUTR):
        '''Tests that BRCA1 variants in UTR are correctly identified as in UTR'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        boundaries = "enigma"

        # BRCA1 variant in 5' UTR
        self.variant["Pos"] = "43124138"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inUTR"])

        # BRCA1 variant in 3' UTR
        self.variant["Pos"] = "43045660"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inUTR"])
        
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInUTR', return_value = True)
    def test_getVarLocationInUtrBRCA2(self, varOutsideBoundaries, getExonBoundaries, varInSpliceRegion, varInUTR):
        '''Tests that BRCA2 variants in UTR are correctly identified as in UTR'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        boundaries = "enigma"

        # BRCA2 variant in 5' UTR
        self.variant["Pos"] = "32316398"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inUTR"])

        # BRCA2 variant in 3' UTR
        self.variant["Pos"] = "32398790"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inUTR"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    def test_getVarLocationInIntron(self, varOutsideBoundaries, varInExon, varInSpliceRegion):
        '''Tests that variants in introns are correctly identified as in introns'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        boundaries = "enigma"

        # BRCA1 variant in intron
        self.variant["Pos"] = "43071263"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inIntron"])

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        boundaries = "enigma"
        
        # BRCA2 variant in intron
        self.variant["Pos"] = "32344537"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inIntron"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = True)
    def test_getVarLocationInGreyZone(self, varOutsideBoundaries, varInExon, varInSpliceRegion, varInGreyZone):
        '''Tests that BRCA2 variant in grey zone is correctly identified as in grey zone'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        boundaries = "enigma"

        # BRCA2 variant in grey zone
        self.variant["Pos"] = "32398465"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inGreyZone"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = True)
    def test_getVarLocationAfterGreyZone(self, varOutsideBoundaries, varInExon, varInSpliceRegion, varAfterGreyZone):
        '''Tests that BRCA2 variant after grey zone is correctly identified as after grey zone'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        boundaries = "enigma"

        # BRCA2 variant after grey zone
        self.variant["Pos"] = "32398499"
        varLoc = calcVarPriors.getVarLocation(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["afterGreyZone"])

    @mock.patch('calcVarPriors.getFastaSeq', return_value = brca1Seq)    
    def test_getSeqLocDictBRCA1(self, getFastaSeq):
        '''
        Tests that boundary endpoints for BRCA1 are:
        1. Included in dictionary
        2. Have the correct base based on mocked sequence
        '''
        chrom = "chr17"
        strand = "-"
        rangeStart = 43051137
        rangeStop = 43051115
        seqLocDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.assertEquals(seqLocDict[rangeStart], brca1Seq[-1])
        self.assertEquals(seqLocDict[rangeStop], brca1Seq[0])
        
    @mock.patch('calcVarPriors.getFastaSeq', return_value = brca2Seq)
    def test_getSeqLocDictBRCA2(self, getFastaSeq):
        '''
        Tests that boundary endpoints for BRCA2 are:
        1. Included in dictionary
        2. Have the correct base based on mocked sequence
        '''
        chrom = "chr13"
        strand = "+"
        rangeStart = 32370936
        rangeStop = 32370958
        seqLocDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.assertEquals(seqLocDict[rangeStart], brca2Seq[0])
        self.assertEquals(seqLocDict[rangeStop], brca2Seq[-1])

    @mock.patch('calcVarPriors.getFastaSeq', return_value = brca1Seq)
    def test_getAltSeqDictBRCA1(self, getFastaSeq):
        '''
        Tests that for given variant genomic position:
        1. Reference allele is set correctly in original dictionary (refSeqDict)
        2. Alternate allele is set correctly in alternate sequence dicitonary (altSeqDict)
        '''
        chrom = "chr17"
        strand = "-"
        rangeStart = 43051137
        rangeStop = 43051115
        refSeqDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.variant["Pos"] = "43051120"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        altSeqDict = calcVarPriors.getAltSeqDict(self.variant, refSeqDict)
        self.assertEquals(refSeqDict[int(self.variant["Pos"])], self.variant["Ref"])
        self.assertEquals(altSeqDict[int(self.variant["Pos"])], self.variant["Alt"])

    @mock.patch('calcVarPriors.getFastaSeq', return_value = brca2Seq)
    def test_getAltSeqDictBRCA2(self, getFastaSeq):
        '''
        Tests that for given variant genomic position:
        1. Reference allele is set correctly in original dictionary (refSeqDict)
        2. Alternate allele is set correctly in alternate sequence dictionary (altSeqDict)
        '''
        chrom = "chr13"
        strand = "+"
        rangeStart = 32370936
        rangeStop = 32370958
        refSeqDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.variant["Pos"] = "32370944"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        altSeqDict = calcVarPriors.getAltSeqDict(self.variant, refSeqDict)
        self.assertEquals(refSeqDict[int(self.variant["Pos"])], self.variant["Ref"])
        self.assertEquals(altSeqDict[int(self.variant["Pos"])], self.variant["Alt"])

    @mock.patch('calcVarPriors.getFastaSeq', return_value = brca1Seq)
    def test_getAltSeqBRCA1(self, getFastaSeq):
        '''Tests that alternate sequence string generated is correct for - strand gene (BRCA1)'''
        chrom = "chr17"
        strand = "-"
        rangeStart = 43051137
        rangeStop = 43051115
        refSeqDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.variant["Pos"] = "43051120"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        altSeqDict = calcVarPriors.getAltSeqDict(self.variant, refSeqDict)
        altSeq = calcVarPriors.getAltSeq(altSeqDict, strand)
        # reference sequence on plus strand
        brca1RefSeq = "GATCTGGAAGAAGAGAGGAAGAG"
        # reverse complement with variant included
        brca1AltSeq = "CTCTTCCTCTCTTCTTCGAGATC"
        self.assertEquals(altSeq, brca1AltSeq)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = brca2Seq)
    def test_getAltSeqBRCA2(self, getFastaSeq):
        '''Tests that alternate sequence string generated is correct for + strand gene (BRCA2)'''
        chrom = "chr13"
        strand = "+"
        rangeStart = 32370936
        rangeStop = 32370958
        refSeqDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.variant["Pos"] = "32370944"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        altSeqDict = calcVarPriors.getAltSeqDict(self.variant, refSeqDict)
        altSeq = calcVarPriors.getAltSeq(altSeqDict, strand)
        # reference sequence on plus strand
        brca2RefSeq = "TGTGTAACACATTATTACAGTGG"
        # alternate sequence containng the alterante allele
        brca2AltSeq = "TGTGTAACCCATTATTACAGTGG"
        self.assertEquals(altSeq, brca2AltSeq)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = brca1Seq)
    def test_getRefAltSeqsBRCA1(self, getFastaSeq):
        '''Tests that ref and alt sequence are generated correctly for - strand gene (BRCA1)'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        rangeStart = 43051137
        rangeStop = 43051115
        self.variant["Pos"] = "43051120"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        refAltSeqs = calcVarPriors.getRefAltSeqs(self.variant, rangeStart, rangeStop)
        # reference sequence on plus strand
        brca1RefSeq = "GATCTGGAAGAAGAGAGGAAGAG"
        # reference sequence on minus strand
        brca1RefMinusSeq = "CTCTTCCTCTCTTCTTCCAGATC"
        # reverse complement with variant included
        brca1AltSeq = "CTCTTCCTCTCTTCTTCGAGATC"
        self.assertEquals(refAltSeqs["refSeq"], brca1RefSeq)
        self.assertEquals(refAltSeqs["altSeq"], brca1AltSeq)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = brca2Seq)
    def test_getRefAltSeqsBRCA2(self, getFastaSeq):
        '''Tests that ref and alt sequence are generated correctly for + strand gene (BRCA2)'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        rangeStart = 32370936
        rangeStop = 32370958
        self.variant["Pos"] = "32370944"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        refAltSeqs = calcVarPriors.getRefAltSeqs(self.variant, rangeStart, rangeStop)
        # reference sequence on plus strand
        brca2RefSeq = "TGTGTAACACATTATTACAGTGG"
        # alternate sequence containng the alterante allele
        brca2AltSeq = "TGTGTAACCCATTATTACAGTGG"
        self.assertEquals(refAltSeqs["refSeq"], brca2RefSeq)
        self.assertEquals(refAltSeqs["altSeq"], brca2AltSeq)

    def test_getVarSeqIndexSNSDiffLengths(self):
        '''Tests that function returns None for ref and alt seqs of different lengths'''
        refSeq = "ACTGTACTC"
        altSeq = "ACTGTAACTC"
        varIndex = calcVarPriors.getVarSeqIndexSNS(refSeq, altSeq)
        self.assertEquals(varIndex, "N/A")

    def test_getVarSeqIndexSNSDiffCases(self):
        '''Tests that function returns correct index for ref and alt seqs that have different cases'''
        refSeq = "TGTGTAACACGTAATTACAGTGG"
        altSeq = "tgtgtaacacgtaattacagtcg"
        varIndex = calcVarPriors.getVarSeqIndexSNS(refSeq, altSeq)
        self.assertEquals(varIndex, 21)

    def test_getVarSeqIndexSNSSameCase(self):
        '''Tests that function returns correct index for ref and alt seqs that are the same case'''
        refSeq = "ctagtcgtt"
        altSeq = "ctactcgtt"
        varIndex = calcVarPriors.getVarSeqIndexSNS(refSeq, altSeq)
        self.assertEquals(varIndex, 3)

    def test_getZScore(self):
        '''
        Tests that:
        1. For score in splice donor site:
            - checks that zscore is less than zero if MaxEntScan score less than donor mean
            - checks that zscore is greater than zero if MaxEntScan score is greater than donor mean
        2. For score in splice acceptor site:
            - checks that zscore is less than zero if MaxEntScan score is less than acceptor mean
            - checks that zscore is greater than zero if MaxEntScan score is greater than acceptor mean
        '''
        # score less than donor mean of ~7.94
        maxEntScanScore = 7.8
        zScore = calcVarPriors.getZScore(maxEntScanScore, donor=True)
        self.assertLess(zScore, 0)

        # score greater than donor mean of ~7.94
        maxEntScanScore = 7.99
        zScore = calcVarPriors.getZScore(maxEntScanScore, donor=True)
        self.assertGreater(zScore, 0)

        # score less than acceptor mean of ~7.98
        maxEntScanScore = 7.9
        zScore = calcVarPriors.getZScore(maxEntScanScore, donor=False)
        self.assertLess(zScore, 0)

        # score less than acceptor mean of ~7.98
        maxEntScanScore = 8
        zScore = calcVarPriors.getZScore(maxEntScanScore, donor=False)
        self.assertGreater(zScore, 0)

    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {"inExonicPortion": True})
    def test_varInExonicPortionTrue(self, getMaxMaxEntScanScoreSlidingWindowSNS):
        '''Tests that varInExonicPortion returns True if variant is in exonic portion of window'''
        inExonicPortion = calcVarPriors.varInExonicPortion(self.variant, STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH, donor=True)
        self.assertTrue(inExonicPortion)

    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {"inExonicPortion": False})
    def test_varInExonicPortionFalse(self, getMaxMaxEntScanScoreSlidingWindowSNS):
        '''Tests that varInExonicPortion returns False if variant is NOT in exonic portion of window'''
        inExonicPortion = calcVarPriors.varInExonicPortion(self.variant, STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH, donor=False)
        self.assertFalse(inExonicPortion)

    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {"varWindowPosition": 2})
    def test_getVarWindowPositionDonorFirstThree(self, getMaxMaxEntScanScoreSlidingWindowSNS):
        '''Tests that function returns correct value for variant in first 3 bp of window'''
        windowPos = calcVarPriors.getVarWindowPosition(self.variant, donor=True)
        self.assertEquals(windowPos, 2)

    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {"varWindowPosition": 7})
    def test_getVarWindowPositionDonorLastSix(self, getMaxMaxEntScanScoreSlidingWindowSNS):
        '''Tests that function returns correct value for variant after first 3 bp of window'''
        windowPos = calcVarPriors.getVarWindowPosition(self.variant, donor=True)
        self.assertEquals(windowPos, 7)

    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {"varWindowPosition": 18})
    def test_getVarWindowPositionAcceptor(self, getMaxMaxEntScanScoreSlidingWindowSNS):
        '''Tests that functions returns correct value for de novo acceptor variant'''
        windowPos = calcVarPriors.getVarWindowPosition(self.variant, donor=False)
        self.assertEquals(windowPos, 18)

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getClosestExonNumberIntronicSNSDonorCloseToSpliceAccBRCA1(self, getVarLocation, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref donor site for minus strand gene (BRCA1) variant close to ref splice acceptor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.4097-23a>C"
        self.variant["Pos"] = "43091055"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=True)
        self.assertEquals(closestExonNumber, "exon11")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getClosestExonNumberIntronicSNSAccCloseToSpliceAccBRCA2(self, getVarLocation, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref acceptor site for plus strand gene (BRCA2) variant close to ref splice acceptor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.8755-22c>A"
        self.variant["Pos"] = "32379295"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "A"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=False)
        self.assertEquals(closestExonNumber, "exon22")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getClosestExonNumberIntronicSNSDonorCloseToSpliceDonorBRCA2(self, getVarLocation, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref donor site for plus strand gene (BRCA2) variant close to ref splice donor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.9256+16g>A"
        self.variant["Pos"] = "32380161"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "A"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=True)
        self.assertEquals(closestExonNumber, "exon24")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getClosestExonNumberIntronicSNSAccCloseToSpliceDonorBRCA1(self, getVarLocation, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref acceptor site for minus strand gene (BRCA1) variant close to ref splice donor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.301+14a>G"
        self.variant["Pos"] = "43104854"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=False)
        self.assertEquals(closestExonNumber, "exon7")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getClosestExonNumberIntronicSNSDonor5PrimeUTRIntronBRCA2(self, getVarLocation, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref donor for plus strand gene (BRCA2) variant in intronic portion of 5' UTR'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.-39-24g>C"
        self.variant["Pos"] = "32316398"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=True)
        self.assertEquals(closestExonNumber, "exon1")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getClosestExonNumberIntronicSNSAcc5PrimeUTRIntronBRCA1(self, getVarLocation, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref acceptor for minus strand gene (BRCA1) variant in intronic portion of 5' UTR'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.-19-23t>G"
        self.variant["Pos"] = "43124138"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=False)
        self.assertEquals(closestExonNumber, "exon2")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getClosestExonNumberIntronicSNSDonor5PrimeUTRExonBRCA1(self, getVarLocation, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref donor for minus strand gene (BRCA1) variant in exonic portion of 5' UTR'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.-14T>C"
        self.variant["Pos"] = "43124110"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=True)
        self.assertEquals(closestExonNumber, "exon0")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getClosestExonNumberIntronicSNSAcc5PrimeUTRExonBRCA2(self, getVarLocation, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref acceptor for plus strand gene (BRCA2) variant in exonic portion of 5' UTR'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.-33T>A"
        self.variant["Pos"] = "32316428"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=False)
        self.assertEquals(closestExonNumber, "exon0")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getClosestExonNumberIntronicSNSDonorLastIntronBRCA1(self, getVarLocation, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref donor for minus strand gene (BRCA1) variant in last intron of gene'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.5468-25c>A"
        self.variant["Pos"] = "43045827"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "T"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=True)
        self.assertEquals(closestExonNumber, "exon23")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getClosestExonNumberIntronicSNSAccLastIntronBRCA2(self, getVarLocation, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref acceptor for plus strand gene (BRCA2) variant in last intron of gene'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.9649-24g>A"
        self.variant["Pos"] = "32398138"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "A"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=False)
        self.assertEquals(closestExonNumber, "exon27")
                                                      
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inCI"])
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon18")
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca1RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "tctgtaagt")
    def test_getClosestSpliceSiteScoresInExonDonorBRCA1(self, varInExon, getVarLocation, getVarExonNumberSNS,
                                                        getRefSpliceDonorBoundaries, varInSpliceRegion, getFastaSeq):
        '''Tests function for variant in exon to get closest splice donor site in minus strand gene (BRCA1)'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.5104A>G"
        self.variant["Pos"] = "43063922"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        deNovoOffset = 0
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, deNovoOffset, donor=True,
                                                                 deNovo=False, deNovoDonorInRefAcc=True, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon18")
        self.assertEquals(closestScores["sequence"], "TCTGTAAGT")

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inExon"])
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon8")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "CATAAATTTTTATCTTACAGTCA")
    def test_getClosestSpliceSiteScoresInExonAccBRCA2(self, varInExon, getVarLocation, getVarExonNumberSNS,
                                                      getSpliceAcceptorBoundaries, varInSpliceRegion, getFastaSeq):
        '''Tests function for variant in exon to get closest splice acceptor site in plus strand gene (BRCA2)'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.648A>G"
        self.variant["Pos"] = "32329459"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        deNovoOffset = 0
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, deNovoOffset, donor=False,
                                                                 deNovo=False, deNovoDonorInRefAcc=False, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon8")
        self.assertEquals(closestScores["sequence"], "CATAAATTTTTATCTTACAGTCA")

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inCISpliceDonor"])
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon20")
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca2RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon20',
                                                                          'donorStart': 32371098,
                                                                          'donorEnd': 32371106})
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "AAGGTAAAA")
    def test_getClosestSpliceSiteScoresInRefDonorExonicBRCA2(self, varInExon, getVarLocation, getVarExonNumberSNS,
                                                             getRefSpliceDonorBoundaries, varInSpliceRegion,
                                                             getVarSpliceRegionBounds, getFastaSeq):
        '''Tests function for variant in exonic portion of ref donor site to get closest splice donor site in plus strand gene (BRCA2)'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.8631A>T"
        self.variant["Pos"] = "32371099"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        deNovoOffset = 0
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, deNovoOffset, donor=True,
                                                                 deNovo=False, deNovoDonorInRefAcc=False, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon20")
        self.assertEquals(closestScores["sequence"], "AAGGTAAAA")

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inSpliceAcceptor"])
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 43106553,
                                                                          'exonName': 'exon5',
                                                                          'acceptorEnd': 43106531})
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "tctttctttataatttatagatt")
    def test_getClosestSpliceSiteScoresInRefAccIntronicBRCA1(self, getVarLocation, varInExon, varInSpliceRegion,
                                                             getVarSpliceRegionBounds, getFastaSeq):
        '''
        Tests function for variant in intronic portion of ref acceptor site 
        to get closest splice acceptor site in minus strand gene (BRCA1)
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.135-11a>C"
        self.variant["Pos"] = "43106544"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        deNovoOffset = 0
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, deNovoOffset, donor=False,
                                                                 deNovo=False, deNovoDonorInRefAcc=False, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon5")
        self.assertEquals(closestScores["sequence"], "TCTTTCTTTATAATTTATAGATT")

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inExon"])
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 32325056,
                                                                          'exonName': 'exon4',
                                                                          'acceptorEnd': 32325085})
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "GAATTATTGTACTGTTTCAGGAA")
    def test_getClosestSpliceSiteScoresInDeNovoAccBRCA2(self, getVarLocation, varInExon, varInSpliceRegion,
                                                        getVarSpliceRegionBounds, getFastaSeq):
        '''Tests function for variant in exon to get closest splice acceptor site for de novo acceptor in plus strand gene (BRCA2)'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.320G>C"
        self.variant["Pos"] = "32325079"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, STD_DE_NOVO_OFFSET, donor=False,
                                                                 deNovo=True, deNovoDonorInRefAcc=False, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon4")
        self.assertEquals(closestScores["sequence"], "GAATTATTGTACTGTTTCAGGAA")

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon3")
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca1RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "CAAGTAAGT")
    def test_getClosestSpliceSiteScoresInIntronDonorBRCA1(self, varInExon, getVarLocation, getClosestExonNumberIntronicSNS,
                                                          getRefSpliceDonorBoundaries, varInSpliceRegion, getFastaSeq):
        '''Tests function for variant in intron to get closest splice donor site for a de novo donor in minus strand gene (BRCA1)'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.135-24t>C"
        self.variant["Pos"] = "43106557"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, STD_DE_NOVO_OFFSET, donor=True, deNovo=False,
                                                                 deNovoDonorInRefAcc=False, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon3")
        self.assertEquals(closestScores["sequence"], "CAAGTAAGT")

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon26")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TTTTCCACTTATTTTCTTAGAAT")
    def test_getClosestSpliceSiteScoresInIntronAccBRCA2(self, varInExon, getVarLocation, getClosestExonNumberIntronicSNS,
                                                        getSpliceAcceptorBoundaries, varInSpliceRegion,getFastaSeq):
        '''Tests function for variant in intron to gest closest splice acceptor site for a de novo acceptor in plus strand gene (BRCA2)'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.9501+18c>T"
        self.variant["Pos"] = "32394951"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        deNovoOffset = 0
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, deNovoOffset, donor=False, deNovo=True,
                                                                 deNovoDonorInRefAcc=False, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon26")
        self.assertEquals(closestScores["sequence"], "TTTTCCACTTATTTTCTTAGAAT")

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon1")
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca2RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "CGGGTTAGT")
    def test_getClosestSpliceSiteScoresInUTRDonorBRCA2(self, varInExon, getVarLocation, getClosestExonNumberIntronicSNS,
                                                       getRefSpliceDonorBoundaries, varInSpliceRegion, getFastaSeq):
        '''Tests function for variant in UTR to get closest splice donor site for a de novo donor in plus strand gene (BRCA2)'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.-39-25t>A"
        self.variant["Pos"] = "32316397"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, STD_DE_NOVO_OFFSET, donor=True, deNovo=False,
                                                                 deNovoDonorInRefAcc=False, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon1")
        self.assertEquals(closestScores["sequence"], "CGGGTTAGT")

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon2")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "gtttttctaatgtgttaaagttc")
    def test_getClosestSpliceSiteScoresInUTRAccBRCA1(self, varInExon, getVarLocation, getClosestExonNumberIntronicSNS,
                                                     getSpliceAcceptorBoundaries, varInSpliceRegion, getFastaSeq):
        '''Tests function for variant in UTR to get closest splice acceptor site for a de novo acceptor in minus strand gene (BRCA1)'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.-19-25t>G"
        self.variant["Pos"] = "43124140"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        deNovoOffset = 0
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, deNovoOffset, donor=False, deNovo=True,
                                                                 deNovoDonorInRefAcc=False, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon2")
        self.assertEquals(closestScores["sequence"], "GTTTTTCTAATGTGTTAAAGTTC")

    def test_isCIDomainInRegionBRCA1(self):
        '''
        Tests that region overlap is identified correctly for a variant on minus strand gene (BRCA1)
        '''
        self.variant["Gene_Symbol"] = "BRCA1"

        boundaries = "enigma"
        # region that includes ENIGMA BRCT domain
        regionStart = 43067625
        regionEnd = 43063950
        CIDomainInRegion = calcVarPriors.isCIDomainInRegion(regionStart, regionEnd, boundaries, self.variant["Gene_Symbol"])
        self.assertTrue(CIDomainInRegion)

        # region that does not include any PRIORS CI domains
        boundaries = "priors"
        regionStart = 43095923
        regionEnd = 43095857
        CIDomainInRegion = calcVarPriors.isCIDomainInRegion(regionStart, regionEnd, boundaries, self.variant["Gene_Symbol"])
        self.assertFalse(CIDomainInRegion)

    def test_isCIDomainInRegionBRCA2(self):
        '''
        Tests that region overlap is identified correctly for a variant on plus strand gene (BRCA2)
        '''
        self.variant["Gene_Symbol"] = "BRCA2"

        # region that does not include any ENIGMA CI domains
        boundaries = "enigma"
        regionStart = 32319089
        regionEnd = 32325063
        CIDomainInRegion = calcVarPriors.isCIDomainInRegion(regionStart, regionEnd, boundaries, self.variant["Gene_Symbol"])
        self.assertFalse(CIDomainInRegion)

        # region that includeds PRIORS DNB domain
        boundaries = "priors"
        regionStart = 32379502
        regionEnd = 32379751
        CIDomainInRegion = calcVarPriors.isCIDomainInRegion(regionStart, regionEnd, boundaries, self.variant["Gene_Symbol"])
        self.assertTrue(CIDomainInRegion)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon9")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getRefExonLengthDonorInExonBRCA1(self, varInExon, getVarExonNumberSNS, getExonBoundaries, getVarStrand):
        '''Tests that exon length for variant in exon is correctly calculated for minus strand (BRCA1) exon'''
        self.variant["Gene_Symbol"] = "BRCA1"
        exon9PlusSeq = "CTGCAATAAGTTGCCTTATTAACGGTATCTTCAGAAGAATCAGATC"
        refExonLength = calcVarPriors.getRefExonLength(self.variant, donor=True)
        self.assertEquals(refExonLength, len(exon9PlusSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon5")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getRefExonLengthAccInExonBRCA2(self, varInExon, getVarExonNumberSNS, getExonBoundaries, getVarStrand):
        '''Tests that exon length for variant in exon is correctly calculated for plus strand (BRCA2) exon'''
        self.variant["Gene_Symbol"] = "BRCA2"
        exon5PlusSeq = "TCCTGTTGTTCTACAATGTACACATGTAACACCACAAAGAGATAAGTCAG"
        refExonLength = calcVarPriors.getRefExonLength(self.variant, donor=False)
        self.assertEquals(refExonLength, len(exon5PlusSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon8',
                                                                          'donorStart': 32329490,
                                                                          'donorEnd': 32329498})
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getRefExonLengthDonorInIntronicRefDonorBRCA2(self, varInExon, varInSpliceRegion, getVarSpliceRegionBounds,
                                                          getExonBoundaries, getVarStrand):
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Pos"] = "32329494"
        exon8PlusSeq = "TCAGAAATGAAGAAGCATCTGAAACTGTATTTCCTCATGATACTACTGCT"
        refExonLength = calcVarPriors.getRefExonLength(self.variant, donor=True)
        self.assertEquals(refExonLength, len(exon8PlusSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 43104976,
                                                                          'exonName': 'exon6',
                                                                          'acceptorEnd': 43104954})
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getRefExonLengthAccInIntronicRefAccBRCA1(self, varInExon, varInSpliceRegion, getVarSpliceRegionBounds,
                                                      getExonBoundaries, getVarStrand):
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Pos"] = "43104959"
        exon6MinusSeq = "gagcctacaagaaagtacgagatttagtcaacttgttgaagagctattgaaaatcatttgtgcttttcagcttgacacaggtttggagt"
        refExonLength = calcVarPriors.getRefExonLength(self.variant, donor=False)
        self.assertEquals(refExonLength, len(exon6MinusSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon3")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getRefExonLengthDonorInIntronBRCA1(self, varInExon, varInSpliceRegion, getClosestExonNumberIntronicSNS,
                                                getExonBoundaries, getVarStrand):
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Pos"] = "43115715"
        exon3MinusSeq = "tctggagttgatcaaggaacctgtctccacaaagtgtgaccacatattttgcaa"
        refExonLength = calcVarPriors.getRefExonLength(self.variant, donor=True)
        self.assertEquals(refExonLength, len(exon3MinusSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon13")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getRefExonLengthAccInIntronBRCA2(self, varInExon, varInSpliceRegion, getClosstExonNumberIntronicSNS,
                                              getExonBoundaries, getVarStrand):
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Pos"] = "32346804"
        exon13PlusSeq = "GCACAATAAAAGATCGAAGATTGTTTATGCATCATGTTTCTTTAGAGCCGATTACCTGTGTACCCTTTCG"
        refExonLength = calcVarPriors.getRefExonLength(self.variant, donor=False)
        self.assertEquals(refExonLength, len(exon13PlusSeq))

    def test_getNewSplicePositionBRCA1DonorInExonicPortion(self):
        '''Tests that new splice position is calculated correctly for minus strand (BRCA1) variant with max donor MES in exonic portion'''
        varStrand = "-"
        inExonicPortion = True
        varGenPos = "43104189"
        varWindowPos = 3
        newSplicePos = calcVarPriors.getNewSplicePosition(varGenPos, varStrand, varWindowPos, inExonicPortion,
                                                          STD_EXONIC_PORTION, STD_DONOR_INTRONIC_LENGTH, donor=True)
        # because varWindowPos == 3, cut will occur after variant
        actualNewSplicePos = 43104189
        self.assertEquals(newSplicePos, actualNewSplicePos)

    def test_getNewSplicePositionBRCA1AccInExonicPortion(self):
        '''Tests that new splice position is calculated correctly for minus strand (BRCA1) variant with max acceptor MES in exonic portion'''
        varStrand = "-"
        inExonicPortion = True
        varGenPos = "43095922"
        varWindowPos = 23
        newSplicePos = calcVarPriors.getNewSplicePosition(varGenPos, varStrand, varWindowPos, inExonicPortion,
                                                          STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH, donor=False)
        # because varWindowPos == 23, cut will occur 3 bases to the left of the variant
        actualNewSplicePos = 43095925
        self.assertEquals(newSplicePos, actualNewSplicePos)
        
    def test_getNewSplicePositionBRCA1DonorNotInExonicPortion(self):
        '''Tests that new splice position is calculated correctly for minus strand (BRCA1) variant with max donor MES NOT in exonic portion'''
        varStrand = "-"
        inExonicPortion = False
        varGenPos = "43104249"
        varWindowPos = 6
        newSplicePos = calcVarPriors.getNewSplicePosition(varGenPos, varStrand, varWindowPos, inExonicPortion,
                                                          STD_EXONIC_PORTION, STD_DONOR_INTRONIC_LENGTH, donor=True)
        # because varWindowPos == 6, cut will occur 3 bases to the left of the variant
        actualNewSplicePos = 43104252
        self.assertEquals(newSplicePos, actualNewSplicePos)

    def test_getNewSplicePositionBRCA1AccNotInExonicPortion(self):
        '''Tests that new splice position is calculated correctly for minus strand (BRCA1) variant with max acceptor MES NOT in exonic portion'''
        varStrand = "-"
        inExonicPortion = True
        varGenPos = "43063373"
        varWindowPos = 19
        newSplicePos = calcVarPriors.getNewSplicePosition(varGenPos, varStrand, varWindowPos, inExonicPortion,
                                                          STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH, donor=False)
        # because varWindowPos == 19, cut will occur 1 base to the right of the variant
        actualNewSplicePos = 43063374
        self.assertEquals(newSplicePos, actualNewSplicePos)
        
    def test_getNewSplicePositionBRCA2DonorInExonicPortion(self):
        '''Tests that new splice position is calculated correctly for plus strand (BRCA2) variant with max donor MES in exonic portion'''
        varStrand = "+"
        inExonicPortion = True
        varGenPos = "32354881"
        varWindowPos = 2
        newSplicePos = calcVarPriors.getNewSplicePosition(varGenPos, varStrand, varWindowPos, inExonicPortion,
                                                          STD_EXONIC_PORTION, STD_DONOR_INTRONIC_LENGTH, donor=True)
        # because varWindowPos == 2, cut will occur 1 base to the right of the variant
        actualNewSplicePos = 32354882
        self.assertEquals(newSplicePos, actualNewSplicePos)

    def test_getNewSplicePositionBRCA2AccInExonicPortion(self):
        '''Tests that new splice position is calcualted correctly for plus strand (BRCA2) variant with max acceptor MES in exonic portion'''
        varStrand = "+"
        inExonicPortion = True
        varGenPos = "32326500"
        varWindowPos = 21
        newSplicePos = calcVarPriors.getNewSplicePosition(varGenPos, varStrand, varWindowPos, inExonicPortion,
                                                          STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH, donor=False)
        # because varWindowPos == 21, cut will occur before variant
        actualNewSplicePos = 32326499
        self.assertEquals(newSplicePos, actualNewSplicePos)
        
    def test_getNewSplicePositionBRCA2DonorNotInExonicPortion(self):
        '''Tests that new splice position is calculated correctly for plus strand (BRCA2) variant with max donor MES NOT in exonic portion'''
        varStrand = "+"
        inExonicPortion = False
        varGenPos = "32326277"
        varWindowPos = 8
        newSplicePos = calcVarPriors.getNewSplicePosition(varGenPos, varStrand, varWindowPos, inExonicPortion,
                                                          STD_EXONIC_PORTION, STD_DONOR_INTRONIC_LENGTH, donor=True)
        # because varWindowPos == 8, cut will occur 5 bases to the left of the variant
        actualNewSplicePos = 32326272
        self.assertEquals(newSplicePos, actualNewSplicePos)

    def test_getNewSplicePositionBRCA2AccNotInExonicPortion(self):
        '''Tests that new splice position is calculated correclty for plus strand (BRCA2) variant with max acceptor MES NOT in exonic portion'''
        varStrand = "+"
        inExonicPortion = True
        varGenPos = "32332274"
        varWindowPos = 5
        newSplicePos = calcVarPriors.getNewSplicePosition(varGenPos, varStrand, varWindowPos, inExonicPortion,
                                                          STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH, donor=False)
        # because varWindowPos == 5, cut will occur 15 bases to the right of the variant
        actualNewSplicePos = 32332289
        self.assertEquals(newSplicePos, actualNewSplicePos)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon21")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'refMaxEntScanScore': -9.9,
                                                                                       'altMaxEntScanScore': -7.45,
                                                                                       'altZScore': -6.6071787973194605,
                                                                                       'inExonicPortion': True,
                                                                                       'varWindowPosition': 2,
                                                                                       'refZScore': -7.659134374464476})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43051109)
    def test_getAltExonLengthBRCA1(self, varInExon, getVarExonNumberSNS, getExonBoundaries,
                                   getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''Tests that exon length is correctly calculated for minus strand (BRCA1) exon'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["HGVS_cDNA"] = "c.5285G>C"
        expectedCutSeq = "ATCTTCACG"
        altExonLength = calcVarPriors.getAltExonLength(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(altExonLength, len(expectedCutSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon13")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'refMaxEntScanScore': -9.89,
                                                                                       'altMaxEntScanScore': -1.7,
                                                                                       'altZScore': -4.13830346320361,
                                                                                       'varWindowPosition': 4,
                                                                                       'inExonicPortion': False,
                                                                                       'refZScore': -7.65484067823123})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32346831)
    def test_getAltExonLengthBRCA2(self, varInExon, getVarExonNumberSNS, getExonBoundaries,
                                   getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''Tests that exon length is correctly calculated for plus strand (BRCA2) exon'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["HGVS_cDNA"] = "c.6943A>G"
        expectedCutSeq = "GCACA"
        altExonLength = calcVarPriors.getAltExonLength(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(altExonLength, len(expectedCutSeq))

    def test_compareRefAltExonLengths(self):
        '''Tests that function correctly determines if ref and alt exons are in same reading frame'''
        # ref and alt exons that share the same reading frame
        refLength = 45
        altLength = 33
        inFrame = calcVarPriors.compareRefAltExonLengths(refLength, altLength)
        self.assertTrue(inFrame)

        # ref and alt exons that do NOT share the smae reading frame
        refLength = 162
        altLength = 103
        inFrame = calcVarPriors.compareRefAltExonLengths(refLength, altLength)
        self.assertFalse(inFrame)

    @mock.patch('calcVarPriors.getRefExonLength', return_value = 45)
    @mock.patch('calcVarPriors.getAltExonLength', return_value = 30)
    @mock.patch('calcVarPriors.compareRefAltExonLengths', return_value = True)    
    def test_isSplicingWindowInFrameTrue(self, getRefExonLength, getAltExonLength, compareRefAltExonLengths):
        '''Tests that if splicing window is in frame, function returns true'''
        inFrame = calcVarPriors.isSplicingWindowInFrame(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertTrue(inFrame)
        
    @mock.patch('calcVarPriors.getRefExonLength', return_value = 45)
    @mock.patch('calcVarPriors.getAltExonLength', return_value = 29)
    @mock.patch('calcVarPriors.compareRefAltExonLengths', return_value = False)    
    def test_isSplicingWindowInFrameFalse(self, getRefExonLength, getAltExonLength, compareRefAltExonLengths):
        '''Tests that if splicing window is NOT in frame, function returns false'''
        inFrame = calcVarPriors.isSplicingWindowInFrame(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertFalse(inFrame)        

    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon16")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'refMaxEntScanScore': -7.31,
                                                                                       'altMaxEntScanScore': -7.32,
                                                                                       'altZScore': -6.551360746287276,
                                                                                       'inExonicPortion': True,
                                                                                       'varWindowPosition': 1,
                                                                                       'refZScore': -6.547067050054031})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43070934)
    def test_compareDeNovoWildTypeSplicePosBRCA1True(self, getVarStrand, getVarExonNumberSNS, getExonBoundaries,
                                                     getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''
        Tests that comparsion between de novo and wild-type splice position is correct for a BRCA1 variant that:
            1. has highest scoring window with variant in first three nucleotides
            2. AND distance between de novo and wild-type donor is divisble by 3
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43070936"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        isDivisible = calcVarPriors.compareDeNovoWildTypeSplicePos(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertTrue(isDivisible)
        
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon9")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'refMaxEntScanScore': -2.95,
                                                                                       'altMaxEntScanScore': 5.56,
                                                                                       'altZScore': -1.0210799978677707,
                                                                                       'inExonicPortion': False,
                                                                                       'varWindowPosition': 4,
                                                                                       'refZScore': -4.67501549235923})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43097266)
    def test_compareDeNovoWildTypeSplicePosBRCA1False(self, getVarStrand, getVarExonNumberSNS, getExonBoundaries,
                                                      getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''
        Tests that comparsion between de novo and wild-type splice position is correct for a BRCA1 variant that:
            1. has highest scoring window with variant in last six nucleotides
            2. AND distance between de novo and wild-type donor is NOT divisble by 3
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43097265"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        isDivisible = calcVarPriors.compareDeNovoWildTypeSplicePos(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertFalse(isDivisible)
                
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon4")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'refMaxEntScanScore': -9.22,
                                                                                       'altMaxEntScanScore': -1.57,
                                                                                       'altZScore': -4.082485412171425,
                                                                                       'inExonicPortion': False,
                                                                                       'varWindowPosition': 5,
                                                                                       'refZScore': -7.367163030603819})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32325178)
    def test_compareDeNovoWildTypeSplicePosBRCA2True(self, getVarStrand, getVarExonNumberSNS, getExonBoundaries,
                                                     getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''
        Tests that comparsion between de novo and wild-type splice position is correct for a BRCA2 variant that:
            1. has highest scoring window with variant in last six nucleotides
            2. AND distance between de novo and wild-type donor is divisble by 3
        '''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32325180"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "T"
        isDivisible = calcVarPriors.compareDeNovoWildTypeSplicePos(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertTrue(isDivisible)

    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon23")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'refMaxEntScanScore': -3.67,
                                                                                       'altMaxEntScanScore': -0.32,
                                                                                       'altZScore': -3.5457733830158054,
                                                                                       'inExonicPortion': True,
                                                                                       'varWindowPosition': 2,
                                                                                       'refZScore': -4.984161621152867})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32379873)
    def test_compareDeNovoWildTypeSplicePosBRCA2False(self, getVarStrand, getVarExonNumberSNS, getExonBoundaries,
                                                      getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''
        Tests that comparsion between de novo and wild-type splice position is correct for a BRCA2 variant that:
            1. has highest scoring window with variant in first three nucleotides
            2. AND distance between de novo and wild-type donor is NOT divisble by 3
        '''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32379872"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "A"
        isDivisible = calcVarPriors.compareDeNovoWildTypeSplicePos(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertFalse(isDivisible)

    @unittest.skip
    # TO DO remove this skip
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = True)
    def test_getPriorProbSpliceRescueNonsenseSNSInLastExon(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon):
        '''Tests that variant in last exon is assigned correct prior prob and splice rescue flags'''
        boundaries = "enigma"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["pathogenic"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class5"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 0)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 0)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], 0)

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")    
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = True)
    def test_getPriorProbSpliceRescueNonsenseSNSInExonicPortion(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon, varInExonicPortion):
        '''Tests that variant in exonic portion of highest scoring window is assigned correct prior prob and splice rescue flag'''
        boundaries = "enigma"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["high"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class4"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 0)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 1)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 0)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], 0)

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = False)
    def test_getPriorProbSpliceRescueNonsenseSNSFrameshift(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon,
                                                           varInExonicPortion, isSplicingWindowInFrame):
        '''Tests that variant that causes a frameshift is assigned correct prior prob and splice rescue flag'''
        boundaries = "enigma"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["pathogenic"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class5"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 1)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 0)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], 0)

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon20")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 6)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = True)
    @mock.patch('calcVarPriors.compareDeNovoWildTypeSplicePos', return_value = True)
    def test_getPriorProbSpliceRescueNonsenseSNSCIRegionEnigma(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon,
                                                               varInExonicPortion, isSplicingWindowInFrame, getVarStrand,
                                                               getVarExonNumberSNS, getSpliceAcceptorBoundaries, getVarWindowPosition,
                                                               isCIDomainInRegion, compareDeNovoWildTypeSplicePos):
        '''Tests that variant that truncates part of ENGIMA CI domain is assigned correct prior prob and splice rescue flag'''
        boundaries = "enigma"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["pathogenic"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class5"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 0)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 1)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], 0)

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")    
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon2")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 7)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = True)
    @mock.patch('calcVarPriors.compareDeNovoWildTypeSplicePos', return_value = True)
    def test_getPriorProbSpliceRescueNonsenseSNSCIRegionPriors(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon,
                                                               varInExonicPortion, isSplicingWindowInFrame, getVarStrand,
                                                               getVarExonNumberSNS, getSpliceAcceptorBoundaries, getVarWindowPosition,
                                                               isCIDomainInRegion, compareDeNovoWildTypeSplicePos):
        '''Tests that variant that truncates part of PRIORS CI domain is assigned correct prior prob and splice rescue flag'''
        boundaries = "priors"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["pathogenic"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class5"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 0)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 1)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], 0)
        
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")        
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon6")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 4)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = False)
    @mock.patch('calcVarPriors.compareDeNovoWildTypeSplicePos', return_value = False)
    def test_getPriorProbSpliceRescueNonsenseSNSNotDivisible(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon,
                                                             varInExonicPortion, isSplicingWindowInFrame, getVarStrand,
                                                             getVarExonNumberSNS, getSpliceAcceptorBoundaries, getVarWindowPosition,
                                                             isCIDomainInRegion, compareDeNovoWildTypeSplicePos):
        '''
        Tests that variant that causes a frameshift (due to difference de novo vs wild-type splice position) 
        is assigned correct prior prob and splice rescue flag
        '''
        boundaries = "enigma"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["pathogenic"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class5"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 1)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 0)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], 1)

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon17")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 5)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = False)
    @mock.patch('calcVarPriors.compareDeNovoWildTypeSplicePos', return_value = True)
    def test_getPriorProbSpliceRescueNonsenseSNSWithSpliceFlag(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon,
                                                               varInExonicPortion, isSplicingWindowInFrame,
                                                               getVarStrand, getVarExonNumberSNS, getSpliceAcceptorBoundaries,
                                                               getVarWindowPosition, isCIDomainInRegion, compareDeNovoWildTypeSplicePos):
        '''Tests that variant with possibility of splice rescue is assigned correct splice rescue and splicing flag'''
        boundaries = "enigma"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["NA"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 1)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 1)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 0)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 0)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], 0)
        
    def test_getEnigmaClass(self):
        ''''
        Tests that predicted qualititative ENIGMA class is assigned correctly based on prior prob
        Specifically tests for priors in class 1 and class 5
        and most commonly assigned priorProb = 0.04, 0.34, and 0.97
        '''
        priorProb = 0.0001
        enigmaClass = calcVarPriors.getEnigmaClass(priorProb)
        self.assertEquals(enigmaClass, enigmaClasses["class1"])
        
        priorProb = 0.04
        enigmaClass = calcVarPriors.getEnigmaClass(priorProb)
        self.assertEquals(enigmaClass, enigmaClasses["class2"])

        priorProb = 0.34
        enigmaClass = calcVarPriors.getEnigmaClass(priorProb)
        self.assertEquals(enigmaClass, enigmaClasses["class3"])

        priorProb = 0.97
        enigmaClass = calcVarPriors.getEnigmaClass(priorProb)
        self.assertEquals(enigmaClass, enigmaClasses["class4"])
                
        priorProb = 0.995
        enigmaClass = calcVarPriors.getEnigmaClass(priorProb)
        self.assertEquals(enigmaClass, enigmaClasses["class5"])

        priorProb = "N/A"
        enigmaClass = calcVarPriors.getEnigmaClass(priorProb)
        self.assertEquals(enigmaClass, None)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCTTACCTT")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = brca1RefSpliceDonorBounds["exon14"])
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.57,
                                                                               "zScore": 1.1300618149879533},
                                                                 "altScores": {"maxEntScanScore": 9.21,
                                                                               "zScore": 0.5461191272666394}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 1)
    def test_getPriorProbRefSpliceDonorSNSLowProbBRCA1(self, getFastaSeq, getVarType, getVarLocation,
                                                       getVarSpliceRegionBounds, getRefAltScores,
                                                       getVarSeqIndexSNS):
        '''Tests function for BRCA1 variant that creates a resaonble splice donor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant that creates a reasonable splice donor site
        self.variant["Pos"] = "43076489"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["low"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["varStart"], 1)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCTTACCTT")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = brca1RefSpliceDonorBounds["exon14"])
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.57,
                                                                               "zScore": 1.1300618149879533},
                                                                 "altScores": {"maxEntScanScore": 6.12,
                                                                               "zScore": -0.7806330088060529}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 5)
    def test_getPriorProbRefSpliceDonorSNSModerateProbBRCA1(self, getFastaSeq, getVarType, getVarLocation,
                                                            getVarSpliceRegionBounds, getRefAltScores,
                                                            getVarSeqIndexSNS):
        '''Tests function for BRCA1 variant that weakens a reasonably strong splice donor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant that weakens a reasonably strong splice donor site
        self.variant["Pos"] = "43076485"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["moderate"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["varStart"], 5)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TTTTACCAA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = brca1RefSpliceDonorBounds["exon7"])
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 3.23,
                                                                               "zScore": -2.021511220213846},
                                                                 "altScores": {"maxEntScanScore": -4.42,
                                                                               "zScore": -5.306188838646238}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 4)
    def test_getPriorProbRefSpliceDonorSNSHighProbBRCA1(self, getFastaSeq, getVarType, getVarLocation,
                                                        getVarSpliceRegionBounds, getRefAltScores,
                                                        getVarSeqIndexSNS):
        '''Tests fucntion for BRCA1 variant that further weakens a weak splice donor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant that further weakens a weak splice donor site
        self.variant["Pos"] = "43104120"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["high"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class4"])
        self.assertEquals(priorProb["varStart"], 4)
        
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCTTACCTT")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = brca1RefSpliceDonorBounds["exon14"])
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.57,
                                                                               "zScore": 1.1300618149879533},
                                                                 "altScores": {"maxEntScanScore": 10.77,
                                                                               "zScore": 1.2159357396528523}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 0)
    def test_getPriorProbRefSpliceDonorSNSImprovedProbBRCA1(self, getFastaSeq, getVarType, getVarLocation,
                                                            getVarSpliceRegionBounds, getRefAltScores,
                                                            getVarSeqIndexSNS):
        '''Tests function for BRCA1 variant that makes a splice site stronger or equally strong'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant that makes a splice donor site stronger or equally strong
        self.variant["Pos"] = "43076490"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["low"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["varStart"], 0)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCGGTAAGA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = brca2RefSpliceDonorBounds["exon13"])
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.53,
                                                                               "zScore": 1.1128870300549731},
                                                                 "altScores": {"maxEntScanScore": 8.91,
                                                                               "zScore": 0.4173082402692903}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 1)
    def test_getPriorProbRefSpliceDonorSNSLowProbBRCA2(self, getFastaSeq, getVarType, getVarLocation,
                                                       getVarSpliceRegionBounds, getRefAltScores,
                                                       getVarSeqIndexSNS):
        '''Tests function for BRCA2 variant that creates a resaonble splice donor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant that creates a reasonable splice donor site
        self.variant["Pos"] = "32346895"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["low"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["varStart"], 1)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCGGTAAGA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = brca2RefSpliceDonorBounds["exon13"])
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.53,
                                                                               "zScore": 1.1128870300549731},
                                                                 "altScores": {"maxEntScanScore": 4.35,
                                                                               "zScore": -1.5406172420904107}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 5)
    def test_getPriorProbRefSpliceDonorSNSModerateProbBRCA2(self, getFastaSeq, getVarType, getVarLocation,
                                                            getVarSpliceRegionBounds, getRefAltScores,
                                                            getVarSeqIndexSNS):
        '''Tests function for BRCA2 variant that weakens a reasonably strong splice donor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant that weakens a reasonably strong splice donor site
        self.variant["Pos"] = "32346899"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["moderate"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["varStart"], 5)        
        
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "CAGGCAAGT")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = brca2RefSpliceDonorBounds["exon17"])
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 3.1,
                                                                               "zScore": -2.07732927124603},
                                                                 "altScores": {"maxEntScanScore": 0.56,
                                                                               "zScore": -3.1679281144902496}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 2)
    def test_getPriorProbRefSpliceDonorSNSHighProbBRCA2(self, getFastaSeq, getVarType, getVarLocation,
                                                        getVarSpliceRegionBounds, getRefAltScores,
                                                        getVarSeqIndexSNS):
        '''Tests fucntion for BRCA2 variant that further weakens a weak splice donor site'''  
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant that further weakens a weak splice donor site
        self.variant["Pos"] = "32362693"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["high"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class4"])
        self.assertEquals(priorProb["varStart"], 2)        
        
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCGGTAAGA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = brca2RefSpliceDonorBounds["exon13"])
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.53,
                                                                               "zScore": 1.1128870300549731},
                                                                 "altScores": {"maxEntScanScore": 11.78,
                                                                               "zScore": 1.649599059210593}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 8)
    def test_getPriorProbRefSpliceDonorSNSImprovedProbBRCA2(self, getFastaSeq, getVarType, getVarLocation,
                                                            getVarSpliceRegionBounds, getRefAltScores,
                                                            getVarSeqIndexSNS):
        '''Tests function for BRCA2 variant that makes a splice site stronger or equally strong'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant that makes a splice donor site stronger or equally strong
        self.variant["Pos"] = "32346902"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["low"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["varStart"], 8)        

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "CATCTGTAAAATACAAGGGAAAA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = brca1RefSpliceAcceptorBounds["exon7"])
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 11.68,
                                                                               "zScore": 1.5183252360035546},
                                                                 "altScores": {"maxEntScanScore": 10.94,
                                                                               "zScore": 1.214256756422072}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 6)    
    def test_getPriorProbRefSpliceAcceptorSNSLowProbBRCA1(self, getFastaSeq, getVarType, getVarLocation,
                                                          getVarSpliceRegionBounds, getRefAltScores,
                                                          getVarSeqIndexSNS):
        '''Tests function for BRCA1 variants that creates a resaonble splice acceptor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant that creates a reasonable splice acceptor site
        self.variant["Pos"] = "43104275"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["low"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["varStart"], 6)        

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "CATCTGTAAAATACAAGGGAAAA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = brca1RefSpliceAcceptorBounds["exon7"])
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 11.68,
                                                                               "zScore": 1.5183252360035546},
                                                                 "altScores": {"maxEntScanScore": 9.01,
                                                                               "zScore": 0.4212132894055031}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 14)
    def test_getPriorProbRefSpliceAcceptorSNSModerateProbBRCA1(self, getFastaSeq, getVarType, getVarLocation,
                                                               getVarSpliceRegionBounds, getRefAltScores,
                                                               getVarSeqIndexSNS):
        '''Tests function for BRCA1 variants that weakens a reasonably strong splice acceptor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant that weakens a reasonably strong splice acceptor site
        self.variant["Pos"] = "43104267"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["moderate"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["varStart"], 14)        
        
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "GAACTTTAACACATTAGAAAAAC")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = brca1RefSpliceAcceptorBounds["exon2"])
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 4.9,
                                                                               "zScore":  -1.2675994823240817},
                                                                 "altScores": {"maxEntScanScore": -3.17,
                                                                               "zScore": -4.583589523165384}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 19)
    def test_getPriorProbRefSpliceAcceptorSNSHighProbBRCA1(self, getFastaSeq, getVarType, getVarLocation,
                                                           getVarSpliceRegionBounds, getRefAltScores,
                                                           getVarSeqIndexSNS):
        '''Tests fucntion for BRCA1 variant that further weakens a weak splice acceptor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant that further weakens a weak splice acceptor site
        self.variant["Pos"] = "43124116"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["high"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class4"])
        self.assertEquals(priorProb["varStart"], 19)        
        
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "CATCTGTAAAATACAAGGGAAAA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = brca1RefSpliceAcceptorBounds["exon7"])
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 11.68,
                                                                               "zScore": 1.5183252360035546},
                                                                 "altScores": {"maxEntScanScore": 12.41,
                                                                               "zScore": 1.8182846820771794}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 20)
    def test_getPriorProbRefSpliceAcceptorSNSImprovedProbBRCA1(self, getFastaSeq, getVarType, getVarLocation,
                                                               getVarSpliceRegionBounds, getRefAltScores,
                                                               getVarSeqIndexSNS):
        '''Tests function for BRCA1 variants that makes a splice site stronger or equally strong'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
    
        # checks prior prob for BRCA1 variant that makes a splice acceptor site stronger or equally strong
        self.variant["Pos"] = "43104261"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["low"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["varStart"], 20)        

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCTCATCTTTCTCCAAACAGTTA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = brca2RefSpliceAcceptorBounds["exon23"])
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.35,
                                                                               "zScore": 0.9718237794584578},
                                                                 "altScores": {"maxEntScanScore": 10.09,
                                                                               "zScore": 0.8649889082541532}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 21)
    def test_getPriorProbRefSpliceAcceptorSNSLowProbBRCA2(self, getFastaSeq, getVarType, getVarLocation,
                                                          getVarSpliceRegionBounds, getRefAltScores,
                                                          getVarSeqIndex):
        '''Tests function for BRCA2 variant that creates a resaonble splice acceptor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant that creates a reasonable splice acceptor site
        self.variant["Pos"] = "32379751"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["low"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["varStart"], 21)   

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCTCATCTTTCTCCAAACAGTTA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = brca2RefSpliceAcceptorBounds["exon23"])
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.35,
                                                                               "zScore": 0.9718237794584578},
                                                                 "altScores": {"maxEntScanScore": 8.84,
                                                                               "zScore": 0.3513597197719193}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 16)
    def test_getPriorProbRefSpliceAcceptorSNSModerateProbBRCA2(self, getFastaSeq, getVarType, getVarLocation,
                                                               getVarSpliceRegionBounds, getRefAltScores,
                                                               getVarSeqIndexSNS):
        '''Tests function for BRCA2 variant that weakens a reasonably strong splice acceptor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant that weakens a reasonably strong splice acceptor site
        self.variant["Pos"] = "32379746"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["moderate"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["varStart"], 16)        

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "AAGTATTTATTCTTTGATAGATT")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = brca2RefSpliceAcceptorBounds["exon15"])
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 5.16,
                                                                               "zScore": -1.1607646111197771},
                                                                 "altScores": {"maxEntScanScore": -2.91,
                                                                               "zScore": -4.4767546519610795}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 19)
    def test_getPriorProbRefSpliceAcceptorSNSHighProbBRCA2(self, getFastaSeq, getVarType, getVarLocation,
                                                           getVarSpliceRegionBounds, getRefAltScores,
                                                           getVarSeqIndexSNS):
        '''Tests fucntion for BRCA2 variant that further weakens a weak splice acceptor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant that further weakens a weak splice acceptor site
        self.variant["Pos"] = "32356427"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["high"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class4"])
        self.assertEquals(priorProb["varStart"], 19)        
        
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCTCATCTTTCTCCAAACAGTTA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = brca2RefSpliceAcceptorBounds["exon23"])
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.35,
                                                                               "zScore": 0.9718237794584578},
                                                                 "altScores": {"maxEntScanScore": 10.42,
                                                                               "zScore": 1.000587014013463}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 1)
    def test_getPriorProbRefSpliceAcceptorSNSImprovedProbBRCA2(self, getFastaSeq, getVarType, getVarLocation,
                                                                getVarSpliceRegionBounds, getRefAltScores,
                                                               getVarSeqIndexSNS):
        '''Tests function for BRCA2 variant that makes a splice site stronger or equally strong'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant that makes a splice acceptor site stronger or equally strong
        self.variant["Pos"] = "32379731"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["low"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["varStart"], 1)        

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["afterGreyZone"])
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "missense_variant")
    def test_getPriorProbAfterGreyZoneMissenseSNS(self, getVarType, getVarLocation, getVarConsequences):
        '''
        Tests that:
        prior prob is set to N/A and ENIGMA class is class 2 for a BRCA2 missense variant after the grey zone
        '''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Chr"] = "13"
        self.variant["Hg38_Start"] = "32398528"
        self.variant["Hg38_End"] = "32398528"

        self.variant["Pos"] = "32398528"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbAfterGreyZoneSNS(self.variant, boundaries)
        self.assertEquals(priorProb["applicablePrior"], priorProbs["NA"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        # checks that all other priors are set to N/A
        self.assertEquals(priorProb["proteinPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that all flags are equal to zero or N/A
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["afterGreyZone"])
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    def test_getPriorProbAfterGreyZoneNonesenseSNS(self, getVarType, getVarLocation, getVarConsequences):
        '''
        Tests that:
        prior prob is set to N/A and ENIGMA class is class 2 for a BRCA2 nonsense variant after the grey zone
        '''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Chr"] = "13"
        self.variant["Hg38_Start"] = "32398492"
        self.variant["Hg38_End"] = "32398492"

        self.variant["Pos"] = "32398492"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbAfterGreyZoneSNS(self.variant, boundaries)
        self.assertEquals(priorProb["applicablePrior"], priorProbs["NA"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        # checks that all other priors are set to N/A
        self.assertEquals(priorProb["proteinPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that all flags are equal to zero or N/A
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon24")
    def test_varInIneligibleDeNovoExonDonorBRCA1True(self, varInExon, getVarExonNumberSNS):
        '''Tests that variant in last exon of BRCA1 is correctly identified as ineligible for de novo donor'''
        self.variant["Gene_Symbol"] = "BRCA1"
        ineligibleDeNovo = calcVarPriors.varInIneligibleDeNovoExon(self.variant, donor=True)
        self.assertTrue(ineligibleDeNovo)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon5")
    def test_varInIneligibleDeNovoExonDonorBRCA1False(self, varInExon, getVarExonNumberSNS):
        '''Tests that variant in other exon of BRCA1 is correctly identified as eligible for de novo donor'''
        self.variant["Gene_Symbol"] = "BRCA1"
        ineligibleDeNovo = calcVarPriors.varInIneligibleDeNovoExon(self.variant, donor=True)
        self.assertFalse(ineligibleDeNovo)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon27")
    def test_varInIneligibleDeNovoExonDonorBRCA2True(self, varInExon, getVarExonNumberSNS):
        '''Tests that variant in last exon of BRCA2 is correctly identified as ineligible for de novo donor'''
        self.variant["Gene_Symbol"] = "BRCA2"
        ineligibleDeNovo = calcVarPriors.varInIneligibleDeNovoExon(self.variant, donor=True)
        self.assertTrue(ineligibleDeNovo)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon19")
    def test_varInIneligibleDeNovoExonDonorBRCA2False(self, varInExon, getVarExonNumberSNS):
        '''Tests that variant in other exon of BRCA2 is correctly identified as eligible for de novo donor'''
        self.variant["Gene_Symbol"] = "BRCA2"
        ineligibleDeNovo = calcVarPriors.varInIneligibleDeNovoExon(self.variant, donor=True)
        self.assertFalse(ineligibleDeNovo)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon1")
    def test_varInIneligibleDeNovoExonAccBRCA1True(self, varInExon, getVarExonNumberSNS):
        '''Tests that variant in first exon of BRCA1 is correctly identified as ineligible for de novo acceptor'''
        self.variant["Gene_Symbol"] = "BRCA1"
        ineligibleDeNovo = calcVarPriors.varInIneligibleDeNovoExon(self.variant, donor=False)
        self.assertTrue(ineligibleDeNovo)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon16")
    def test_varInIneligibleDeNovoExonAccBRCA1False(self, varInExon, getVarExonNumberSNS):
        '''Tests that variant in other exon of BRCA1 is correctly identified as eligible for de novo acceptor'''
        self.variant["Gene_Symbol"] = "BRCA1"
        ineligibleDeNovo = calcVarPriors.varInIneligibleDeNovoExon(self.variant, donor=False)
        self.assertFalse(ineligibleDeNovo)
        
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon1")
    def test_varInIneligibleDeNovoExonAccBRCA2True(self, varInExon, getVarExonNumberSNS):
        '''Tests that variant in first exon of BRCA2 is correctly identified as ineligible for de novo acceptor'''
        self.variant["Gene_Symbol"] = "BRCA2"
        ineligibleDeNovo = calcVarPriors.varInIneligibleDeNovoExon(self.variant, donor=False)
        self.assertTrue(ineligibleDeNovo)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon2")
    def test_varInIneligibleDeNovoExonAccBRCA2False(self, varInExon, getVarExonNumberSNS):
        '''Tests that variant in other exon of BRCA2 is correctly identified as eligible for de novo acceptor'''
        self.variant["Gene_Symbol"] = "BRCA2"
        ineligibleDeNovo = calcVarPriors.varInIneligibleDeNovoExon(self.variant, donor=False)
        self.assertFalse(ineligibleDeNovo)
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = True)
    def test_getPriorProbDeNovoDonorSNSELastExonBRCA1(self, getVarType, varInExon, varInSpliceRegion,
                                                      varInIneligibleDeNovoExon):
        '''Tests that variant in last exon of BRCA1 is correctly assigned de novo prob'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43045765"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = True)
    def test_getPriorProbDeNovoDonorSNSELastExonBRCA2(self, getVarType, varInExon, varInSpliceRegion,
                                                      varInIneligibleDeNovoExon):
        '''Tests that variant in last exon of BRCA2 is correclty assigned de novo prob'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32398180"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AGGATACCG',
                                                                                       'varWindowPosition': 2,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': 1.49,
                                                                                       'altMaxEntScanScore': -3.56,
                                                                                       'refSeq': 'AAGATACCG',
                                                                                       'varStart': 1,
                                                                                       'altZScore': -4.936930962587172,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -2.7686143647984682})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 1.1729987773204027,
                                                                            'sequence': 'CAGGTGAGT',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon9',
                                                                            'maxEntScanScore': 10.67})
    def test_getPriorProbDeNovoDonorSNSExonRefGreaterAltBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                              getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''Tests BRCA1 variant in exon where ref zscore is greater than alt zscore'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43097273"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    # the below variant is in exonic portion of splice site, just making sure that function works if varInExon == False
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TGGTAAAAA',
                                                                                       'varWindowPosition': 1,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': -12.18,
                                                                                       'altMaxEntScanScore': -13.41,
                                                                                       'refSeq': 'AGGTAAAAA',
                                                                                       'varStart': 0,
                                                                                       'altZScore': -9.166221752333454,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -8.638097115644324})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.27990996080545155,
                                                                            'sequence': 'CAGGTAAAA',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon12',
                                                                            'maxEntScanScore': 8.59})
    def test_getPriorProbDeNovoDonorSNSSpliceSiteRefGreaterAltBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                                    getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''Tests BRCA1 variant in splice site where ref zscore is greater than alt zscore'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43090945"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAAGAGACT',
                                                                                       'varWindowPosition': 6,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -3.85,
                                                                                       'altMaxEntScanScore': -7.01,
                                                                                       'refSeq': 'AAAGAAACT',
                                                                                       'varStart': 5,
                                                                                       'altZScore': -6.418256163056683,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -5.061448153351276})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -1.3516946078276324,
                                                                            'sequence': 'ATGGTAAAA',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon12',
                                                                            'maxEntScanScore': 4.79})
    def test_getPriorProbDeNovoDonorSNSExonRefGreaterAltBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                              getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''Tests BRCA2 variant in exon where ref zscore is greater than alt zscore'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32344578"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    # the below variant is in exonic portion of splice site, just making sure that function works if varInExon == False
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TGGTAAGAC',
                                                                                       'varWindowPosition': 1,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': -14.69,
                                                                                       'altMaxEntScanScore': -17.11,
                                                                                       'refSeq': 'CGGTAAGAC',
                                                                                       'varStart': 0,
                                                                                       'altZScore': -10.75488935863409,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -9.71581487018881})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 1.1128870300549731,
                                                                            'sequence': 'TCGGTAAGA',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon13',
                                                                            'maxEntScanScore': 10.53})
    def test_getPriorProbDeNovoDonorSNSSpliceSiteRefGreaterAltBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                                    getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''Tests BRCA2 variant in splice site where ref zscore is greater than alt zscore'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32346895"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAGGCCATT',
                                                                                       'varWindowPosition': 7,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -5.67,
                                                                                       'altMaxEntScanScore': -3.44,
                                                                                       'refSeq': 'AAGGCCTTT',
                                                                                       'varStart': 6,
                                                                                       'altZScore': -4.885406607788233,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -5.842900867801858})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 1.1300618149879533,
                                                                            'sequence': 'AAGGTAAGA',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon14',
                                                                            'maxEntScanScore': 10.57})
    def test_getPriorProbDeNovoDonorSNSExonLowProbBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                        getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''Tests BRCA1 variant in exon with expected low (0.02) prior prob where alt zscore > ref zscore'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43076557"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    # the below variant is in exonic portion of splice site, just making sure that function works if varInExon == False
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'ATTGCACGT',
                                                                                       'varWindowPosition': 7,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -4.41,
                                                                                       'altMaxEntScanScore': -2.12,
                                                                                       'refSeq': 'ATTGCAGGT',
                                                                                       'varStart': 6,
                                                                                       'altZScore': -4.318638704999898,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -5.301895142412993})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 1.1729987773204027,
                                                                            'sequence': 'CAGGTGAGT',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon9',
                                                                            'maxEntScanScore': 10.67})
    def test_getPriorProbDeNovoDonorSNSSpliceSiteLowProbBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                              getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''Tests BRCA1 variant in splice site with expected low (0.02) prior prob where alt zscore > ref zscore'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43097244"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'CTGTTGTGC',
                                                                                       'varWindowPosition': 8,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -12.7,
                                                                                       'altMaxEntScanScore': -5.05,
                                                                                       'refSeq': 'CTGTTGTTC',
                                                                                       'varStart': 7,
                                                                                       'altZScore': -5.57669170134067,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -8.861369319773063})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.6534615330977633,
                                                                            'sequence': 'CAGGTATGA',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon5',
                                                                            'maxEntScanScore': 9.46})
    def test_getPriorProbDeNovoDonorSNSExonLowProbBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                        getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''Tests BRCA2 variant in exon with expected low (0.02) prior prob where alt zscore > ref zscore'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32326110"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    # the below variant is in exonic portion of splice site, just making sure that function works if varInExon == False
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAGCTTCTT',
                                                                                       'varWindowPosition': 9,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -6.24,
                                                                                       'altMaxEntScanScore': -4.4,
                                                                                       'refSeq': 'AAGCTTCTG',
                                                                                       'varStart': 8,
                                                                                       'altZScore': -5.297601446179749,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -6.087641553096821})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 1.164411384853913,
                                                                            'sequence': 'CTGGTAAGT',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon26',
                                                                            'maxEntScanScore': 10.65})
    def test_getPriorProbDeNovoDonorSNSSpliceSiteLowProbBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                              getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''Tests BRCA2 variant in splice site with expected low (0.02) prior prob where alt zscore > ref zscore'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32397044"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AGTGTGAGC',
                                                                                       'varWindowPosition': 8,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -2.47,
                                                                                       'altMaxEntScanScore': 3.73,
                                                                                       'refSeq': 'AGTGTGACC',
                                                                                       'varStart': 7,
                                                                                       'altZScore': -1.8068264085515982,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -4.468918073163471})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.9196706995589503,
                                                                            'sequence': 'CAAGTAAGT',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon3',
                                                                            'maxEntScanScore': 10.08})
    def test_getPriorProbDeNovoDonorSNSExonModProbBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                        getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''Tests BRCA1 variant in exon with expected moderate (0.3) prior prob where alt zscore > ref zscore'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43115740"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoMod"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    # the below variant is in exonic portion of splice site, just making sure that function works if varInExon == False
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TTTGTAAGT',
                                                                                       'varWindowPosition': 5,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -0.35,
                                                                                       'altMaxEntScanScore': 7.4,
                                                                                       'refSeq': 'TTTGCAAGT',
                                                                                       'varStart': 4,
                                                                                       'altZScore': -0.2310398909506982,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -3.558654471715541})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.9196706995589503,
                                                                            'sequence': 'CAAGTAAGT',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon3',
                                                                            'maxEntScanScore': 10.08})
    def test_getPriorProbDeNovoDonorSNSSpliceSiteModProbBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                              getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''Tests BRCA1 variant in splice site with expected moderate (0.3) prior prob where alt zscore > ref zscore'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43115728"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoMod"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TCAGTATGT',
                                                                                       'varWindowPosition': 4,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -3.5,
                                                                                       'altMaxEntScanScore': 5.0,
                                                                                       'refSeq': 'TCATTATGT',
                                                                                       'varStart': 3,
                                                                                       'altZScore': -1.2615269869294883,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -4.911168785187702})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.09528102277591848,
                                                                            'sequence': 'CAGGTACCT',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon10',
                                                                            'maxEntScanScore': 8.16})
    def test_getPriorProbDeNovoDonorSNSExonModProbBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                        getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''Tests BRCA2 variant in exon with expected moderate (0.3) prior prob where alt zscore > ref zscore'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32332406"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoMod"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    # the below variant is in exonic portion of splice site, just making sure that function works if varInExon == False
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAAGTAGGT',
                                                                                       'varWindowPosition': 5,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -0.91,
                                                                                       'altMaxEntScanScore': 6.84,
                                                                                       'refSeq': 'AAAGCAGGT',
                                                                                       'varStart': 4,
                                                                                       'altZScore': -0.47148688001241607,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -3.799101460777258})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.17686125120757246,
                                                                            'sequence': 'CAGGTATTG',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon2',
                                                                            'maxEntScanScore': 8.35})
    def test_getPriorProbDeNovoDonorSNSSpliceSiteModProbBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                              getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''Tests BRCA2 variant in splice site with expected moderate (0.3) prior prob where alt zscore > ref zscore'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32316525"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoMod"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'ACGGTGAGA',
                                                                                       'varWindowPosition': 3,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': 2.78,
                                                                                       'altMaxEntScanScore': 8.94,
                                                                                       'refSeq': 'ACTGTGAGA',
                                                                                       'varStart': 2,
                                                                                       'altZScore': 0.4301893289690249,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -2.2147275507098687})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.49030107623445457,
                                                                            'sequence': 'TGGGTAAGG',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon8',
                                                                            'maxEntScanScore': 9.08})
    def test_getPriorProbDeNovoDonorSNSExonHighProbBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                         getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''Tests BRCA1 variant in exon with expected high (0.64) prior prob where alt zscore > ref zscore'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43099839"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoHigh"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAGGTATGT',
                                                                                       'varWindowPosition': 5,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': 2.14,
                                                                                       'altMaxEntScanScore': 9.79,
                                                                                       'refSeq': 'AAGGGATGT',
                                                                                       'varStart': 4,
                                                                                       'altZScore': 0.7951535087948461,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -2.4895241096375464})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 1.2545790057520567,
                                                                            'sequence': 'CAGGTAAGT',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon22',
                                                                            'maxEntScanScore': 10.86})
    def test_getPriorProbDeNovoDonorSNSExonHighProbBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                         getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''Tests BRCA2 variant in exon with expected high (0.64) prior prob where alt zscore > ref zscore'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32379455"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoHigh"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AATGTATGG',
                                                                                       'varWindowPosition': 3,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': 3.77,
                                                                                       'altMaxEntScanScore': 3.37,
                                                                                       'refSeq': 'AAAGTATGG',
                                                                                       'varStart': 2,
                                                                                       'altZScore': -1.9613994729484163,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -1.7896516236186177})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -2.021511220213846,
                                                                            'sequence': 'TTGGTAAAA',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon7',
                                                                            'maxEntScanScore': 3.23})
    def test_getPriorProbDeNovoDonorSNSExonLowProbGreaterSubBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                                  getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''
        Tests BRCA1 variant in exon with expected low (0.02) prior prob that is promoted to moderate prior prob 
        because alt zscore > subsequent z score
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43104184"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoMod"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AATGTGACT',
                                                                                       'varWindowPosition': 7,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': 0.21,
                                                                                       'altMaxEntScanScore': 3.25,
                                                                                       'refSeq': 'AATGTGCCT',
                                                                                       'varStart': 6,
                                                                                       'altZScore': -2.012923827747356,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -3.318207482653823})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -2.07732927124603,
                                                                            'sequence': 'CAGGCAAGT',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon17',
                                                                            'maxEntScanScore': 3.1})
    def test_getPriorProbDeNovoDonorSNSExonLowProbGreaterSubBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                                  getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''
        Tests BRCA2 variant in exon with expected low (0.02) prior prob that is promoted to moderate prior prob 
        because alt zscore > subsequent z score
        '''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32362627"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoMod"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'GAGGTATCC',
                                                                                       'varWindowPosition': 5,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -0.17,
                                                                                       'altMaxEntScanScore': 7.59,
                                                                                       'refSeq': 'GAGGCATCC',
                                                                                       'varStart': 4,
                                                                                       'altZScore': -0.14945966251904425,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -3.4813679395171317})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -0.9867304280018111,
                                                                            'sequence': 'TAGGTATTG',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon11',
                                                                            'maxEntScanScore': 5.64})
    def test_getPriorProbDeNovoDonorSNSExonModProbGreaterSubBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                                  getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''
        Tests BRCA1 variant in exon with expected moderate (0.3) prior prob that is promoted to high prior prob 
        because alt zscore > subsequent z score
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Referenec_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43094762"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoHigh"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'CAGGTGGGG',
                                                                                       'varWindowPosition': 7,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': 6.34,
                                                                                       'altMaxEntScanScore': 6.92,
                                                                                       'refSeq': 'CAGGTGTGG',
                                                                                       'varStart': 6,
                                                                                       'altZScore': -0.43713731014645635,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -0.686171691674664})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -2.07732927124603,
                                                                            'sequence': 'CAGGCAAGT',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon17',
                                                                            'maxEntScanScore': 3.1})
    def test_getPriorProbDeNovoDonorSNSExonModProbGreaterSubBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                                  getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''
        Tests BRCA2 variant in exon with expected moderate (0.3) prior prob that is promoted to high prior prob 
        because alt zscore > subsequent z score
        '''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Referenec_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32362546"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoHigh"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAGGTATGG',
                                                                                       'varWindowPosition': 3,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': 3.77,
                                                                                       'altMaxEntScanScore': 9.26,
                                                                                       'refSeq': 'AAAGTATGG',
                                                                                       'varStart': 2,
                                                                                       'altZScore': 0.5675876084328637,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -1.7896516236186177})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -2.021511220213846,
                                                                            'sequence': 'TTGGTAAAA',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon7',
                                                                            'maxEntScanScore': 3.23})
    def test_getPriorProbDeNovoDonorSNSExonHighProbGreaterSubBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                                   getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''
        Tests BRCA1 variant in exon with expected high (0.64) prior prob and alt zscore > subsequent z score
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43104184"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoHigh"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAGGTAATG',
                                                                                       'varWindowPosition': 4,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': 0.81,
                                                                                       'altMaxEntScanScore': 8.99,
                                                                                       'refSeq': 'AAGATAATG',
                                                                                       'varStart': 3,
                                                                                       'altZScore': 0.45165781013525,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -3.0605857086591257})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.4044271515695557,
                                                                            'sequence': 'AAGGTAAAT',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon18',
                                                                            'maxEntScanScore': 8.88})
    def test_getPriorProbDeNovoDonorSNSExonHighProbGreaterSubBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                                   getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''
        Tests BRCA2 variant in exon with expected high (0.64) prior prob and alt zscore > subsequent z score
        '''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32363225"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, STD_EXONIC_PORTION, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoHigh"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 1)
            
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TTTTACATCTAAATGTCCAATTT',
                                                                                       'varWindowPosition': 20,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -3.96,
                                                                                       'altMaxEntScanScore': -4.11,
                                                                                       'refSeq': 'TTTTACATCTAAATGTCCATTTT',
                                                                                       'varStart': 19,
                                                                                       'altZScore': -4.969838672904024,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -4.908203170286155})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.2815061501383356,
                                                                            'sequence': 'CATCTAAATGTCCATTTTAGATC',
                                                                            'exonStart': 20,
                                                                            'intronStart': 0,
                                                                            'exonName': 'exon22',
                                                                            'maxEntScanScore': 8.67})
    def test_getPriorProbDeNovoAccSNSFalseAltLessRefBRCA1(self, getVarType, varInSpliceRegion,
                                                          getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43049200"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbDeNovoAcceptorSNS(self.variant, STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], 0)
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TCTTACAGTCAGAAACGAAGAAG',
                                                                                       'varWindowPosition': 16,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -11.02,
                                                                                       'altMaxEntScanScore': -11.86,
                                                                                       'refSeq': 'TCTTACAGTCAGAAATGAAGAAG',
                                                                                       'varStart': 15,
                                                                                       'altZScore': -8.154339641493873,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -7.8091808268338125})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.018528005635431572,
                                                                            'sequence': 'CATAAATTTTTATCTTACAGTCA',
                                                                            'exonStart': 20,
                                                                            'intronStart': 0,
                                                                            'exonName': 'exon8',
                                                                            'maxEntScanScore': 8.03})
    def test_getPriorProbDeNovoAccSNSFalseAltLessRefBRCA2(self, getVarType, varInSpliceRegion,
                                                          getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32329450"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbDeNovoAcceptorSNS(self.variant, STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'GGACTCTGTCTTTTCCCTATAGC',
                                                                                        'varWindowPosition': 23,
                                                                                        'inExonicPortion': True,
                                                                                        'refMaxEntScanScore': -0.03,
                                                                                        'altMaxEntScanScore': 0.26,
                                                                                        'refSeq': 'GGACTCTGTCTTTTCCCTATAGT',
                                                                                        'varStart': 22,
                                                                                        'altZScore': -3.174191029970134,
                                                                                        'varLength': 1,
                                                                                        'refZScore': -3.2933530016980126})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.8280076066834324,
                                                                            'sequence': 'ACTCTGTCTTTTCCCTATAGTGT',
                                                                            'exonStart': 20,
                                                                            'intronStart': 0,
                                                                            'exonName': 'exon10',
                                                                            'maxEntScanScore': 10.0})
    def test_getPriorProbDeNovoAccSNSFlagAltGreaterRefBRCA1(self, getVarType, varInSpliceRegion,
                                                             getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43095922"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbDeNovoAcceptorSNS(self.variant, STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], 0)
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAATCAATATATTTATTAAGTTG',
                                                                                       'varWindowPosition': 20,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -7.9,
                                                                                       'altMaxEntScanScore': 0.7,
                                                                                       'refSeq': 'AAATCAATATATTTATTAATTTG',
                                                                                       'varStart': 19,
                                                                                       'altZScore': -2.9933935556243876,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -6.527162372382157})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -1.5305776268269857,
                                                                            'sequence': 'ATATTTATTAATTTGTCCAGATT',
                                                                            'exonStart': 20,
                                                                            'intronStart': 0,
                                                                            'exonName': 'exon19',
                                                                            'maxEntScanScore': 4.26})
    def test_getPriorProbDeNovoAccSNSFlagAltGreaterRefBRCA2(self, getVarType, varInSpliceRegion,
                                                             getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32370393"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbDeNovoAcceptorSNS(self.variant, STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], 0)
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'ATTTATCGTTTTTGAAGCAGATG',
                                                                                       'varWindowPosition': 22,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': 3.17,
                                                                                       'altMaxEntScanScore': 4.73,
                                                                                       'refSeq': 'ATTTATCGTTTTTGAAGCAGAGG',
                                                                                       'varStart': 21,
                                                                                       'altZScore': -1.3374530519576655,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -1.9784622791834936})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -1.4031975880833913,
                                                                            'sequence': 'GCCATTTATCGTTTTTGAAGCAG',
                                                                            'exonStart': 20,
                                                                            'intronStart': 0,
                                                                            'exonName': 'exon13',
                                                                            'maxEntScanScore': 4.57})
    def test_getPriorProbDeNovoAccSNSFlagAltGreaterClosestBRCA1(self, getVarType, varInSpliceRegion,
                                                                getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43082571"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoAcceptorSNS(self.variant, STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], 1)
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'GTCCAGATTTCTCCTAACAGTAC',
                                                                                       'varWindowPosition': 13,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': 2.86,
                                                                                       'altMaxEntScanScore': 5.26,
                                                                                       'refSeq': 'GTCCAGATTTCTGCTAACAGTAC',
                                                                                       'varStart': 12,
                                                                                       'altZScore': -1.1196742760411986,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -2.1058423179270873})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -1.5305776268269857,
                                                                            'sequence': 'ATATTTATTAATTTGTCCAGATT',
                                                                            'exonStart': 20,
                                                                            'intronStart': 0,
                                                                            'exonName': 'exon19',
                                                                            'maxEntScanScore': 4.26})
    def test_getPriorProbDeNovoAccSNSFlagAltGreaterClosestBRCA2(self, getVarType, varInSpliceRegion,
                                                                getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32370408"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbDeNovoAcceptorSNS(self.variant, STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], 1)

    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getPriorProbRefSpliceDonorSNS', return_value = {'refMaxEntScanScore': 10.08,
                                                                               'altZScore': 0.159686466274593,
                                                                               'varLength': 1,
                                                                               'exonStart': 0,
                                                                               'intronStart': 3,
                                                                               'varStart': 2,
                                                                               'refZScore': 0.9196706995589503,
                                                                               'altMaxEntScanScore': 8.31,
                                                                               'enigmaClass': 'class_2',
                                                                               'priorProb': 0.04,
                                                                               'altSeq': 'CATGTAAGT',
                                                                               'spliceSite': 1,
                                                                               'refSeq': 'CAAGTAAGT'})
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'altZScore': -5.66256562600557,
                                                                            'closestZScore': 0.9196706995589503,
                                                                            'closestSeq': 'CAAGTAAGT',
                                                                            'refMaxEntScanScore': -0.35,
                                                                            'deNovoDonorAltGreaterClosestFlag': 0,
                                                                            'altMaxEntScanScore': -5.25,
                                                                            'enigmaClass': 'N/A',
                                                                            'deNovoDonorAltGreaterRefFlag': 0,
                                                                            'priorProb': 'N/A',
                                                                            'exonStart': 0,
                                                                            'altSeq': 'TTTGCATGT',
                                                                            'intronStart': 3,
                                                                            'closestMaxEntScanScore': 10.08,
                                                                            'closestIntronStart': 3,
                                                                            'varStart': 6,
                                                                            'refSeq': 'TTTGCAAGT',
                                                                            'varLength': 1,
                                                                            'refZScore': -3.558654471715541,
                                                                            'closestExonStart': 0})
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_3',
                                                                        'priorProb': 0.29})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "missense_variant")
    def test_getPriorProbSpliceDonorSNSNoDeNovoBRCA1(self, varInSpliceRegion, getVarType, varInExon,
                                                     getPriorProbRefSpliceDonorSNS, getPriorProbDeNovoDonorSNS,
                                                     getPriorProbProteinSNS, getVarConsequences):
        '''Tests that applicable prior for a variant in a reference splice site is assigned correctly (no de novo splicing)'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Chr"] = "17"
        self.variant["HGVS_cDNA"] = "c.134A>T"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43115726"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbSpliceDonorSNS(self.variant, boundaries, variantData)
        # checks that variant splice site flag is assigned correctly
        self.assertEquals(priorProb["spliceSite"], 1)
        # checks that variant is NOT flagged as a de novo splice donor or acceptor
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        # checks that prior prob and enigma class are appropriate based on applicable prior
        self.assertEquals(priorProb["applicablePrior"], priorProbs["proteinMod"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class3"])
        # checks that protein prior prob, ref prior prob, and de novo prior prob are set appropriately
        self.assertEquals(priorProb["proteinPrior"], priorProbs["proteinMod"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["low"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that scores and sequences are present for reference and de novo donor values and closest donor site
        self.assertNotEquals(priorProb["altRefDonorZ"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoDonorMES"], "N/A")
        self.assertNotEquals(priorProb["refRefDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorMES"], "N/A")
        # checks that scores and sequences are not present for ref splice acceptor site or de novo splice acceptor sites and closest acceptor site
        self.assertEquals(priorProb["altRefAccZ"], "N/A")
        self.assertEquals(priorProb["refDeNovoAccMES"], "N/A")
        self.assertEquals(priorProb["refRefAccSeq"], "N/A")
        self.assertEquals(priorProb["altDeNovoAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccMES"], "N/A")
        # checks that splice rescue, splice flag, and splice rescue flags are all equal to approriate value (either 0 or N/A)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getPriorProbRefSpliceDonorSNS', return_value = {'refMaxEntScanScore': 8.88,
                                                                               'altZScore': -0.9051501995701567,
                                                                               'varLength': 1,
                                                                               'exonStart': 0,
                                                                               'intronStart': 3,
                                                                               'varStart': 1,
                                                                               'refZScore': 0.4044271515695557,
                                                                               'altMaxEntScanScore': 5.83,
                                                                               'enigmaClass': 'class_3',
                                                                               'priorProb': 0.34,
                                                                               'altSeq': 'AGGGTAAAT',
                                                                               'spliceSite': 1,
                                                                               'refSeq': 'AAGGTAAAT'})
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'altZScore': -2.7385584911657537,
                                                                            'closestZScore': 0.4044271515695557,
                                                                            'closestSeq': 'AAGGTAAAT',
                                                                            'refMaxEntScanScore': -9.44,
                                                                            'deNovoDonorAltGreaterClosestFlag': 0,
                                                                            'altMaxEntScanScore': 1.56,
                                                                            'enigmaClass': 'class_2',
                                                                            'deNovoDonorAltGreaterRefFlag': 1,
                                                                            'priorProb': 0.02,
                                                                            'exonStart': 0,
                                                                            'altSeq': 'TTTGTGAGG',
                                                                            'intronStart': 3,
                                                                            'closestMaxEntScanScore': 8.88,
                                                                            'closestIntronStart': 3,
                                                                            'varStart': 7,
                                                                            'refSeq': 'TTTGTGAAG',
                                                                            'varLength': 1,
                                                                            'refZScore': -7.461624347735207,
                                                                            'closestExonStart': 0})
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_2',
                                                                        'priorProb': 0.02})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "missense_variant")
    def test_getPriorProbSpliceDonorSNSWithDeNovoBRCA2(self, varInSpliceRegion, getVarType, varInExon,
                                                       getPriorProbRefSpliceDonorSNS, getPriorProbDeNovoDonorSNS,
                                                       getPriorProbProteinSNS, getVarConsequences):
        '''Tests that applicable prior for a variant in a reference splice site is assigned correctly (with de novo splicing)'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Chr"] = "13"
        self.variant["HGVS_cDNA"] = "c.515A>G"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32326281"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbSpliceDonorSNS(self.variant, boundaries, variantData)
        # checks that variant splice site flag and de novo splice flag are assigned correctly
        self.assertEquals(priorProb["spliceSite"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        # checks that variant is not flagged as a de novo splice acceptor
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        # checks that prior prob and enigma class are appropriate based on applicable prior
        self.assertEquals(priorProb["applicablePrior"], priorProbs["moderate"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class3"])
        # checks that protein prior prob, ref prior prob, and de novo prior prob are set appropriately
        self.assertEquals(priorProb["proteinPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["moderate"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that scores and sequences are present for reference donor score and de novo splice donor score and closest donor
        self.assertNotEquals(priorProb["altDeNovoDonorZ"], "N/A")
        self.assertNotEquals(priorProb["refRefDonorMES"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["altRefDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorSeq"], "N/A")
        # checks that scores and sequences are not present for ref splice acceptor site or de novo splice acceptor sites and closest acceptor
        self.assertEquals(priorProb["altDeNovoAccZ"], "N/A")
        self.assertEquals(priorProb["refRefAccMES"], "N/A")
        self.assertEquals(priorProb["refDeNovoAccSeq"], "N/A")
        self.assertEquals(priorProb["altRefAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccSeq"], "N/A")
        # checks that splice rescue, splice flag, and splice rescue flags are all equal to approriate value (either 0 or N/A)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")

    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getPriorProbRefSpliceDonorSNS', return_value = {'refMaxEntScanScore': 9.66,
                                                                               'altZScore': -0.5358923235110902,
                                                                               'varLength': 1,
                                                                               'exonStart': 0,
                                                                               'intronStart': 3,
                                                                               'varStart': 2,
                                                                               'refZScore': 0.7393354577626622,
                                                                               'altMaxEntScanScore': 6.69,
                                                                               'enigmaClass': 'class_3',
                                                                               'priorProb': 0.34,
                                                                               'altSeq': 'TATGTAAGT',
                                                                               'spliceSite': 1,
                                                                               'refSeq': 'TAGGTAAGT'})
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'altZScore': -3.6960527511793795,
                                                                            'closestZScore': 0.7393354577626622,
                                                                            'closestSeq': 'TAGGTAAGT',
                                                                            'refMaxEntScanScore': -1.72,
                                                                            'deNovoDonorAltGreaterClosestFlag': 0,
                                                                            'altMaxEntScanScore': -0.67,
                                                                            'enigmaClass': 'class_2',
                                                                            'deNovoDonorAltGreaterRefFlag': 1,
                                                                            'priorProb': 0.02,
                                                                            'exonStart': 0,
                                                                            'altSeq': 'GACTTATGT',
                                                                            'intronStart': 3,
                                                                            'closestMaxEntScanScore': 9.66,
                                                                            'closestIntronStart': 3,
                                                                            'varStart': 6,
                                                                            'refSeq': 'GACTTAGGT',
                                                                            'varLength': 1,
                                                                            'refZScore': -4.1468908556701,
                                                                            'closestExonStart': 0})
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_5',
                                                                        'priorProb': 0.99})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.getPriorProbSpliceRescueNonsenseSNS', return_value = {'CIDomainInRegionFlag': 0,
                                                                                     'inExonicPortionFlag': 0,
                                                                                     'frameshiftFlag': 1,
                                                                                     'isDivisibleFlag': 0,
                                                                                     'spliceFlag': 0,
                                                                                     'enigmaClass': 'class_5',
                                                                                     'priorProb': 0.99,
                                                                                     'spliceRescue': 0})
    def test_getPriorProbSpliceDonorSNSNonsenseBRCA2(self, varInSpliceRegion, getVarType, varInExon,
                                                     getPriorProbRefSpliceDonorSNS, getPriorProbDeNovoDonorSNS,
                                                     getPriorProbProteinSNS, getVarConsequences,
                                                     getPriorProbSpliceRescueNonsenseSNS):
        '''Tests function for nonsense variant in reference splice donor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Chr"] = "13"
        self.variant["HGVS_cDNA"] = "c.316G>T"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32319325"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbSpliceDonorSNS(self.variant, boundaries, variantData)
        # checks that variant splice site flag and de novo splice flag are assigned correctly
        self.assertEquals(priorProb["spliceSite"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        # checks that variant is not flagged as a de novo splice acceptor
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        # checks that prior prob and enigma class are appropriate based on applicable prior
        self.assertEquals(priorProb["applicablePrior"], priorProbs["pathogenic"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class5"])
        # checks that protein prior prob, ref prior prob, and de novo prior prob are set appropriately
        self.assertEquals(priorProb["proteinPrior"], priorProbs["pathogenic"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["moderate"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that scores and sequences are present for reference donor score and de novo splice donor score and closest donor 
        self.assertNotEquals(priorProb["altDeNovoDonorZ"], "N/A")
        self.assertNotEquals(priorProb["refRefDonorMES"], "N/A")
        self.assertNotEquals(priorProb["refRefDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorMES"], "N/A")
        # checks that scores and sequences are not present for ref splice acceptor site or de novo splice acceptor sites and closest acceptor
        self.assertEquals(priorProb["altDeNovoAccZ"], "N/A")
        self.assertEquals(priorProb["refRefAccMES"], "N/A")
        self.assertEquals(priorProb["altRefAccSeq"], "N/A")
        self.assertEquals(priorProb["refDeNovoAccSeq"], "N/A")
        # checks that splice rescue and splice flag are equal to zero
        self.assertEquals(priorProb["spliceRescue"], 0)
        self.assertEquals(priorProb["spliceFlag"], 0)
        # checks that frameshift is equal to 1, because nonsense variant causes frameshift mutation
        self.assertEquals(priorProb["frameshiftFlag"], 1)
        # checks that other nonsense rescue flags are equal to zero
        self.assertEquals(priorProb["inExonicPortionFlag"], 0)
        self.assertEquals(priorProb["CIDomainInRegionFlag"], 0)
        self.assertEquals(priorProb["isDivisibleFlag"], 0)

    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getPriorProbRefSpliceAcceptorSNS', return_value =  {'refMaxEntScanScore': 10.37,
                                                                                   'altZScore': 1.4936710349564073,
                                                                                   'varLength': 1,
                                                                                   'exonStart': 20,
                                                                                   'intronStart': 0,
                                                                                   'varStart': 20,
                                                                                   'refZScore': 0.9800418464741734,
                                                                                   'altMaxEntScanScore': 11.62,
                                                                                   'enigmaClass': 'class_2',
                                                                                   'priorProb': 0.04,
                                                                                   'altSeq': 'ATATTTTCTCCCCATTGCAGGAC',
                                                                                   'spliceSite': 1,
                                                                                   'refSeq': 'ATATTTTCTCCCCATTGCAGCAC'})
    @mock.patch('calcVarPriors.getPriorProbDeNovoAcceptorSNS', return_value = {'altZScore': -5.705355670810582,
                                                                               'closestZScore': 0.9800418464741734,
                                                                               'deNovoAccAltGreaterClosestFlag': 0,
                                                                               'closestSeq': 'ATATTTTCTCCCCATTGCAGCAC',
                                                                               'refMaxEntScanScore': -13.96,
                                                                               'altMaxEntScanScore': -5.9,
                                                                               'enigmaClass': 'N/A',
                                                                               'priorProb': 'N/A',
                                                                               'exonStart': 20,
                                                                               'altSeq': 'TATTTTCTCCCCATTGCAGGACA',
                                                                               'intronStart': 0,
                                                                               'closestMaxEntScanScore': 10.37,
                                                                               'closestIntronStart': 0,
                                                                               'varStart': 19,
                                                                               'refSeq': 'TATTTTCTCCCCATTGCAGCACA',
                                                                               'deNovoAccAltGreaterRefFlag': 1,
                                                                               'varLength': 1,
                                                                               'refZScore': -9.017236678144027,
                                                                               'closestExonStart': 20})
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'altZScore': -5.928774792466758,
                                                                            'closestZScore': -0.9867304280018111,
                                                                            'closestSeq': 'TAGGTATTG',
                                                                            'refMaxEntScanScore': -14.15,
                                                                            'deNovoDonorAltGreaterClosestFlag': 0,
                                                                            'altMaxEntScanScore': -5.87,
                                                                            'enigmaClass': 'class_2',
                                                                            'deNovoDonorAltGreaterRefFlag': 1,
                                                                            'priorProb': 0.02,
                                                                            'exonStart': 0,
                                                                            'altSeq': 'CAGGACAAC',
                                                                            'intronStart': 3,
                                                                            'closestMaxEntScanScore': 5.64,
                                                                            'closestIntronStart': 3,
                                                                            'varStart': 3,
                                                                            'refSeq': 'CAGCACAAC',
                                                                            'varLength': 1,
                                                                            'refZScore': -9.483955273593583,
                                                                            'closestExonStart': 0})
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_2',
                                                                        'priorProb': 0.02})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "splice_region_variant")
    def test_getPriorProbSpliceAcceptorSNSDeNovoAccBRCA2(self, varInSpliceRegion, getVarType, varInExon,
                                                         getPriorProbRefSpliceAcceptorSNS, getPriorProbDeNovoAcceptorSNS,
                                                         getPriorProbDeNovoDonorSNS, getPriorProbProteinSNS, getVarConsequences):
        '''Tests that applicable prior for a variant in a reference splice site is assigned correctly (no de novo splicing)'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Chr"] = "13"
        self.variant["HGVS_cDNA"] = "c.7008C>G"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32354861"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbSpliceAcceptorSNS(self.variant, boundaries, variantData)
        # checks that variant splice site flag is assigned correctly
        self.assertEquals(priorProb["spliceSite"], 1)
        # checks that variant is correctly flagged as a potential de novo splice donor and acceptor
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], 0)
        # checks that prior prob and enigma class are appropriate based on applicable prior
        self.assertEquals(priorProb["applicablePrior"], priorProbs["low"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        # checks that protein prior prob, ref prior prob, and de novo prior probs are set appropriately
        self.assertEquals(priorProb["proteinPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["low"])
        self.assertEquals(priorProb["deNovoAccPrior"], "N/A")
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        # checks that scores and sequences are present for reference acceptor value and de novo donor/acceptor value and closest splice sites
        self.assertNotEquals(priorProb["refRefAccZ"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoAccZ"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoDonorZ"], "N/A")
        self.assertNotEquals(priorProb["refRefAccSeq"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoAccSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorMES"], "N/A")
        self.assertNotEquals(priorProb["closestAccZ"], "N/A")
        # checks that scores and sequences are not present for ref splice donor site
        self.assertEquals(priorProb["refRefDonorZ"], "N/A")
        self.assertEquals(priorProb["altRefDonorSeq"], "N/A")
        # checks that splice rescue, splice flag, and splice rescue flags are all equal to approriate value (either 0 or N/A)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getPriorProbRefSpliceAcceptorSNS', return_value = {'refMaxEntScanScore': 4.57,
                                                                                  'altZScore': -2.286639792272834,
                                                                                  'varLength': 1,
                                                                                  'exonStart': 20,
                                                                                  'intronStart': 0,
                                                                                  'varStart': 4,
                                                                                  'refZScore': -1.4031975880833913,
                                                                                  'altMaxEntScanScore': 2.42,
                                                                                  'enigmaClass': 'class_4',
                                                                                  'priorProb': 0.97,
                                                                                  'altSeq': 'GCCAGTTATCGTTTTTGAAGCAG',
                                                                                  'spliceSite': 1,
                                                                                  'refSeq': 'GCCATTTATCGTTTTTGAAGCAG'})
    @mock.patch('calcVarPriors.getPriorProbDeNovoAcceptorSNS', return_value = {'altZScore': -0.5238644174018071,
                                                                               'closestZScore': -1.4031975880833913,
                                                                               'deNovoAccAltGreaterClosestFlag': 1,
                                                                               'closestSeq': 'GCCATTTATCGTTTTTGAAGCAG',
                                                                               'refMaxEntScanScore': -1.89,
                                                                               'altMaxEntScanScore': 6.71,
                                                                               'enigmaClass': 'N/A',
                                                                               'priorProb': 'N/A',
                                                                               'exonStart': 20,
                                                                               'altSeq': 'TTTCATTTTCTTGGTGCCAGTTA',
                                                                               'intronStart': 0,
                                                                               'closestMaxEntScanScore': 4.57,
                                                                               'closestIntronStart': 0,
                                                                               'varStart': 19,
                                                                               'refSeq': 'TTTCATTTTCTTGGTGCCATTTA',
                                                                               'deNovoAccAltGreaterRefFlag': 1,
                                                                               'varLength': 1,
                                                                               'refZScore': -4.057633234159576,
                                                                               'closestExonStart': 20})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "intron_variant")
    def test_getPriorProbSpliceAcceptorSNSWithDeNovoBRCA1(self, varInSpliceRegion, getVarType, varInExon,
                                                          getPriorProbRefSpliceAcceptorSNS, getPriorProbDeNovoAcceptorSNS,
                                                          getVarConsequences):
        '''Tests that applicable prior for a variant in a reference splice site is assigned correctly (with de novo splicing)'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Chr"] = 17
        self.variant["HGVS_cDNA"] = "c.4186-16t>G"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43082591"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbSpliceAcceptorSNS(self.variant, boundaries, variantData)
        # checks that variant splice site flag is assigned correctly
        self.assertEquals(priorProb["spliceSite"], 1)
        # checks that variant is flagged as a de novo splice acceptor
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], 1)
        # checks that variant is not flagged as a de novo donor
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], "N/A")
        # checks that prior prob and enigma class are appropriate based on applicable prior
        self.assertEquals(priorProb["applicablePrior"], priorProbs["high"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class4"])
        # checks that protein prior prob, ref prior prob, and de novo prior prob are set appropriately
        self.assertEquals(priorProb["proteinPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["high"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that scores and sequences are present for reference acceptor score and de novo splice acceptor score and closest acceptor
        self.assertNotEquals(priorProb["altDeNovoAccMES"], "N/A")
        self.assertNotEquals(priorProb["refRefAccZ"], "N/A")
        self.assertNotEquals(priorProb["refRefAccSeq"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoAccSeq"], "N/A")
        self.assertNotEquals(priorProb["altRefAccSeq"], "N/A")
        self.assertNotEquals(priorProb["closestAccSeq"], "N/A")
        # checks that scores and sequences are not present for ref splice donor site or de novo splice donor sites and closest donor
        self.assertEquals(priorProb["altDeNovoDonorMES"], "N/A")
        self.assertEquals(priorProb["refRefDonorZ"], "N/A")
        self.assertEquals(priorProb["refDeNovoDonorSeq"], "N/A")
        self.assertEquals(priorProb["altRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["closestDonorSeq"], "N/A")
        # checks that splice rescue, splice flag, and splice rescue flags are all equal to approriate value (either 0 or N/A)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")

    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getPriorProbRefSpliceAcceptorSNS', return_value = {'refMaxEntScanScore': 3.71,
                                                                                  'altZScore': -2.0400977818013613,
                                                                                  'varLength': 1,
                                                                                  'exonStart': 20,
                                                                                  'intronStart': 0,
                                                                                  'varStart': 20,
                                                                                  'refZScore': -1.7565744697591685,
                                                                                  'altMaxEntScanScore': 3.02,
                                                                                  'enigmaClass': 'class_3',
                                                                                  'priorProb': 0.34,
                                                                                  'altSeq': 'TTCTTTACCATACTGTTTAGTAG',
                                                                                  'spliceSite': 1,
                                                                                  'refSeq': 'TTCTTTACCATACTGTTTAGCAG'})
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'altZScore': -4.061016931005201,
                                                                            'closestZScore': 0.49030107623445457,
                                                                            'closestSeq': 'TGGGTAAGG',
                                                                            'refMaxEntScanScore': 0.48,
                                                                            'deNovoDonorAltGreaterClosestFlag': 0,
                                                                            'altMaxEntScanScore': -1.52,
                                                                            'enigmaClass': 'N/A',
                                                                            'deNovoDonorAltGreaterRefFlag': 0,
                                                                            'priorProb': 'N/A',
                                                                            'exonStart': 0,
                                                                            'altSeq': 'TAGGAAACC',
                                                                            'intronStart': 3,
                                                                            'closestMaxEntScanScore': 9.08,
                                                                            'closestIntronStart': 3,
                                                                            'varStart': 0,
                                                                            'refSeq': 'CAGGAAACC',
                                                                            'varLength': 1,
                                                                            'refZScore': -3.2022776843562095,
                                                                            'closestExonStart': 0})
    @mock.patch('calcVarPriors.getPriorProbDeNovoAcceptorSNS', return_value = {'altZScore': -1.8716274079791886,
                                                                               'closestZScore': -1.7565744697591685,
                                                                               'deNovoAccAltGreaterClosestFlag': 0,
                                                                               'closestSeq': 'TTCTTTACCATACTGTTTAGCAG',
                                                                               'refMaxEntScanScore': 4.78,
                                                                               'altMaxEntScanScore': 3.43,
                                                                               'enigmaClass': 'N/A',
                                                                               'priorProb': 'N/A',
                                                                               'exonStart': 20,
                                                                               'altSeq': 'TTTACCATACTGTTTAGTAGGAA',
                                                                               'intronStart': 0,
                                                                               'closestMaxEntScanScore': 3.71,
                                                                               'closestIntronStart': 0,
                                                                               'varStart': 17,
                                                                               'refSeq': 'TTTACCATACTGTTTAGCAGGAA',
                                                                               'deNovoAccAltGreaterRefFlag': 0,
                                                                               'varLength': 1,
                                                                               'refZScore': -1.3169078844183761,
                                                                               'closestExonStart': 20})
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_5',
                                                                        'priorProb': 0.99})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.getPriorProbSpliceRescueNonsenseSNS', return_value = {'CIDomainInRegionFlag': 0,
                                                                                     'inExonicPortionFlag': 1,
                                                                                     'frameshiftFlag': 0,
                                                                                     'isDivisibleFlag': 0,
                                                                                     'spliceFlag': 0,
                                                                                     'enigmaClass':
                                                                                     'class_4',
                                                                                     'priorProb': 0.97,
                                                                                     'spliceRescue': 0})
    def test_getPriorProbSpliceAcceptorSNSNonsenseBRCA1(self, varInSpliceRegion, getVarType, varInExon,
                                                        getPriorProbRefSpliceAcceptorSNS, getPriorProbDeNovoDonorSNS,
                                                        getPriorProbDeNovoAcceptorSNS, getPriorProbProteinSNS,
                                                        getVarConsequences, getPriorProbSpliceRescueNonsenseSNS):
        '''Tests function with nonsense variant in reference acceptor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Chr"] = "17"
        self.variant["HGVS_cDNA"] = "c.442C>T"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43099880"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbSpliceAcceptorSNS(self.variant, boundaries, variantData)
        # checks that variant splice site flag is assigned correctly
        self.assertEquals(priorProb["spliceSite"], 1)
        # checks that variant is not flagged as a de novo splice donor or acceptor
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], 0)
        # checks that prior prob and enigma class are appropriate based on applicable prior
        self.assertEquals(priorProb["applicablePrior"], priorProbs["high"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class4"])
        # checks that protein prior prob, ref prior prob, and de novo prior prob are set appropriately
        self.assertEquals(priorProb["proteinPrior"], priorProbs["pathogenic"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["moderate"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that a score and sequence are NOT present for reference donor score and are present for de novo splice donor score
        self.assertNotEquals(priorProb["altDeNovoDonorZ"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorMES"], "N/A")
        self.assertEquals(priorProb["refRefDonorMES"], "N/A")
        self.assertEquals(priorProb["altRefDonorSeq"], "N/A")
        # checks that scores and sequences are present for ref splice acceptor site or de novo splice acceptor sites
        self.assertNotEquals(priorProb["altDeNovoAccZ"], "N/A")
        self.assertNotEquals(priorProb["refRefAccMES"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoAccSeq"], "N/A")
        self.assertNotEquals(priorProb["refRefAccSeq"], "N/A")
        self.assertNotEquals(priorProb["closestAccZ"], "N/A")
        # checks that inExonicPortion flag is equal to 1
        self.assertEquals(priorProb["inExonicPortionFlag"], 1)
        # checks that splice rescue, splice flag, and splice rescue flags are equal to zero
        self.assertEquals(priorProb["spliceRescue"], 0)
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], 0)
        self.assertEquals(priorProb["CIDomainInRegionFlag"], 0)
        self.assertEquals(priorProb["isDivisibleFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_getPriorProbProteinSNS(self, getVarType):
        '''Tests that function parses data from variantData correctly and returns correct prior prob/class'''
        # checks for BRCA1 variant
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["HGVS_cDNA"] = "c.592A>T"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbProteinSNS(self.variant, variantData)
        self.assertEquals(priorProb["priorProb"], priorProbs["proteinMod"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])

        # checks for BRCA2 variant
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["HGVS_cDNA"] = "c.620C>T"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbProteinSNS(self.variant, variantData)
        self.assertEquals(priorProb["priorProb"], priorProbs["proteinHigh"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inGreyZone"])
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {"priorProb": 0.02,
                                                                        "enigmaClass": "class_2"})
    def test_getPriorProbInGreyZoneSNSLowProb(self, getVarType, getVarLocation, getPriorProbProteinSNS):
        '''Tests that prior prob is correct for variant in the grey zone with a low protein prior'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.9930A>G"
        self.variant["Pos"] = "32398443"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbInGreyZoneSNS(self.variant, boundaries, variantData)
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["proteinPrior"], priorProbs["deNovoLow"])
        # checks that all other priors are set to N/A
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that all flags are equal to zero or N/A
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inGreyZone"])
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {"priorProb": 0.99,
                                                                        "enigmaClass": "class_5"})
    def test_getPriorProbInGreyZoneSNSHighProb(self, getVarType, getVarLocation, getPriorProbProteinSNS):
        '''Tests that prior prob is correct for variant in the grey zone with a high protein prior'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.9943A>T"
        self.variant["Pos"] = "32398456"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbInGreyZoneSNS(self.variant, boundaries, variantData)
        self.assertEquals(priorProb["applicablePrior"], priorProbs["capped"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["proteinPrior"], priorProbs["capped"])
        # checks that all other priors are set to N/A
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that all flags are equal to zero or N/A
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inExon"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_2',
                                                                        'priorProb': 0.02})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "missense_variant")
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'altZScore': -1.8454696746508026,
                                                                            'closestZScore': -0.870800629704197,
                                                                            'closestSeq': 'TTTGTGAGT',
                                                                            'refMaxEntScanScore': -4.51,
                                                                            'deNovoDonorAltGreaterClosestFlag': 0,
                                                                            'altMaxEntScanScore': 3.64,
                                                                            'enigmaClass': 'class_3',
                                                                            'deNovoDonorAltGreaterRefFlag': 1,
                                                                            'priorProb': 0.3,
                                                                            'exonStart': 0,
                                                                            'altSeq': 'AGGGTCAGC',
                                                                            'intronStart': 3,
                                                                            'closestMaxEntScanScore': 5.91,
                                                                            'closestIntronStart': 3,
                                                                            'varStart': 2,
                                                                            'refSeq': 'AGAGTCAGC',
                                                                            'varLength': 1,
                                                                            'refZScore': -5.344832104745444,
                                                                            'closestExonStart': 0})
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    def test_getPriorProbInExonSNSDeNovoDonorBRCA1(self, getVarLocation, getVarType, getPriorProbProteinSNS,
                                                   getVarConsequences, getPriorProbDeNovoDonorSNS, varInSpliceRegion):
        '''Tests that function works correctly for missense variant in exon with de novo donor score, no de novo acceptor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.4757A>G"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43071157"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbInExonSNS(self.variant, boundaries, variantData)
        # checks that applicable prior and enigma class are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoMod"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class3"])
        # checks that protein prior, ref donor prior, and ref acceptor prior are correct
        self.assertEquals(priorProb["proteinPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor prior and de novo acceptor prior are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoMod"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that scores and sequences are present for de novo donor and closest donor
        self.assertNotEquals(priorProb["refDeNovoDonorMES"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorMES"], "N/A")
        # checks that flags are correct for de novo donor and acceptor
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        # checks that scores and sequences are NOT present for ref splice acceptor, ref splice donor, de novo acceptor, and closest acceptor
        self.assertEquals(priorProb["refRefAccZ"], "N/A")
        self.assertEquals(priorProb["altRefDonorMES"], "N/A")
        self.assertEquals(priorProb["altDeNovoAccZ"], "N/A")
        self.assertEquals(priorProb["refRefAccSeq"], "N/A")
        self.assertEquals(priorProb["altRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["altDeNovoAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccZ"], "N/A")
        # checks that flags (splice site, splice rescue, splice flag, splice rescue flags) are all equal to correct values
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inCI"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_3',
                                                                        'priorProb': 0.81})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "missense_variant")
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'altZScore': -3.4384309771846815,
                                                                            'closestZScore': 0.4044271515695557,
                                                                            'closestSeq': 'AAGGTAAAT',
                                                                            'refMaxEntScanScore': 0.02,
                                                                            'deNovoDonorAltGreaterClosestFlag': 0,
                                                                            'altMaxEntScanScore': -0.07,
                                                                            'enigmaClass': 'N/A',
                                                                            'deNovoDonorAltGreaterRefFlag': 0,
                                                                            'priorProb': 'N/A', 'exonStart': 0,
                                                                            'altSeq': 'ATGCTACGG',
                                                                            'intronStart': 3,
                                                                            'closestMaxEntScanScore': 8.88,
                                                                            'closestIntronStart': 3,
                                                                            'varStart': 3,
                                                                            'refSeq': 'ATGATACGG',
                                                                            'varLength': 1,
                                                                            'refZScore': -3.3997877110854775,
                                                                            'closestExonStart': 0})
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getPriorProbDeNovoAcceptorSNS', return_value = {'altZScore': -4.501408853008226,
                                                                               'closestZScore': 1.444362632862113,
                                                                               'deNovoAccAltGreaterClosestFlag': 0,
                                                                               'closestSeq': 'ATTTTTGTTTTCACTTTTAGATA',
                                                                               'refMaxEntScanScore': -3.14,
                                                                               'altMaxEntScanScore': -2.97,
                                                                               'enigmaClass': 'N/A',
                                                                               'priorProb': 'N/A',
                                                                               'exonStart': 20,
                                                                               'altSeq': 'TATGCTACGGAAATTGATAGAAG',
                                                                               'intronStart': 0,
                                                                               'closestMaxEntScanScore': 11.5,
                                                                               'closestIntronStart': 0,
                                                                               'varStart': 4,
                                                                               'refSeq': 'TATGATACGGAAATTGATAGAAG',
                                                                               'deNovoAccAltGreaterRefFlag': 1,
                                                                               'varLength': 1,
                                                                               'refZScore': -4.57126242264181,
                                                                               'closestExonStart': 20})
    def test_getPriorProbInExonSNSEnigmaCIDeNovoAcceptorBRCA2(self, getVarLocation, getVarType, getPriorProbProteinSNS,
                                                              getVarConsequences, getPriorProbDeNovoDonorSNS,
                                                              varInSpliceRegion, getPriorProbDeNovoAcceptorSNS):
        '''Tests that function works correctly for missense variant in ENIGMA CI domain  with de novo acceptor score, no de novo donor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.7982A>C"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32363184"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbInExonSNS(self.variant, boundaries, variantData)
        # checks that applicable prior and enigma class are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["proteinHigh"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class3"])
        # checks that protein prior, ref donor prior, and ref acceptor prior are correct
        self.assertEquals(priorProb["proteinPrior"], priorProbs["proteinHigh"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor prior and de novo acceptor prior are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that scores and sequences are present for de novo acceptor and de novo donor and closest donor/acceptor
        self.assertNotEquals(priorProb["altDeNovoAccZ"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoDonorMES"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoAccSeq"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestAccSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorMES"], "N/A")
        # checks that flags are correct for de novo donor and acceptor
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], 0)
        # checks that scores and sequences are NOT present for ref splice acceptor and ref splice donor
        self.assertEquals(priorProb["altRefAccMES"], "N/A")
        self.assertEquals(priorProb["refRefDonorZ"], "N/A")
        self.assertEquals(priorProb["altRefAccSeq"], "N/A")
        self.assertEquals(priorProb["refRefDonorSeq"], "N/A")
        # checks that flags (splice site, splice rescue, splice flag, splice rescue flags) are all equal to correct values
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        
    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inCI"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_5',
                                                                        'priorProb': 0.99})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.getPriorProbSpliceRescueNonsenseSNS', return_value = {'CIDomainInRegionFlag': 0,
                                                                                     'inExonicPortionFlag': 0,
                                                                                     'frameshiftFlag': 1,
                                                                                     'isDivisibleFlag': 0,
                                                                                     'spliceFlag': 0,
                                                                                     'enigmaClass': 'class_5',
                                                                                     'priorProb': 0.99,
                                                                                     'spliceRescue': 0})
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'altZScore': -3.3740255336860074,
                                                                            'closestZScore': 1.164411384853913,
                                                                            'closestSeq': 'CTGGTAAGT',
                                                                            'refMaxEntScanScore': -1.14,
                                                                            'deNovoDonorAltGreaterClosestFlag': 0,
                                                                            'altMaxEntScanScore': 0.08,
                                                                            'enigmaClass': 'class_2',
                                                                            'deNovoDonorAltGreaterRefFlag': 1,
                                                                            'priorProb': 0.02,
                                                                            'exonStart': 0,
                                                                            'altSeq': 'ATGCTATGT',
                                                                            'intronStart': 3,
                                                                            'closestMaxEntScanScore': 10.65,
                                                                            'closestIntronStart': 3,
                                                                            'varStart': 8,
                                                                            'refSeq': 'ATGCTATGC',
                                                                            'varLength': 1,
                                                                            'refZScore': -3.897856474141892,
                                                                            'closestExonStart': 0})
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    def test_getPriorProbInExonSNSPriorsCIWithoutSpliceRescueBRCA1(self, getVarLocation, getVarType, getPriorProbProteinSNS,
                                                                   getVarConsequences, getPriorProbSpliceRescueNonsenseSNS,
                                                                   getPriorProbDeNovoDonorSNS, varInSpliceRegion):
        '''Tests that funciton works correctly for nonsense variant in PRIORS CI domain that does not have splice rescue'''
        boundaries = "priors"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.55C>T"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124042"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbInExonSNS(self.variant, boundaries, variantData)
        # checks that applicable prior and enigma class are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["pathogenic"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class5"])
        # checks that protein prior, ref donor prior, and ref acceptor prior are correct
        self.assertEquals(priorProb["proteinPrior"], priorProbs["pathogenic"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor prior and de novo acceptor prior are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that scores and sequences are present for de novo donor and closest donor
        self.assertNotEquals(priorProb["refDeNovoDonorMES"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorZ"], "N/A")
        # checks that flags are correct for de novo donor and acceptor
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        # checks that scores and sequences are NOT present for ref splice acceptor, ref splice donor, de novo acceptor, and closest acceptor
        self.assertEquals(priorProb["refRefAccMES"], "N/A")
        self.assertEquals(priorProb["refRefDonorZ"], "N/A")
        self.assertEquals(priorProb["altDeNovoAccMES"], "N/A")
        self.assertEquals(priorProb["refRefAccSeq"], "N/A")
        self.assertEquals(priorProb["refRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["altDeNovoAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccMES"], "N/A")
        # checks that flags (splice site, splice rescue, splice rescue flags) are all equal to zero
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], 0)
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["inExonicPortionFlag"], 0)
        self.assertEquals(priorProb["CIDomainInRegionFlag"], 0)
        self.assertEquals(priorProb["isDivisibleFlag"], 0)
        # checks that frameshift flag is correct
        self.assertEquals(priorProb["frameshiftFlag"], 1)
        
    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inExon"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_5',
                                                                        'priorProb': 0.99})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.getPriorProbSpliceRescueNonsenseSNS', return_value = {'CIDomainInRegionFlag': 0,
                                                                                     'inExonicPortionFlag': 0,
                                                                                     'frameshiftFlag': 0,
                                                                                     'isDivisibleFlag': 0,
                                                                                     'spliceFlag': 1,
                                                                                     'enigmaClass': 'N/A',
                                                                                     'priorProb': 'N/A',
                                                                                     'spliceRescue': 1})
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'altZScore': -3.6230599152142147,
                                                                            'closestZScore': 1.1128870300549731,
                                                                            'closestSeq': 'TCGGTAAGA',
                                                                            'refMaxEntScanScore': -6.87,
                                                                            'deNovoDonorAltGreaterClosestFlag': 0,
                                                                            'altMaxEntScanScore': -0.5,
                                                                            'enigmaClass': 'class_2',
                                                                            'deNovoDonorAltGreaterRefFlag': 1,
                                                                            'priorProb': 0.02,
                                                                            'exonStart': 0,
                                                                            'altSeq': 'TACCTGAGT',
                                                                            'intronStart': 3,
                                                                            'closestMaxEntScanScore': 10.53,
                                                                            'closestIntronStart': 3,
                                                                            'varStart': 6,
                                                                            'refSeq': 'TACCTGTGT',
                                                                            'varLength': 1,
                                                                            'refZScore': -6.358144415791253,
                                                                            'closestExonStart': 0})
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    def test_getPriorProbInExonSNSWithSpliceRescueBRCA2(self, getVarLocation, getVarType, getPriorProbProteinSNS,
                                                        getVarConsequences, getPriorProbSpliceRescueNonsenseSNS,
                                                        getPriorProbDeNovoDonorSNS, varInSpliceRegion):
        '''Tests that function works correctly for nonsense variant in exon with possibility of splice rescue'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.6996T>A"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32346885"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbInExonSNS(self.variant, boundaries, variantData)
        # checks that applicable prior and enigma class are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["NA"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["NA"])
        # checks that protein prior, ref donor prior, and ref acceptor prior are correct
        self.assertEquals(priorProb["proteinPrior"], priorProbs["pathogenic"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor prior and de novo acceptor prior are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that scores and sequences are present for de novo donor and closest donor
        self.assertNotEquals(priorProb["refDeNovoDonorMES"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorZ"], "N/A")
        # checks that flags are correct for de novo donor and acceptor
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        # checks that scores and sequences are NOT present for ref splice acceptor, ref splice donor, de novo acceptor, and closest acceptor
        self.assertEquals(priorProb["refRefAccMES"], "N/A")
        self.assertEquals(priorProb["refRefDonorZ"], "N/A")
        self.assertEquals(priorProb["altDeNovoAccMES"], "N/A")
        self.assertEquals(priorProb["altRefAccSeq"], "N/A")
        self.assertEquals(priorProb["altRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["refDeNovoAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccSeq"], "N/A")
        # checks that flags (splice site, splice rescue, splice flag, and splice rescue flags) are all correct
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], 1)
        self.assertEquals(priorProb["spliceFlag"], 1)
        self.assertEquals(priorProb["frameshiftFlag"], 0)
        self.assertEquals(priorProb["inExonicPortionFlag"], 0)
        self.assertEquals(priorProb["CIDomainInRegionFlag"], 0)
        self.assertEquals(priorProb["isDivisibleFlag"], 0)

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["outBounds"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_getPriorProbOutsideTranscriptBoundsSNS(self, getVarLocation, getVarType):
        ''' Tests that function works correctly for both minus and plus strand variants outside transcript boundaries'''
        boundaries = "enigma"
        # checks for minus strand (BRCA1) variant
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.-1074C>G"
        self.variant["Pos"] = "43126325"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbOutsideTranscriptBoundsSNS(self.variant, boundaries)
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        # checks that all other priors are set to N/A
        self.assertEquals(priorProb["proteinPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that all flags are equal to zero or N/A
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")

        # checks for plus strand (BRCA2) variant
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.-764A>G"
        self.variant["Pos"] = "32314943"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbOutsideTranscriptBoundsSNS(self.variant, boundaries)
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        # checks that all other priors are set to N/A
        self.assertEquals(priorProb["proteinPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that all flags are equal to zero or N/A
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'CATATGTGT',
                                                                                       'varWindowPosition': 8,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -13.63,
                                                                                       'altMaxEntScanScore': -5.58,
                                                                                       'refSeq': 'CATATGTAT',
                                                                                       'varStart': 7,
                                                                                       'altZScore': -5.804257601702654,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -9.260683069464845})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -0.870800629704197,
                                                                            'sequence': 'TTTGTGAGT',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon16',
                                                                            'maxEntScanScore': 5.91})
    def test_getPriorProbIntronicDeNovoDonorSNSWithSpliceFlag(self, varInExon, varInSpliceRegion, getVarType,
                                                              getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''Tests that funciton works for variant with predicted splice flag = 1 (altMES > refMES)'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.4986+19a>G"
        self.variant["Pos"] = "43070909"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbIntronicDeNovoDonorSNS(self.variant)
        # checks that prior prob, enigma class, de novo donor flag, and splice flag have the correct values
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        self.assertEquals(priorProb["spliceFlag"], 1)
        # checks that a de novo donor score, sequence, and closest donor sequence are present
        self.assertNotEquals(priorProb["altMaxEntScanScore"], "N/A")
        self.assertNotEquals(priorProb["refSeq"], "N/A")
        self.assertNotEquals(priorProb["closestMaxEntScanScore"], "N/A")

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TTAACAACT',
                                                                                       'varWindowPosition': 8,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -16.81,
                                                                                       'altMaxEntScanScore': -17.75,
                                                                                       'refSeq': 'TTAACAATT',
                                                                                       'varStart': 7,
                                                                                       'altZScore': -11.029685917561768,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -10.62607847163674})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.6534615330977633,
                                                                            'sequence': 'CAGGTATGA',
                                                                            'exonStart': 0,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon5',
                                                                            'maxEntScanScore': 9.46})
    def test_getPriorProbIntronicDeNovoDonorSNSNoSpliceFlag(self, varInExon, varInSpliceRegion, getVarType,
                                                            getMaxMaxEntScanScoreSlidingWindowSNS, getClosestSpliceSiteScores):
        '''Tests that function works for variant with predicted splice flag of 0 (refMES > altMES)'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.476-23t>C"
        self.variant["Pos"] = "32326219"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbIntronicDeNovoDonorSNS(self.variant)
        # checks that prior prob, enigma class, de novo donor flag, and splice flag have the correct values
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        self.assertEquals(priorProb["spliceFlag"], 0)
        # checks that a de novo donor score, sequence, and closest donor sequence are present
        self.assertNotEquals(priorProb["refMaxEntScanScore"], "N/A")
        self.assertNotEquals(priorProb["altSeq"], "N/A")
        self.assertNotEquals(priorProb["closestSeq"], "N/A")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getPriorProbIntronicDeNovoDonorSNS', return_value = {'altZScore': -8.698208862909755,
                                                                                    'closestZScore': -0.11940378888632941,
                                                                                    'closestMaxEntScanScore': 7.66,
                                                                                    'closestSeq': 'GAGGTGAGA',
                                                                                    'refMaxEntScanScore': -10.54,
                                                                                    'altMaxEntScanScore': -12.32,
                                                                                    'enigmaClass': 'N/A',
                                                                                    'deNovoDonorAltGreaterRefFlag': 0,
                                                                                    'priorProb': 'N/A',
                                                                                    'exonStart': 0,
                                                                                    'altSeq': 'CTAATATCT',
                                                                                    'spliceFlag': 0,
                                                                                    'intronStart': 3,
                                                                                    'deNovoDonorAltGreaterClosestFlag': 0,
                                                                                    'closestIntronStart': 3,
                                                                                    'varStart': 1,
                                                                                    'refSeq': 'CCAATATCT',
                                                                                    'varLength': 1,
                                                                                    'refZScore': -7.933930933392152,
                                                                                    'closestExonStart': 0})
    def test_getPriorProbInIntronSNSNoDeNovoBRCA2(self, getVarLocation, getVarType, getPriorProbIntronicDeNovoDonorSNS):
        '''Tests function for plus strand (BRCA2) variant in intron with ref MES score GREATER than alt MES score'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.8755-21c>T"
        self.variant["Pos"] = "32379296"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbInIntronSNS(self.variant, boundaries)
        # checks that prior prob, enigma class, de novo donor flag, and splice flag are all set correctly
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        self.assertEquals(priorProb["spliceFlag"], 0)
        # checks that values are present for de novo donor scores, sequences, and closest donor
        self.assertNotEquals(priorProb["refDeNovoDonorZ"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorZ"], "N/A")
        # checks that values are NOT present for ref donor/acceptor, de novo acceptor, and closest acceptor
        self.assertEquals(priorProb["refRefDonorMES"], "N/A")
        self.assertEquals(priorProb["altRefAccZ"], "N/A")
        self.assertEquals(priorProb["refDeNovoAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccMES"], "N/A")
        # checks that all other priors are set to N/A
        self.assertEquals(priorProb["proteinPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that all flags are equal to zero or N/A
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getPriorProbIntronicDeNovoDonorSNS', return_value = {'altZScore': -5.877250437667818,
                                                                                    'closestZScore': -0.5573608046773153,
                                                                                    'closestMaxEntScanScore': 6.64,
                                                                                    'closestSeq': 'AAGGTGTGT',
                                                                                    'refMaxEntScanScore': -14.16,
                                                                                    'altMaxEntScanScore': -5.75,
                                                                                    'enigmaClass': 'N/A',
                                                                                    'deNovoDonorAltGreaterRefFlag': 1,
                                                                                    'priorProb': 'N/A',
                                                                                    'exonStart': 0,
                                                                                    'altSeq': 'TTGGCCAGA',
                                                                                    'spliceFlag': 1,
                                                                                    'intronStart': 3,
                                                                                    'deNovoDonorAltGreaterClosestFlag': 0,
                                                                                    'closestIntronStart': 3,
                                                                                    'varStart': 7,
                                                                                    'refSeq': 'TTGGCCAAA',
                                                                                    'varLength': 1,
                                                                                    'refZScore': -9.488248969826827,
                                                                                    'closestExonStart': 0})
    def test_getPriorProbInIntronSNSWithFlagBRCA1(self, getVarLocation, getVarType, getPriorProbIntronicDeNovoDonorSNS):
        '''Tests function for minus strand (BRCA1) variant in intron with ref MES score LESS than alt MES score'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.4357+18a>G"
        self.variant["Pos"] = "43082386"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbInIntronSNS(self.variant, boundaries)
        # checks that prior prob, enigma class, de novo donor flag, and splice flag are all set correctly
        self.assertEquals(priorProb["applicablePrior"], priorProbs["NA"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        self.assertEquals(priorProb["spliceFlag"], 1)
        # checks that values are present for de novo donor scores, sequences, and closest donor
        self.assertNotEquals(priorProb["altDeNovoDonorMES"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorMES"], "N/A")
        # checks that values are NOT present for ref donor/acceptor, de novo acceptor, and closest acceptor
        self.assertEquals(priorProb["altRefDonorZ"], "N/A")
        self.assertEquals(priorProb["refRefAccMES"], "N/A")
        self.assertEquals(priorProb["altDeNovoAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccSeq"], "N/A")
        # checks that all other priors are set to N/A
        self.assertEquals(priorProb["proteinPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that all flags are equal to zero or N/A
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "3_prime_UTR_variant")
    def test_getPriorProbInUTRSNS3PrimeBRCA1(self, getVarLocation, getVarType, getVarConsequences):
        '''Tests function for minus strand (BRCA1) variant in 3' UTR'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.5592+10g>A"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43045668"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbInUTRSNS(self.variant, boundaries)
        # checks that applicable prior, applicable class, and splice flag are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["spliceFlag"], 0)
        # checks that de novo and ref donor and acceptor priors are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor and acceptor flags are correct
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        # checks that there are NOT values present for de novo donor and acceptor, ref donor and acceptor, and closest donor/acceptor
        self.assertEquals(priorProb["refDeNovoDonorMES"], "N/A")
        self.assertEquals(priorProb["altDeNovoAccZ"], "N/A")
        self.assertEquals(priorProb["refRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["altRefAccMES"], "N/A")
        self.assertEquals(priorProb["closestDonorZ"], "N/A")
        self.assertEquals(priorProb["closestAccSeq"], "N/A")
        # checks that all flags are equal to N/A
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "3_prime_UTR_variant")
    def test_getPriorProbInUTRSNS3PrimeBRCA2(self, getVarLocation, getVarType, getVarConsequences):
        '''Tests function for plus strand (BRCA2) variant in 3' UTR'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.10257+25t>G"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32398795"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbInUTRSNS(self.variant, boundaries)
        # checks that applicable prior, applicable class, and splice flag are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["spliceFlag"], 0)
        # checks that de novo and reference donor and acceptor priors are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor and acceptor flags are correct
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        # checks that there are NOT values present for de novo donor and acceptor, ref donor and acceptor, and closest donor/acceptor
        self.assertEquals(priorProb["altDeNovoDonorZ"], "N/A")
        self.assertEquals(priorProb["refDeNovoAccMES"], "N/A")
        self.assertEquals(priorProb["altRefDonorZ"], "N/A")
        self.assertEquals(priorProb["refRefAccSeq"], "N/A")
        self.assertEquals(priorProb["closestDonorSeq"], "N/A")
        self.assertEquals(priorProb["closestAccMES"], "N/A")
        # checks that all flags are equal to N/A
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "5_prime_UTR_variant")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'altZScore': -4.69219027729221,
                                                                            'closestZScore': 0.17686125120757246,
                                                                            'closestSeq': 'CAGGTATTG',
                                                                            'refMaxEntScanScore': -11.17,
                                                                            'deNovoDonorAltGreaterClosestFlag': 0,
                                                                            'altMaxEntScanScore': -2.99,
                                                                            'enigmaClass': 'class_2',
                                                                            'deNovoDonorAltGreaterRefFlag': 1,
                                                                            'priorProb': 0.02,
                                                                            'exonStart': 0,
                                                                            'altSeq': 'AAGCTTTGG',
                                                                            'intronStart': 3,
                                                                            'closestMaxEntScanScore': 8.35,
                                                                            'closestIntronStart': 3,
                                                                            'varStart': 4,
                                                                            'refSeq': 'AAGCATTGG',
                                                                            'varLength': 1,
                                                                            'refZScore': -8.204433796086585,
                                                                            'closestExonStart': 0})
    def test_getPriorProbInUTRSNS5PrimeExonDeNovoDonor(self, getVarLocation, getVarType, getVarConsequences, varInExon,
                                                       varInSpliceRegion, getPriorProbDeNovoDonorSNS):
        '''Test function for plus strand (BRCA2) variant in exonic portion of 5' UTR that has de novo donor, no de novo acceptor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.-24A>T"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32316437"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbInUTRSNS(self.variant, boundaries)
        # checks that applicable prior, applicable class, and splice flag are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["spliceFlag"], 0)
        # checks that de novo and ref donor and acceptor priors are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor and acceptor flags are correct
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        # checks that values are present for de novo donor and closest donor
        self.assertNotEquals(priorProb["refDeNovoDonorZ"], "N/A")
        self.assertNotEquals(priorProb["closestDonorSeq"], "N/A")
        # checks that values are NOT present for de novo acceptor, ref donor/acceptor, and closest acceptor
        self.assertEquals(priorProb["altDeNovoAccMES"], "N/A")
        self.assertEquals(priorProb["refRefDonorZ"], "N/A")
        self.assertEquals(priorProb["altRefAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccMES"], "N/A")
        # checks that all flags are equal to N/A
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "5_prime_UTR_variant")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getPriorProbDeNovoAcceptorSNS', return_value = {'altZScore': -3.3549885043158807,
                                                                               'closestZScore': -1.2675994823240817,
                                                                               'deNovoAccAltGreaterClosestFlag': 0,
                                                                               'closestSeq': 'GTTTTTCTAATGTGTTAAAGTTC',
                                                                               'refMaxEntScanScore': -8.78,
                                                                               'altMaxEntScanScore': -0.18,
                                                                               'enigmaClass': 'N/A',
                                                                               'priorProb': 'N/A',
                                                                               'exonStart': 20,
                                                                               'altSeq': 'TCTAATGTGTTAAAGTTCAGTGG',
                                                                               'intronStart': 0,
                                                                               'closestMaxEntScanScore': 4.9,
                                                                               'closestIntronStart': 0,
                                                                               'varStart': 19,
                                                                               'refSeq': 'TCTAATGTGTTAAAGTTCATTGG',
                                                                               'deNovoAccAltGreaterRefFlag': 1,
                                                                               'varLength': 1,
                                                                               'refZScore': -6.888757321073649,
                                                                               'closestExonStart': 20})
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'altZScore': -3.335382267586803,
                                                                            'closestZScore': 1.164411384853913,
                                                                            'closestSeq': 'CTGGTAAGT',
                                                                            'refMaxEntScanScore': -4.19,
                                                                            'deNovoDonorAltGreaterClosestFlag': 0,
                                                                            'altMaxEntScanScore': 0.17,
                                                                            'enigmaClass': 'class_2',
                                                                            'deNovoDonorAltGreaterRefFlag': 1,
                                                                            'priorProb': 0.02,
                                                                            'exonStart': 0,
                                                                            'altSeq': 'AAGTTCAGT',
                                                                            'intronStart': 3,
                                                                            'closestMaxEntScanScore': 10.65,
                                                                            'closestIntronStart': 3,
                                                                            'varStart': 7,
                                                                            'refSeq': 'AAGTTCATT',
                                                                            'varLength': 1,
                                                                            'refZScore': -5.207433825281605,
                                                                            'closestExonStart': 0})
    def test_getPriorProbInUTRSNS5PrimeExonDeNovoAccAndDonor(self, getVarLocation, getVarType, getVarConsequences,
                                                             varInExon, varInSpliceRegion, getPriorProbDeNovoAcceptorSNS,
                                                             getPriorProbDeNovoDonorSNS):
        '''Tests function for minus strand (BRCA1) variant in exonic portion of 5' UTR that has de novo donor and acceptor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.-15T>G"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124111"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbInUTRSNS(self.variant, boundaries)
        # checks that applicable prior, applicable class, and splice flag are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["spliceFlag"], 0)
        # checks that de novo and ref donor and acceptor priors are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor and acceptor flags are correct
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], 0)
        # checks that values are present for de novo donor and de novo acceptor and closest donor/acceptor
        self.assertNotEquals(priorProb["altDeNovoDonorMES"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoAccMES"], "N/A")
        self.assertNotEquals(priorProb["closestDonorZ"], "N/A")
        self.assertNotEquals(priorProb["closestAccSeq"], "N/A")
        # checks that values are NOT present for ref donor and acceptor
        self.assertEquals(priorProb["refRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["altRefAccSeq"], "N/A")
        # checks that all flags are equal to N/A
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "intron_variant")
    @mock.patch('calcVarPriors.getPriorProbIntronicDeNovoDonorSNS', return_value = {'altZScore': -5.112972508150215,
                                                                                    'closestZScore': -1.287289164328958,
                                                                                    'closestSeq': 'CGGGTTAGT',
                                                                                    'refMaxEntScanScore': -11.72,
                                                                                    'deNovoDonorAltGreaterClosestFlag': 0,
                                                                                    'altMaxEntScanScore': -3.97,
                                                                                    'enigmaClass': 'N/A',
                                                                                    'deNovoDonorAltGreaterRefFlag': 1,
                                                                                    'priorProb': 'N/A',
                                                                                    'exonStart': 0,
                                                                                    'altSeq': 'AGTGTATTT',
                                                                                    'spliceFlag': 1,
                                                                                    'intronStart': 3,
                                                                                    'closestMaxEntScanScore': 4.94,
                                                                                    'closestIntronStart': 3,
                                                                                    'varStart': 4,
                                                                                    'refSeq': 'AGTGCATTT',
                                                                                    'varLength': 1,
                                                                                    'refZScore': -8.44058708891506,
                                                                                    'closestExonStart': 0})
    def test_getPriorProbInUTRSNS5PrimeIntronWithSpliceFlag(self, getVarLocation, getVarType, getVarConsequences,
                                                            getPriorProbIntronicDeNovoDonorSNS):
        '''Tests function for variant in intronic portion of 5' UTR for plus strand (BRCA2) gene that has de novo donor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.-39-23c>T"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32316399"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbInUTRSNS(self.variant, boundaries)
        # checks that applicable prior, applicable class, and splice flag are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["NA"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["spliceFlag"], 1)
        # checks that de novo and ref donor and acceptor priors are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor and acceptor flags are correct
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        # checks that values are present for de novo donor and closest donor
        self.assertNotEquals(priorProb["refDeNovoDonorZ"], "N/A")
        self.assertNotEquals(priorProb["closestDonorMES"], "N/A")
        # checks that values are NOT present for de novo acceptor, closest acceptor, and ref donor and acceptor
        self.assertEquals(priorProb["altDeNovoAccMES"], "N/A")
        self.assertEquals(priorProb["closestAccZ"], "N/A")
        self.assertEquals(priorProb["refRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["altRefAccSeq"], "N/A")
        # checks that all flags are equal to N/A
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "intron_variant")
    @mock.patch('calcVarPriors.getPriorProbIntronicDeNovoDonorSNS', return_value = {'altZScore': -5.666859322238815,
                                                                                    'closestZScore': -0.965261946835586,
                                                                                    'closestSeq': 'AAGGTAGTA',
                                                                                    'refMaxEntScanScore': -4.93,
                                                                                    'deNovoDonorAltGreaterClosestFlag': 0,
                                                                                    'altMaxEntScanScore': -5.26,
                                                                                    'enigmaClass': 'N/A',
                                                                                    'deNovoDonorAltGreaterRefFlag': 0,
                                                                                    'priorProb': 'N/A',
                                                                                    'exonStart': 0,
                                                                                    'altSeq': 'TATTTATGT',
                                                                                    'spliceFlag': 0,
                                                                                    'intronStart': 3,
                                                                                    'closestMaxEntScanScore': 5.69,
                                                                                    'closestIntronStart': 3,
                                                                                    'varStart': 3,
                                                                                    'refSeq': 'TATATATGT',
                                                                                    'varLength': 1,
                                                                                    'refZScore': -5.525167346541731,
                                                                                    'closestExonStart': 0})
    def test_getPriorProbInUTRSNS5PrimeIntronNoSpliceFlag(self, getVarLocation, getVarType, getVarConsequences,
                                                          getPriorProbIntronicDeNovoDonorSNS):
        '''Tests variant in intronic portion of 5' UTR for minus strand (BRCA1) gene that does not have de novo donor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.-19-24a>T"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124139"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbInUTRSNS(self.variant, boundaries)
        # checks that applicable prior, applicable class, and splice flag are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["spliceFlag"], 0)
        # checks that de novo and ref donor and acceptor priors are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor and acceptor flags are correct
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestFlag"], "N/A")
        # checks that values are present for de novo donor and closest donor
        self.assertNotEquals(priorProb["refDeNovoDonorZ"], "N/A")
        self.assertNotEquals(priorProb["closestDonorMES"], "N/A")
        # checks that values are NOT present for de novo acceptor, closest acceptor, and ref donor and acceptor
        self.assertEquals(priorProb["altDeNovoAccMES"], "N/A")
        self.assertEquals(priorProb["closestAccZ"], "N/A")
        self.assertEquals(priorProb["refRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["altRefAccSeq"], "N/A")
        # checks that all flags are equal to N/A
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inExon"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_getVarDataNonACTG(self, getVarLocation, getVarType):
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.4965C>R"
        self.variant["Pos"] = "32339320"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "R"
        priorProb = calcVarPriors.getVarData(self.variant, boundaries, variantData)
        self.assertEquals(priorProb["applicablePrior"], "-")

    @mock.patch('calcVarPriors.getVarLocation', return_value = variantLocations["inExon"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    def test_getVarDataNonSNS(self, getVarLocation, getVarType):
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.4965delCinsGA"
        self.variant["Pos"] = "32339320"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "GA"
        priorProb = calcVarPriors.getVarData(self.variant, boundaries, variantData)
        self.assertEquals(priorProb["applicablePrior"], "-")
        
    @mock.patch('calcMaxEntScanMeanStd.fetch_gene_coordinates', return_value = transcriptDataBRCA2)
    def test_getVarDict(self, fetch_gene_coordinates):
        '''
        Tests that: 
        1. Variant information is being parsed correctly
        '''
        boundaries = "enigma"
        varDict = calcVarPriors.getVarDict(self.variant, boundaries)
        self.assertEquals(varDict["varHGVScDNA"], self.variant["HGVS_cDNA"])
        self.assertEquals(varDict["varChrom"], self.variant["Chr"])
        self.assertEquals(varDict["varGene"], self.variant["Gene_Symbol"])
        self.assertEquals(varDict["varGenCoordinate"], self.variant["Pos"])
