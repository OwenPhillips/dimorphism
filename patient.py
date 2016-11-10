import numpy as np
from scipy import stats
from math import log
import matplotlib.pyplot as plt
import os

class Patient:
    # patient_id = id of patient, type: string
    # gender = gender of patient, type: string
    # data = map from name of brain region (string) to its value (float)
    def __init__(self, patient_id, gender, data):
        self.id = patient_id
        self.gender = gender
        self.data = data
        # self.__region_zones = map from name of region (string) to its category (male-end,
        # female-end, or intermediate)
        self.__region_zones = {}

    # Returns gender of this patient
    def getGender(self):
        return self.gender

    # Returns data of this patient (map from brain region (string) to its value (float))
    def getData(self):
        return self.data

    # Parameter: top_regions (regions to be included in calculation);
    # end_ranges (map from region (string) to its distribution of each brain region in brain_regions
    # "male-end" and "female-end" zones are the scores of the self.end_percentage percent
    # most extreme males and females, respectively.
    # For each brain region, calculates a list of [('M', n, score), ('F', n, score)]
    # 1) 'M' or 'F' means male-end or female-end, respectively
    # 2) n = 1 (>= score) or -1 (<= score)
    # 3) score = least extreme score in that end)
    # Returns map from brain region (string) to the zone that region is categorized in ('M', 'F', or 'I')
    def calculateRegionZones(self, top_regions, end_ranges):
        for region in top_regions:
            score = self.data[region]
            ranges = end_ranges[region]
            if (ranges[0][1] == -1 and ranges[0][2] >= score):
                self.__region_zones[region] = ranges[0][0]
            elif (ranges[0][1] == 1 and ranges[0][2] <= score):
                self.__region_zones[region] = ranges[0][0]
            elif (ranges[1][1] == -1 and ranges[1][2] >= score):
                self.__region_zones[region] = ranges[1][0]
            elif (ranges[1][1] == 1 and ranges[1][2] <= score):
                self.__region_zones[region] = ranges[1][0]
            else:
                self.__region_zones[region] = 'I'
        return self.__region_zones

    # Returns map from brain region (string) to which zone that region is in ('M' = male-end,
    # 'F' = female-end, 'I' = intermediate). Only for top regions
    def getRegionZones(self):
        return self.__region_zones

    # Returns true if all top brain regions are in one end or intermediate,
    # false if any one region is in a different category from othe others
    def isConsistent(self):
        n_female_end = 0
        n_male_end = 0
        n_intermediate = 0
        for region in self.__region_zones.keys():
            if (self.__region_zones[region] == 'M'):
                n_male_end = n_male_end + 1
            elif (self.__region_zones[region] == 'F'):
                n_female_end = n_female_end + 1
            else:
                n_intermedaite = n_intermediate + 1
        return (n_female_end == 0 and n_intermediate == 0) or (n_male_end == 0 and n_intermediate == 0) or (
        n_male_end == 0 and n_intermediate == 0)

    def plotProbDensity(self, female_data, male_data):
        for region in self.data.keys():
            f = sorted(female_data[region])
            m = sorted(male_data[region])
            f_kernel = stats.gaussian_kde(f)
            m_kernel = stats.gaussian_kde(m)

            # plot pdfs for every var
            plots_path = 'results/pdfplots/'
            if not os.path.exists(plots_path):
                os.makedirs(plots_path)

            figpath = plots_path + str(region)

            plt.plot(f, f_kernel.evaluate(f), 'pink')
            plt.plot(m, m_kernel.evaluate(m), 'blue')
            plt.title(str(region))
            plt.xlabel(region)
            plt.ylabel('probability density')
            plt.savefig(figpath)
            plt.close()

    def genderLikelihood(self, female_data, male_data):
        ratio_map = {}
        for region in self.data.keys():
            f = sorted(female_data[region])
            m = sorted(male_data[region])
            value = self.data[region]

            if(value == float("inf")):
                ratio_map[region] = 'NA'
                continue

            f = [x for x in f if x != float("inf")]
            m = [x for x in m if x != float("inf")]

            # using gaussian kernel density estimate
            f_kernel = stats.gaussian_kde(f)
            m_kernel = stats.gaussian_kde(m)
            f_pdf = f_kernel.evaluate(value)[0]
            m_pdf = m_kernel.evaluate(value)[0]

            # Calculate log likelihood ratio (add small amount to both values to prevent div0 and log(0) errors
            llr = log((m_pdf + 0.0000000001)/ (f_pdf + 0.0000000001))
            ratio_map[region] = llr

            ## plot pdfs for every var (deprecated method)

            # plots_path = 'results/sex_differences/pdfplots/'
            # if not os.path.exists(plots_path):
            #     os.makedirs(plots_path)
            #
            # figpath = plots_path + str(region)
            #
            # plt.plot(f, f_kernel.evaluate(f), 'pink')
            # plt.plot(m, m_kernel.evaluate(m), 'blue')
            # plt.title(str(region))
            # plt.xlabel('measure')
            # plt.ylabel('probability density')
            # plt.savefig(figpath)
            # plt.close()

        return ratio_map

    # (Deprecated) Method for calculating posterior probability using Bayes' Theorem. An alternative to using
    # the log likelihood ratio as a dimorphism score. This value would be between 0 and 1 and
    # reflects the percent chance that a subject is male given a data point.
    def posteriorProb(self, female_data, male_data):
        prob_map = {}

        for region in self.data.keys():
            f = sorted(female_data[region])
            m = sorted(male_data[region])
            value = self.data[region]

            if(value == float("inf")):
                prob_map[region] = 'NA'
                continue

            f = [x for x in f if x != float("inf")]
            m = [x for x in m if x != float("inf")]

            #### using gaussian kernel density estimate
            f_kernel = stats.gaussian_kde(f)
            m_kernel = stats.gaussian_kde(m)
            f_pdf = f_kernel.evaluate(value)[0] #likelihood
            m_pdf = m_kernel.evaluate(value)[0] #likelihood
            prior = 0.5
            p_data = f_pdf*prior + m_pdf*prior
            prob_map[region] = m_pdf*prior/p_data
        return prob_map
