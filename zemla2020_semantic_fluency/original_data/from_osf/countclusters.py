import snafu

# Load WRAP data, excluding intrusions and perseverations (spell-corrected)
print('Loading fluency data without intrusions or perseverations...')
fluency_noip = snafu.load_fluency_data("wrap_itemlevel_20190618.csv",
                                       spell="animals_snafu_spellfile.csv",
                                       removeIntrusions=True,
                                       removePerseverations=True,
                                       scheme="animals_snafu_scheme.csv",
                                       cleanBadChars=True)                      # removes spaces and stray punctuation

# WRAP scoring excluded intrusions and perseverations before clustering statistics
# count cluster switches and avg cluster size per list
print('Counting cluster sizes and switches...')
cluster_size = snafu.clusterSize(fluency_noip.labeledXs, "animals_snafu_scheme.csv", clustertype="static")
cluster_switch = snafu.clusterSwitch(fluency_noip.labeledXs, "animals_snafu_scheme.csv", clustertype="static")

# Load WRAP data, including intrusions and perseverations (spell-corrected)
print('Loading fluency data with intrusions or perseverations...')
fluencydata = snafu.load_fluency_data("wrap_itemlevel_20190618.csv",
                                      spell="animals_snafu_spellfile.csv",
                                      cleanBadChars=True)

# Number of perseverations
print('Counting perseverations...')
num_persev = snafu.perseverations(fluencydata.labeledXs)
persev_list = snafu.perseverationsList(fluencydata.labeledXs)

# Number of intrusions
print('Counting intrusions and generating intrusion list...')
num_intrusion = snafu.intrusions(fluencydata.labeledXs, 'animals_snafu_scheme.csv')

# A closer look shows most of these intrusions are not really intrusions
# Valid intrusions: pecan, pumpkinseed, child, veal
# Misspelling: beavr, gazebra, coyore
# Not categorized: labradoodle, mayfly
intrusion_list = snafu.intrusionsList(fluencydata.labeledXs, 'animals_snafu_scheme.csv')
intrusion_list = sorted(set(snafu.flatten_list(intrusion_list)))
# len(intrusion_list) == 249 unique intrusions

# WRAP counts valid, intrusions, and perseverations separately
# We compare the sum of these (e.g., valid + persev + intrusion) between SNAFU and hand-coded
print('Counting total number of responses...')
totalcount = [len(i) for i in fluencydata.labeledXs]

print('Calculating AoA and word frquency....')
# by imputing 0.5 for missing words missing from the SUBTLEX norms, all responses are included
wf, wf_excluded = snafu.wordFrequency(fluencydata.labeledXs, data='subtlex-us.csv', missing=0.5)
aoa, aoa_excluded = snafu.ageOfAcquisition(fluencydata.labeledXs, data='kuperman.csv')

# what percentage of responses are excluded from the age-of-aquisition calculation?
aoa_percentage_excluded = len(snafu.flatten_list(aoa_excluded)) / len(snafu.flatten_list(fluencydata.labeledXs))

# grab order of subject ids and list nums
sub_list, listnum_list = zip(*fluencydata.listnums)

# merge data into rows, including sub and list number
print('Writing data to file...')
to_write = list(zip(
            sub_list,
            listnum_list,
            totalcount,
            num_persev,
            num_intrusion,
            cluster_size,
            cluster_switch,
            wf,
            aoa
            ))

# write data to file
with open('clusters.csv','w') as fo:
    fo.write('id,listnum,numresponses,perseverations,intrusions,clustersize,clusterswitch,wordfreq,aoa\n')
    for i in range(len(to_write)):
        fo.write(','.join([str(j) for j in to_write[i]]) + '\n')
fo.close()
