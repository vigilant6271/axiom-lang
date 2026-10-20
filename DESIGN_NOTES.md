# Design Notes

## Adaptive moving average

For observation x and smoothing factor alpha:

`ema_n = alpha * x_n + (1 - alpha) * ema_(n-1)`

A larger alpha responds faster; a smaller alpha smooths noise. The prototype keeps a bounded sample window and reports observations. It does not autonomously rewrite programs.

## Performance claims

An adaptive formula does not itself improve execution speed. The 16x–32x idea remains a research target requiring a native compiler, suitable workload suite, credible baselines, and repeatable measurements.
