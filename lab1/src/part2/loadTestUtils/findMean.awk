BEGIN { FS = "," }

{
    sum = 0
    for (i=1;i<=NF;i++) sum += $i
    avg = sum / NF
    total += avg
}

END { print "Average response time (milliseconds): " total/NR }