# Log Completeness Testing

This folder contains all the data used to evaluate exo-slpn discovery when
given more complete samples with respect to a original log. For this evaluation
one event log was used, i.e. the road fines log and the normative model.


## Files

Below is a list of the files in this sub-folder

In ['data'](./data), there should be four files:
- the road fines log;
- an xes file for the exogenous influence of amount of unpaid fines;
- an xes file for the exogenous influence of the total amount of fines unpaid;
- and the ['models'](./data/models/) subfolder contains the normative model for the road fines log;

In the directory, there should be:
- visualise.py (which produces the evaluation visualisation);
- three logging files which describe the performance of weight forms in 
exo-slpns:
    - exo-slpn-eq-1-incomplete.stdout
    - exo-slpn-eq-2-incomplete.stdout
    - exo-slpn-eq-3-incomplete.stdout
- 9 visualisations (3 for each form in different formats, png, eps, svg)

## Code Runner

The code runner to produce the stdout files needed to visualise the evaluation
data can be found within the ExogenousData package, i.e. 
[github.com/promworkbench/ExogenousData/blob/main/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNRMMTesting.java](https://github.com/promworkbench/ExogenousData/blob/main/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNRMMTesting.java). 

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

A small wrapper is used to redirect stdout for the java process into a .stdout
for capturing diagonstic information for the evaluation.
The wrapper can be found at [github.com/promworkbench/ExogenousData/blob/main/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNRMMTestingRunner.java](https://github.com/promworkbench/ExogenousData/blob/main/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNRMMTestingRunner.java).

The following steps should be repeated for each type of weight form to be
tested.

### Step One 

Set the variable [outFile](https://github.com/promworkbench/ExogenousData/blob/437912b3a9d29b1e65e761c60a3cbf57dfe3ed97/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNRMMTesting.java#L34) in `ExoSLPNRMMTestingRunner` to '[the absolute path to this directory]/[exo-slpn-eq-?-incomplete].stdout'. Where ? is either 1,2,3 is your choice of weight form for testing.

### Step Two

Set the variable [dataDir](https://github.com/promworkbench/ExogenousData/blob/main/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNRMMTesting.java#L34) in `ExoSLPNRMMTesting.java` to the absolute path of the sub-folder [data](./data/).

### Step Three

Uncomment out the desired equation form within the list variable `forms` in 
`ExoSLPNRMMTestingRunner`.

The following lines are mapped to the equation numbers for data in this folder:
- 1; multiplicative form; [uncomment this](https://github.com/promworkbench/ExogenousData/blob/437912b3a9d29b1e65e761c60a3cbf57dfe3ed97/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNRMMTesting.java#L66);
- 2; additive form; [uncomment this](https://github.com/promworkbench/ExogenousData/blob/437912b3a9d29b1e65e761c60a3cbf57dfe3ed97/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNRMMTesting.java#L67);
- 3; global additive form; [uncomment this](https://github.com/promworkbench/ExogenousData/blob/437912b3a9d29b1e65e761c60a3cbf57dfe3ed97/src/org/processmining/qut/exogenousdata/ab/jobs/ExoSLPNRMMTesting.java#L68)

If the user wishs, all three can be uncommented, producing a single
stdout file with all the evaluation data.

### Step Four

Lanuch a run configuration through Eclipse targeting `ExoSLPNRMMTestingRunner`,
using the parameters outlined in the 'Code Runner' section. Note that for 
our evaluation, the runner was rerun at least another 4 times to capture the
variablity of each weight form. Rerunning the runner will append new metrics to
the specified stdout file. After the process and reruns are completed, 
the logging file can be visualised using the following steps.

1) 
    Grep the logging file with the follow command:
    ```bash
    grep "\[Outcomes\]" [exo-slpn-eq-?-incomplete.stdout] > exo-slpn-eq-?-incomplete.txt
    ```
    The command grabs the performance metrics from the sampling process.

2) 
    Then, the performance metrics can be visualised using 'visualise.py' in the folder,
    using the following command:
    ```bash
    py visualise.py exo-slpn-eq-?-incomplete.txt
    ```

To run the visualise.py, ensure that you have matplotlib and numpy installed
in your python environment. Python '3.11.5', Matplotlib '3.8.4', and 
numpy '1.26.4' were used, but realistically diferences in versions shouldn't 
affect the visualisation.
