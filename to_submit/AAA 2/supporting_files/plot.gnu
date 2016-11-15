set key off
set term png
set output 'of.png'
# Each bar is half the (visual) width of its x-range.
set boxwidth 0.5 absolute
set style fill solid 1.0 noborder
set xlabel 'Number of turns'
set ylabel 'Frequency'
set xrange [0:120]
plot 'dataf' using ($1):(1) smooth frequency with boxes