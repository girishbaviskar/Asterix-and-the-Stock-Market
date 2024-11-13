#!/usr/bin/env bash
$1 clean install
$1 exec:java -pl Client -Dexec.mainClass=com.compsci677.lab1.part2.CustomerClient  -Dexec.args="$2 $3 $4"