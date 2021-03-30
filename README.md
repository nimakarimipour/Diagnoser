# Diagnoser
Script to run [AutoFixer](https://github.com/nimakarimipour/NullAwayAutoFixer) Diagnoser task

## Dependencies
---
### Overview
`Autofixer` depends on two projects shown below:
1. [AnnotationInjector](https://github.com/nimakarimipour/AnnotationInjector): Used to inject suggested annotations to source code. It receives a path to `json` file where all the suggested fixes are written as an argument. The default location is `/tmp/NullAwayFix/fixes.json`
2. [Customized NullAway](https://github.com/nimakarimipour/NullAway): A special version of `NullAway` with suggested fixes capability. It needs to be on `autofix` branch to have all the fix suggestions features available.

### Installation
`AutoFixer` is delivered via gradle plugin, and all those dependencies will be managed by gradle, However, In this repo, `AutoFixer` is provided via a `jar` file where all dependenceis related to `AnnotationInjector` is already handled. 
To install the customized version of `NullAway` in `maven local` repository, please follow the instructions below:
```
git clone https://github.com/nimakarimipour/NullAway
cd NullAway
git checkout autofixer
./gradlew Install
```
Or simply run the `dependecies.sh` script provided.

The customized version of `NullAway` will be installed at the following location in maven local repository:
```
edu.ucr.cs.riple:nullaway:0.7.12-SNAPSHOT
```


## Requirements for Target Project
---
The only requirement for a target project to run autofixer on is that it needs to work with the [customized](https://github.com/nimakarimipour/NullAway) version of `NullAway` mentioned in `Dependencies/Installation` rather than the original version.
After that the original version of the `NullAway` is replaced by the customized version, the following flag must be sent to `NullAway` to activate the autofix features.
```
-XepOpt:NullAway:AutoFix=true
```

Please find a sample project setup below:
```java
dependencies {
    //Here we pass the customized verion of NullAway
    annotationProcessor "edu.ucr.cs.riple:nullaway:0.7.12-SNAPSHOT"
    compileOnly "com.google.code.findbugs:jsr305:3.0.2"
    errorprone "com.google.errorprone:error_prone_core:2.3.2"
    errorproneJavac "com.google.errorprone:javac:9+181-r4173-1"
}

tasks.withType(JavaCompile) {
    if (!name.toLowerCase().contains("test")) {
        options.errorprone.errorproneArgs += ["-XepDisableAllChecks",
                                              "-Xep:NullAway:ERROR",
                                              "-XepOpt:NullAway:AnnotatedPackages=",
                                              //Autofix flag must be set to true
                                              "-XepOpt:NullAway:AutoFix=true",
                                              "-XepDisableAllWarnings"]
        options.compilerArgs << "-Xmaxerrs" << "100000"
    }
}
```

If `AutoFix` flag is set to `true`, anytime `NullAway` (can be via the build command) is executed on a project, a `fixes.json` file will be generetaed which includes all the suggested fixes.

Please find a sample `fixes.json` below:
```json
{
    "fixes": [
        {
            "annotation": "javax.annotation.Nullable",
            "reason": "FIELD_NO_INIT",
            "method": "",
            "param": "mVelocityTracker",
            "location": "CLASS_FIELD",
            "class": "com.github.CustomGestureDetector",
            "pkg": "com.github.chrisbanes.photoview",
            "uri": "file:AbsolutePathTo/CustomGestureDetector.java",
            "inject": "true"
        },
    ]
}
```

## Config
---
Configurations are written inside the `config.json` file. Please find a sample below:
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
---
Before running, please make sure that all the changes in the `setup` section has been applied to the target project.

The script is written in python in the file `run.py`. It needs the `NullAwayAutoFixer.jar` file to execute at the relative path: `./jars/NulAwayAutoFixer.jar` just like the structure in this repo.
Run the following command to execute the diagnose task

```python
python run.py
```

## Output

