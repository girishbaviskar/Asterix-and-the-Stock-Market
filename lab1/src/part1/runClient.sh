#!/usr/bin/env bash
$1 clean install
$1 exec:java -pl Client -Dexec.mainClass=com.compsci677.lab1.part1.Client  -Dexec.args="$2 $3 $4"




