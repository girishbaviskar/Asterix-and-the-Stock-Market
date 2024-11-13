#!/usr/bin/env bash
$1 clean install
$1 exec:java -pl Server -Dexec.mainClass=com.compsci677.lab1.part2.TradingServer -Dexec.args="$2 $3"