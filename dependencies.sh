if [ mvn dependency:get -Dartifact=edu.ucr.cs.riple:nullaway:0.7.12-SNAPSHOT -o -DrepoUrl=file://~/.m2/repository ]; then
    :
else
    pushd /tmp/
    git clone https://github.com/nimakarimipour/NullAway.git
    pushd NullAway
    git checkout autofix

    ./gradlew install
    
    popd
    popd
fi

if [ mvn dependency:get -Dartifact=edu.ucr.cs.riple:annotationinjector:1.0-SNAPSHOT -o -DrepoUrl=file://~/.m2/repository ]; then
    :
else
    pushd /tmp/
    git clone https://github.com/nimakarimipour/AnnotationInjector.git
    pushd AnnotationInjector
    git checkout stable

    ./gradlew install
    
    popd
    popd
fi


if [ mvn dependency:get -Dartifact=edu.ucr.cs.riple:NullAwayAutoFixer:1.0-SNAPSHOT -o -DrepoUrl=file://~/.m2/repository ]; then
    :
else
    pushd /tmp/
    git clone https://github.com/nimakarimipour/NullAwayAutoFixer.git
    pushd NullAwayAutoFixer

    ./gradlew install

    popd
    popd
fi