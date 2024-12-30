# exo-slpn-testing
This is a repository for the testing of a new modelling formalism called
"Stochastic Petri Nets with Exogenous Dependencies" (Exo-SLPN). Included are
two folders which contain the files used to generate evaluation figures
and tables.

The code (which uses the ProM framework) used to generate the data within each 
folder can be found here: [ExogenousData Plugin](https://github.com/promworkbench/ExogenousData/tree/main/src/org/processmining/qut/exogenousdata/ab/jobs). A more 
in-depth breakdown on the code and reproduction steps can be found in the 
readmes in each sub-folder.

## Event logs
This evaluation uses three event logs, from different domains, paired with 
exogenous data.

### MIMIC
The first event log comes from the MIMIC III dataset~\cite{Johnson2016} which 
contains `MICU' ward admissions focusing on the first 48 hours of admission 
and follows the preparation outlined in~\cite{Banham2022a}.For this log, blood 
pressure measurements collected from nurse observations are used for 
exogenous data. 

### Toy Smart Factory
The second log comes from a smart factory~\cite{Malburg2023}, where only the 
`WF\_101' process is considered and the start events within these executions 
(as these are associated IoT sensors).

### Road Fines 
The third log used is the road fines event log~\cite{roadfines}. 
For this log, inter-case variables from the log were used as exogenous data, 
i.e. the total number of unpaid fines and the amount of unpaid fines seen 
in the event log. 

## System Requirements

During testing it was noted that for larger logs, exersive amounts of system
memory were required (in the range 256Gb to 1TB) for discovering and measuring
unit Earth movers (including the data-aware variants). As such, both road fines
and MIMIC logs were randomlly reduced through trail and error to run the evaluation
with the following system requirements:
 - RAM: 64GB (4 x 16GB DDR4 @ 1053 MHz, Dual Channel)
 - CPU: AMD Ryzen 9 3900XT

Notely, not all existing techniques have a threaded version so in some cases,
runtime could be improved. However, both Exo-SLPN discovery and conformance 
checking that  were implemented for this study are threaded.

## Log Incompleteness
To show that our approach can identify the stochastic nature of a process, we considered how the model quality changes as we apply our approach to progressively more complete samples of a given log.
The intuition being that with a more complete understanding of the original, the discovered stochastic nature should better reflect the original or at least not degrade.

For each sample, we discovered an Exo-SLPN (recording runtime and memory usage) and then using the complete log, we compute duEMSC to quantify the quality of the discovered Exo-SLPN.
We created many samples logs of the road fines log, where the n-th sample consists of $1000 \cdot n$ traces, and each progressive larger sample contains all samples from previous sample.

In the sub-folder ['log-completeness'](./log-completeness/) there are three logging
files which describe the performance of EXo-SLPNs. Each logging file describes
the performance outcomes for a single equation form for Exo-SLPNs, i.e. 
individual multiplictive (invmut), individual additive (invadd), and global 
additive (globadd).

These logging files are then visualised using python and can be rerun to 
reproduce the figures relating to log-incompleteness.

## Model Quality
To compare our approach against existing, we discovered a variety of stochastic extensions of Petri nets and considered how close these nets represent the 
stochastic nature of a log.
A variety of extensions from the inductive miner family were selected to discover
control-flow models, which then a variety of stochastic miners were applied.

The procedure for discovering and quantifying a model consisted of: (i) discovering a control-flow model with the original log, (ii) sampling the original log with replacement, (iii) discovering stochastic weights using the sampled log and control-flow model, and (iv) measure the discovered stochastic model using the original log. 
The same sampled log for step (ii) and (iii) is used across techniques.

In the sub-folder ['model-quality'](./model-quality/) there are the discovered
Exo-SLPNs and the measured (data-aware) Unit Earth Movers conformance result.
Where possible all original data is kept in the data folders and the 
extracting scripts for exogenous data.

## References



