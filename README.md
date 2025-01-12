My solutions to the 2024 advent of code (https://adventofcode.com/2024). I am not competing for the public leaderboard,
but aim to provide high-quality solutions. All solutions have been developed without external help or hints,
with the following exceptions:

- For Day 21 I had the right approach but was unable to get the correct answer for the second part. I looked at reddit which confirmed I had tha right approach. I re-wrote my solution a second time (using the same approaches) and this time the result was correct. I suspect something around the optimization of the multiple ways to get from one key to another (e.g. <<v vs. v<<) was the root cause, but I never found the culprit. I deleted the first version of the code and retained the second. The information I found on reddit did not change the overall design - optimizing multiple alternate key directions to a single for each pair of keys, and compressing the key sequences into a dictionary of '...A' sequences and their occurrence count were already accounted for in the original design.

Note to self, regarding profiling...

Profiling: python3 -m cProfile -s tottime some_file.py