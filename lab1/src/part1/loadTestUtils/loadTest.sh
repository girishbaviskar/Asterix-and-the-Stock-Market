#!/usr/bin/env bash
$1 clean install
rm -rf loadTestResult
mkdir loadTestResult
rm -rf loadTestResult/*

for run in {1..5};
do
$1 exec:java -pl Client -Dexec.mainClass=com.compsci677.lab1.part1.Client -DloadTest="loadTestResult/loadRes$run" -Dexec.args="$2 $3 1000" &
done
wait
awk 'FNR==1&&NR!=1{print ""}1' loadTestResult/loadRes* > loadTestResult/combinedResult
awk 'NF' loadTestResult/combinedResult > loadTestResult/averageReponseTimePerClient
rm loadTestResult/combinedResult
rm -rf loadTestResult/loadRes*
awk -f loadTestUtils/findMean.awk loadTestResult/averageReponseTimePerClient > loadTestResult/averageResponseTime


