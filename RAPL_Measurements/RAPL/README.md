### RAPL Directory

- `main.c`: Entry point of the program (see `../README.md` for more details).
- `rapl.c`: Implements functions for RAPL-based energy estimation. Inspired by: https://web.eece.maine.edu/~vweaver/projects/rapl/
- `rapl.h`: Header file for `rapl.c`, containing definitions and MSR (Model-Specific Register) constants.
- `Makefile`: Compiles the contents of this directory.
- `sensors.c`: Implements functions to calculate the average temperature across all CPU cores.
- `sensors.h`: Header file for `sensors.c`.
