import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# function to take list of brain regions to analyze (in the beginning to either take all regions
    # or just take these regions)
class Brain():

    # female_data: map from brain region (string) to its value (float) for female patients
    # male_data: map from brain region (string) to its value (float) for male patients
    def __init__(self, female_data, male_data):
        self.female_data = female_data
        self.male_data = male_data
        self.n_top_regions = 10
        self.end_percentage = 1.0/3.0
        self.intermediate_percentage = 1-2*(self.end_percentage)
        # self.divergence_map = map from brain region name to the divergence value for that region
        # self.divergence = list of pairs (divergence, region name) in decreasing order
        # self.top_regions = names of the top regions to be used for further analysis
        self.divergence_map, self.divergence, self.top_regions = self.__calculateTopRegions()
        # self.end_ranges_map = map from brain region name to a list of [('M', n, score), ('F', n, score)]
        # 1) 'M' or 'F' means male-end or female-end, respectively
        # 2) n = 1 (>= score) or -1 (<= score)
        # 3) score = least extreme score in that end
        #     example: ('M', -1, 120.4) = categorize any value <= 120.4 into male-end
        #    example: ('M', 1, 120.4) = categorize any value >= 120.4 into male-end
        self.end_ranges_map = self.__calculateRegionScores(self.top_regions)

    # Calculates divergence value (female_mean - male_mean) / (sqrt(female_var + male_var))
    # for each brain region to determine the top brain regions (those with biggest abs(divergence))
    # Number of top regions is determined by self.n_top_regions
    # Returns: divergence map (map from region to its divergence), divergence array (array of
    # (abs(divergence), region name) pairs, in decreasing order), and top_regions array (array or)
    # names of top regions
    def __calculateTopRegions(self):
        divergence_map = {} # map from region (string) to its statistical distance value (float)
        regions = [] # list of region names
        divergence = [] # list of absolute value of divergence
        for region in self.female_data.keys():
            # data for that region
            f = sorted(self.female_data[region])
            m = sorted(self.male_data[region])
            all = sorted(np.hstack((f,m)))

            f_kernel = stats.gaussian_kde(f)
            m_kernel = stats.gaussian_kde(m)

            # subract one kernel from the other and integrate
            kernel_abs_diff = abs(f_kernel.evaluate(all) - m_kernel.evaluate(all))
            diff_area = np.trapz(kernel_abs_diff, all)

            divergence_map[region] = diff_area
            regions.append(region)
            divergence.append(abs(divergence_map[region]))

        # array of sorted (abs(divergences), region) pairs
        sorted_divergence_array = sorted(zip(divergence, regions), reverse=True)

        print(sorted_divergence_array)
        # names of top regions
        top_regions = [x for (y,x) in sorted_divergence_array][:self.n_top_regions]

        return divergence_map, sorted_divergence_array, top_regions

    # Parameter: brain_regions (list of brain regions (string))
    # Calculates the distribution of each brain region in brain_regions
    # "male-end" and "female-end" zones are the scores of the self.end_percentage percent
    # most extreme males and females, respectively.
    # For each brain region, calculates a list of [('M', n, score), ('F', n, score)]
        # 1) 'M' or 'F' means male-end or female-end, respectively
        # 2) n = 1 (>= score) or -1 (<= score)
        # 3) score = least extreme score in that end
    # Returns a map from brain region (string) to its respective list
    def __calculateRegionScores(self, brain_regions):
        end_ranges = {}
        for region in brain_regions:
            # data for that region
            f = sorted(self.female_data[region]) # increasing order
            m = sorted(self.male_data[region])
            # number of regions to be counted into female-end and male-end
            num_f = int(np.ceil(len(f)*(self.end_percentage)))
            num_m = int(np.ceil(len(m)*(self.end_percentage)))
            end_ranges[region] = []
            if(self.divergence_map[region] < 0): # means average in females is larger than average in males
                end_ranges[region].append(('M', -1, m[num_m]))
                end_ranges[region].append(('F', 1, f[-num_f]))
            else:
                end_ranges[region].append(('M', 1, m[-num_m]))
                end_ranges[region].append(('F', -1, f[num_f]))
        return end_ranges

    # Parameter: n (number of top regions)
    # Sets the number of top regions to be included in further analysis, resets self.top_regions
    # to include n number of top regions, and calculates region scores (distribution of male-end,
    # female-end, intermediate) for regions that did not previously have their scores calculated
    def setNumTopRegions(self, n):
        past_num = self.n_top_regions
        self.n_top_regions = n
        past_top_regions = self.top_regions
        # resets names of top regions
        self.top_regions = [x for (y,x) in self.divergence][:n]
        # might need to calculate which scores are cutoffs for female/male-end for new regions
        new_regions = list(set(self.top_regions) - set(past_top_regions))
        if len(new_regions) != 0:
            self.end_ranges_map = self.__calculateRegionScores(new_regions)

    # Returns number of top regions
    def getNumTopRegions(self):
        return self.n_top_regions

    # Returns array of current top regions
    def getTopRegions(self):
        return self.top_regions

    # Parameter: percentage (float)
    # Sets the percentage of data from males to be included in male-end,
    # and the percentage of data from females to be included in female-end
    # Reclaculates the region scores (distribution of male-end, female-end, intermediate)
    def setEndPercentage(self, percentage):
        self.end_percentage = float(percentage)
        self.intermediate_percentage = 1-2*(self.end_percentage)
        # need to recalculate which scores are cutoffs for female/male-end
        self.end_ranges_map = self.__calculateRegionScores(self.top_regions)

    # Returns the percentage of data categorized into one of the ends
    def getEndPercentage(self):
        return self.end_percentage

    # Parameter: region (string)
    # Returns the divergence value for the specified brain region
    def getDivergence(self, region):
        return self.divergence_map[region]

    # Returns the map from brain region (string) to its distribution of male-end, intermediate,
    # and female end (list)
    def getEndRanges(self):
        return self.end_ranges_map

    def drawDistribution(self, region):
        f = self.female_data[region]
        m = self.male_data[region]
        plt.hist(f, bins=len(f), normed=1, histtype='stepfilled', lw=2, edgecolor="None", color="r", alpha=0.5, label="female")
        plt.hist(m, bins=len(m), normed=1, histtype='stepfilled', lw=2, edgecolor="None", color="b", alpha=0.5, label="male")
        plt.legend(loc="upper right")
        plt.xlabel(region)
        plt.ylabel('Probability')
        plt.show()
