subid: Do NOT use this variable. Use 'uniform_id' instead. 
trialid: Position of trial (text) in experiment: 1-12
itemid: Do NOT use this variable - use 'trialid' instead.
cond: Condition - not applicable here.
sentnum: Number of sentence within text
wordnum: Number of interest area (IA) within text
word: Text of IA
blink: Variable indicating whether there was blink directly before, during, or directly after the IA was fixated
skip: Variable indicating whether the IA was fixated in the trial
nrun: Number of times the IA was reread within the trial ("reread" means that it was read again after it has been left to the left or right)
reread: Variable indicating whether the IA was reread at least once during the trial
nfix: Number of fixations on the IA during the whole trial
refix: Variable indicating whether the IA has been refixated at least once during a trial
reg.in: Variable indicating whether there was at least one regression into the IA 
reg.out: Variable indicating whether there was at least one regression from the IA
dur: Total time the interest area was read during the trial in ms (total reading time)
firstrun.skip: Variable indicating whether the IA was skipped during first-pass reading
firstrun.nfix: Number of fixations made on the IA during first-pass reading
firstrun.refix: Variable indicating whether the IA was refixated during first-pass reading
firstrun.reg.in: Variable indicating whether there was a regression into the IA during first-pass reading
firstrun.reg.out: Variable indicating whether there was a regression from the IA during first-pass reading
firstrun.dur: Time the IA was read during first-pass reading (gaze duration)
firstrun.gopast: Sum of all fixations durations from the time the IA was entered until it was left to the right (go-past time/regression path duration)
firstrun.gopast.sel: Sum of all fixations on the IA from the time the IA was entered until it was left to the right (selective go-past time: go-past time minus the time of the regression path)
firstfix.sac.in: Incoming saccade length (in letters) for the first fixation on the IA
firstfix.sac.out: Outcoming saccade length (in letters) for the first fixation on the IA
firstfix.launch: Launch site distance (incoming saccade length until the space before the IA)
firstfix.land: Landing position (letter) of the first fixation on the IA
firstfix.cland: Centered landing position of the first fixation on the IA (Vitu et al., 2001: (landing position - (wordlength + 1)) / 2)
firstfix.dur: Duration of the first fixation on the IA (first fixation duration)
singlefix: Variable indicating whether the IA was fixated only once during first-pass reading
singlefix.sac.in: Incoming saccade length (in letters) for the first fixation on the IA when it was fixated only once during first-pass reading
singlefix.sac.out: Outgoing saccade length (in letters) for the first fixation on the IA when it was fixated only once during first-pass reading
singlefix.launch: Launch site distance (incoming saccade length until the space before the IA) for the first fixation on the IA when it was fixated only once during first-pass reading
singlefix.land: Landing position (letter) of the first fixation on the IA when it was read only once
singlefix.cland: Centered landing position of the first fixation on the IA when it was read only once
singlefix.dur: Duration of the first fixation on the IA when it was read only once
lang: language code - du: Dutch; ee: Estonian; en: English; fi: Finnish; ge: German; gr: Greek; he: Hebrew; it: Italian; ko: Korean; no: Norwegian; ru: Russian; sp: Spanish; tr: Turkish.
trial: do NOT use. Use 'trialid' instead.
supplementary_id: do NOT use. Use 'uniform_id' instead.
uniform_id: Participant ID. Please use this variable in all analyses in order to merge different data frames. 
