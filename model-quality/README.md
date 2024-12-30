# Model Quality Testing

This folder contains all the data and discovered stochastic Petri nets used
to compare between approaches.
Where possible all data used can be found in subfolders, with the extraction
scripted used to prepare and generate exogenous data.
Notably, MIMIC data cannot be directly redistrubed so instead we refer users
back to our previous work for the extraction processes [1].

For existing approaches, the ProM Gui was used to perform discovery and
conformance checking. While for the proposed approch a programatic code runner 
is provided.

## Files

In each subfolder contains the event logs used for discovery at the top level
and two subfolders, 'models' and 'out'.
The 'models' subfolders contain the based control-flow models and existing approaches
enhanced models.
The 'out' subfolders contain the discovered exo-slpns and their data-aware
unit Earth movers conformance measurement.

## Code Runner

The code runner for this evaluation can be found in the ExogenousData Package
for ProM. The runner in question is [ExoSLPNModelQualityTesting](https://github.com/promworkbench/ExogenousData/blob/main/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNModelQualityTesting.java)

Users should clone the ExogenousData project from github and open the plugin 
using Eclipse.  Some manual editing in the code is 
required to direct the runner to the correct directories and signpost where 
the stdout should be generated, the following section outlines these steps.

The JRE used for the run configuration was version 1.8.0_251, but the ProM
framework can be run on latter versions.The run configuration for the code 
runner should be set up with the following parameters:
```code
-ea -Xmx50G -XX:MaxPermSize=256m -Djava.library.path=. -Djava.util.Arrays.useLegacyMergeSort=true  -Djava.library.path=.\lib\
```

## Reproduction Steps

The following steps ensure that exo-slpns are discovered, measured, and recorded
in the 'out' sub-folders in this directory.


### Step One
Set the variable ['dataFolder'](https://github.com/promworkbench/ExogenousData/blob/e92f1197ce94c027696df54ff2cdbb8c974937fc/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNModelQualityTesting.java#L49) in `ExoSLPNModelQualityTesting.java` to 
the absolute path to this sub-folder.

### Step Two
Set the variable ['feedbackFolder'](https://github.com/promworkbench/ExogenousData/blob/e92f1197ce94c027696df54ff2cdbb8c974937fc/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNModelQualityTesting.java#L225) in `ExoSLPNModelQualityTesting.java` to 
the absolute path to this sub-folder.

### Step Three
Decide what weight form for exo-slpns you would select to evaluate:
- if testing the multiplicative form (eq 1);
    - then ensure that only [these lines](https://github.com/promworkbench/ExogenousData/blob/e92f1197ce94c027696df54ff2cdbb8c974937fc/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNModelQualityTesting.java#L227-L228) for variables 'outFile' and 
    'outSuffix' are uncommented;
    - and ensure that only the following [configuration call](https://github.com/promworkbench/ExogenousData/blob/e92f1197ce94c027696df54ff2cdbb8c974937fc/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNModelQualityTesting.java#L297-L302) 
    is uncommented in the runner.
- if testing the additive form (eq 2);
    - then ensure that only [these lines](https://github.com/promworkbench/ExogenousData/blob/e92f1197ce94c027696df54ff2cdbb8c974937fc/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNModelQualityTesting.java#L230-L231) for variables 'outFile' and 
    'outSuffix' are uncommented;
    - and ensure that only the following [configuration call](https://github.com/promworkbench/ExogenousData/blob/e92f1197ce94c027696df54ff2cdbb8c974937fc/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNModelQualityTesting.java#L304-L309) 
    is uncommented in the runner.
- if testing the global additive form (eq 3);
    - then ensure that only [these lines](https://github.com/promworkbench/ExogenousData/blob/e92f1197ce94c027696df54ff2cdbb8c974937fc/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNModelQualityTesting.java#L233-L234) for variables 'outFile' and 
    'outSuffix' are uncommented;
    - and ensure that only the following [configuration call](https://github.com/promworkbench/ExogenousData/blob/e92f1197ce94c027696df54ff2cdbb8c974937fc/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNModelQualityTesting.java#L311-L316) 
    is uncommented in the runner.

### Runtime Notes

The data-aware unit Earth mover conformance checking does take a much longer
on the following models: the POWL model for roadfines and POWL model for mimic.
In these cases, the measurement can take up to 24 hours, even when threaded.

## References

[1] Banham, A., Leemans, S.J.J., Wynn, M.T., Andrews, R., Laupland, K.B., Shinners,
L.: xPM: Enhancing exogenous data visibility. Artif. Intell. Medicine (2022)