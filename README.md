# Diagnoser
Script to run [AutoFixer](https://github.com/nimakarimipour/NullAwayAutoFixer) Diagnoser task

## Dependencies/Installation

`Autofixer` depends on two projects shown below which should be installed in `maven local` repository.
1. [AnnotationInjector](https://github.com/nimakarimipour/AnnotationInjector): Used to inject suggested annotations to source code.
2. [NullAway](https://github.com/nimakarimipour/NullAway): A special version of `NullAway` with suggested fixes capability.

`AnnotationInjector` receives a path to `json` file where all the suggested fixes are written as an argument. The default location is `/tmp/NullAwayFix/fixes.json`

`NullAway` needs to be on `autofix` branch to have all the fix suggestions features available.


`AutoFixer` is delivered via gradle plugin, and all those dependencies will be managed by gradle, However, In this repo, `AutoFixer` is provided by a `jar` file where all above dependenceis are inside the jar file, therefore, no installation is requred.

## Requirements for target Project
The only requirement for a target project to run autofixer on is that it needs to work with the customized version of `NullAway` mentioned in `Dependencies/Installation` rather than the original version.
After that the original version of the `NullAway` is replaced by the [customized](https://github.com/nimakarimipour/NullAway) version the following flags must be sent to `NullAway` to activate the auto fix features.
```
-XepOpt:NullAway:AutoFix=true
```
To install the customized version in `maven local` repository, please run the following command:
```
git clone https://github.com/nimakarimipour/NullAway
cd NullAway
git checkout autofix
./gradlew install
```
or simply run the `dependenceis.sh` script.


## Config

Configurations are written inside the `config.json` file. Please find the sample below:
```json
{
    "PROJECT_PATH": "/Users/nima/Developer/ArtifactEvaluation/NullAwayFixer/Projects/PhotoView",
    "BUILD_COMMAND": "./gradlew build -x test",
    "FIX_PATH": "/tmp/NullAwayFix/fixes.json"
}
```
Below is the description of each setting:
1. `PROJECT_PATH`: the path to the project directory (if a subproject needs to be analyzied, this path needs to point to the subproject not the root project)
2. `BUILD_COMMAND`: the command to execute `NullAway` for the project at the path given in `PROJECT_PATH`. The script will use the command, `cd PROJECT_PATH && BUILD_COMMAND` to execute `NullAway`.
3. The path to the `fixes.json` file where all the fixes are written which we want to anaylyze their impact.

## Run

Before running, please make sure that all the changes in the `setup` section has been applied to the target project.

The script is written in python in the file `run.py`. It needs the `NullAwayAutoFixer.jar` file to execute at the relative path: `./jars/NulAwayAutoFixer.jar` just like the structure in this repo.
Run the following command to execute the diagnose task

```python
python run.py
```

## Output

