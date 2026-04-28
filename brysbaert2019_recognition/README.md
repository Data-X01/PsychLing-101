Reference:
Brysbaert, M., Keuleers, E., & Mandera, P. (2019). Recognition times for 54 thousand Dutch words: Data from the Dutch Crowdsourcing Project. *Psychologica Belgica*, 59(1), 281–300. https://doi.org/10.5334/pb.491

Data source:
https://osf.io/5fk8d/

Description

* Task: Participants indicated which words they knew (yes/no vocabulary test); response times were recorded even though speed was not emphasized
* Nonwords (~1/3 of stimuli) were included to penalize guessing; participants were warned that yes-responses to nonwords would be penalized
* 26,000,000 trial-level data points from 410,000 sessions
* 54,319 unique Dutch stimulus words (predominantly uninflected lemma forms)
* Data collected via internet vocabulary test (woordentest.ugent.be), in collaboration with Dutch newspapers and television
* Metadata collected: native language status, country of upbringing (Belgium vs. Netherlands), education level, gender, age, number of languages spoken
  * NOTE: Participants could take the test more than once (receiving new items each time). Only the first 3 sessions per IP address were used, all trials were included. 
* Mean RT: 1,326 ms (SD = 282); considerably longer than lab-based lexical decision tasks (~600 ms) due to untimed nature of the task
* Outlier removal: responses > 8,000 ms excluded; further trimming using adjusted boxplot method for skewed distributions (Hubert & Vandervieren, 2008)
* Only correct trials included in RT calculations; overall accuracy = .84
* Standardized RTs (zRTs) also provided (correlation with raw RTs: r = .977)
* Data split available by education level (high school / bachelor / master) and age group (18-29 / 30-49 / 50+)

* NOTE: original data gets downloaded in preprocess_data.R step. Because raw dat ais too big for git lfs. 

