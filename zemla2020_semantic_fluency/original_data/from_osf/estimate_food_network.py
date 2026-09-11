import snafu
import networkx as nx

# load FOODS fluency lists, correcting spelling mistakes, grouping by participant

fluencydata = snafu.load_fluency_data("../fluency_data/snafu_sample.csv",
                                      category="foods",
                                      spell="../spellfiles/foods_snafu_spellfile.csv",
                                      hierarchical=True)

# check for any "intrusions". many times, these are just items that are
# misspelled or not categorized if they aren't legitimate intrusions, add any
# misspellings to your spellfile and provide at least one category for them in
# your scheme file, then re-run!

intrusions_num = snafu.intrusions(fluencydata.labeledXs, scheme="../schemes/foods_snafu_scheme.csv")
intrusions_list = snafu.intrusionsList(fluencydata.labeledXs, scheme="../schemes/foods_snafu_scheme.csv")

# check for perseverations... keep in mind some of these may be due to spelling
# corrections e.g., if a participant lists "fry" and "french fries", the latter
# is treated as a perseveration

perseverations_num = snafu.perseverations(fluencydata.labeledXs)
perseverations_list = snafu.perseverationsList(fluencydata.labeledXs)

# Conceptual Network is not a hierarchical method, so let's flatten our data
# before we make a network
fluencydata.nonhierarchical()

# specify some free parameters for generating Conceptual Network below are the
# defaults (if you don't specify them), but they are re-listed here for
# transparency For more details on the Conceptual Network method, see Goni et
# al. (2011) [in journal Cognitive Processing] and Zemla & Austerweil (2018)
# [in Computational Brain and Behavior]

fitinfo = snafu.Fitinfo({'cn_windowsize': 2,           # items co-occur if they fall within +/- this window size
                         'cn_threshold': 2,            # an item must appear in this many lists, else it is excluded 
                         'cn_alpha': 0.05})            # co-occurence p-value must be below this alpha to accept edge

# generate network using Conceptual Network method
# may take a couple minutes, be patient...

foodsnetwork = snafu.conceptualNetwork(fluencydata.Xs, fitinfo=fitinfo)

# write edge list to file

snafu.write_graph(foodsnetwork,
                  "foods_network.csv",      # filename of edge list
                  labels = fluencydata.groupitems,
                  sparse = False,           # list all edge pairs, even if graph has no edge
                  subj = "Group")             # an identifier for the graph in the file (e.g., "S101", "Bilinguals", etc.)
