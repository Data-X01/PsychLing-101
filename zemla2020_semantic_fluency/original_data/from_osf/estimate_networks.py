import snafu
import numpy as np

filepath = "../fluency_data/snafu_sample.csv"
category="animals"

# These fitting parameters are used for U-INVITE and/or Conceptual Network
fitinfo = snafu.Fitinfo({
        'cn_alpha': 0.05,                   # p-value for deciding if two nodes occur together more than chance. Goni et al (2011) Table 1 \alpha
        'cn_windowsize': 2,                 # Do two items in a list co-occur? See Goni et al (2011) Fig 1
        'cn_threshold': 2,                  # At least this many co-occurrences to add an edge. See Goni et al (2011) Table 1 'Hits'
        })

# read in data from file, flattening all participants together
fluencydata = snafu.load_fluency_data(filepath,
                category=category,
                removePerseverations=True,
                spell="../spellfiles/animals_snafu_spellfile.csv",
                hierarchical=False,
                group="Experiment1")

# Estimate the best network using a Naive Random Walk
nrw_graph = snafu.naiveRandomWalk(fluencydata.Xs, numnodes=fluencydata.groupnumnodes)
print('Estimated Naive Random Walk network')

# Estimate the best network using Conceptual Network (Goni et al)
cn_graph = snafu.conceptualNetwork(fluencydata.Xs, numnodes=fluencydata.groupnumnodes, fitinfo=fitinfo)
print('Estimated Conceptual Netwok')
    
# Estimate the best network using Pathfinder (Chan et al)
pf_graph = snafu.pathfinder(fluencydata.Xs, numnodes=fluencydata.groupnumnodes)
print('Estimated Pathfinder Network')

# Estimate the best network using correlation-based Network (Kenett et al)
# Requires the 'planarity' module for Python
cbn_graph = snafu.correlationBasedNetwork(fluencydata.Xs, numnodes=fluencydata.groupnumnodes)
print('Estimated Correlation-Based Network')

# Estimate the best network using First-Edge (Abrahao et al)
fe_graph = snafu.firstEdge(fluencydata.Xs, numnodes=fluencydata.groupnumnodes)
print('Estimated First-Edge Network')

# write edge lists to a file
snafu.write_graph(nrw_graph, "nrw_graph.csv", labels=fluencydata.groupitems, subj="GROUP")
snafu.write_graph(cn_graph, "cn_graph.csv", labels=fluencydata.groupitems, subj="GROUP")
snafu.write_graph(pf_graph, "pf_graph.csv", labels=fluencydata.groupitems, subj="GROUP")
snafu.write_graph(cbn_graph, "cbn_graph.csv", labels=fluencydata.groupitems, subj="GROUP")
snafu.write_graph(fe_graph, "fe_graph.csv", labels=fluencydata.groupitems, subj="GROUP")
