## Requirements

- Debian-based Linux distributions
- Intel processor (compatible with RAPL)
- Non-containerized environment

## Required Libraries
1. RAPL
2. lm-sensors
3. Powercap
4. Raplcap

Install all dependencies by running:

```bash
sudo bash install.sh
```

## Prerequisites and Configuration

Before running any measurements, ensure that the following conditions are met:

### 1. Close Unnecessary Applications and Processes
Close all unnecessary applications and background processes to minimize measurement noise
and reduce system overhead. This includes, for example, disabling Wi-Fi and Bluetooth,
closing web browsers, email clients, and other non-essential services.

### 2. System Permissions
Run the C main function with `sudo` privileges to ensure access to the RAPL registers.

### 3. Power Caps Configuration
The script uses power caps values defined in `POWER_CAPS` array. By default, it's set to `(-1)` which means no power capping. You can modify this in the script to test different power caps:
```bash
POWER_CAPS=(7 11 15)  # Test with 7W, 11W, and 15W power caps
```

---

## Temperature Calibration

To calibrate the average CPU core temperature, execute the following:

```bash
cd RAPL
make
./main --temperature-calibration -sleep-secs XX
```

Replace `XX` with the number of seconds to idle (sleep) before measuring the temperature.
The output will be saved to `/tmp/cores_temperature.txt`. 

---

## Powercap Calibration

To determine the most energy-efficient power cap setting for your system, you must specify custom programs for calibration. The tool supports both compiled and interpreted languages.

### Usage

```bash
cd RAPL
make
# For compiled languages
sudo -E ./main --powercap-calibration -range <min>-<max> -variance <V> -time_out_limit <hours> -secs_to_sleep <secs> -n_times <N> -compile_cmd "<compile_cmd>" -run_cmd "<run_cmd>" -language <language> -program <program>

# For interpreted languages
sudo -E ./main --powercap-calibration -range <min>-<max> -variance <V> -time_out_limit <hours> -secs_to_sleep <secs> -n_times <N> -run_cmd "<run_cmd>" -language <language> -program <program>
```

### Parameters

- Replace `min`-`max` with the desired power cap range in Watts (e.g., 2-25).
- `variance` is the allowed temperature fluctuation (e.g., 5), and can be set to 0.
- `time_out_limit` is the maximum time in hours allowed for each test iteration.
- `secs_to_sleep` is the number of seconds where the CPU is idle before measuring the temperature.
- `n_times` is the number of times to execute the test program.
- `compile_cmd` (for compiled languages): Compilation command for your test program.
- `run_cmd`: Execution command for your test program.
- `language`: Programming language (e.g., C, Python).
- `program`: Name identifier for the program being tested.

### Examples

**C program calibration:**
```bash
sudo -E ./main --powercap-calibration -range 40-60 -variance 3 -time_out_limit 2 -secs_to_sleep 30 -n_times 10 -compile_cmd "gcc myprogram.c -o myprogram" -run_cmd "./myprogram" -language C -program myprogram
```

**Python script calibration:**
```bash
sudo -E ./main --powercap-calibration -range 40-60 -variance 3 -time_out_limit 2 -secs_to_sleep 30 -n_times 5 -run_cmd "python3 myscript.py" -language Python -program myscript
```

**Compiled program with specific arguments:**
```bash
sudo -E ./main --powercap-calibration -range 40-60 -variance 3 -time_out_limit 2 -secs_to_sleep 30 -n_times 7 -compile_cmd "gcc fibonacci.c -o fib" -run_cmd "./fib 20" -language C -program fibonacci
```

This will calibrate power caps from 2W to 25W, running 7 executions per power cap value, allowing for a 5°C temperature variance and a 2-hour limit per execution. If the initial temperature is not calculated, it will calibrate the temperature while waiting for 30 seconds of idle time.

## Parametrized Execution

To perform energy measurements on a specific program, use the following syntax  (`--standard`):

```bash
./main --standard -command "<command>" -language <language> -program <program> -n_times <n_times> -variance <variance> -time_out_limit <time_out_limit> -sleep_time <sleep_time> -powercap <powercap>
```

### Arguments

| Argument          | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| `<command>`       | The command to execute (e.g., `./my_program`)                               |
| `<language>`      | Programming language (e.g., `C`, `Python`)                                  |
| `<program>`       | Name of the program being tested                                            |
| `<n_times>`       | Number of times to execute the program (must be > 0)                        |
| `<variance>`      | Acceptable temperature variance (in Celsius, must be ≥ 0)                   |
| `<time_out_limit>`| Timeout limit per execution (in hours, must be > 0)                       |
| `<sleep_time>`    | Idle time before execution (in seconds, must be ≥ 0)                        |
| `<powercap>`      | Power cap in watts (-1 for no power cap, or > 0 for power cap)             |

### Examples

```bash
cd RAPL
make

# Run with 15W power cap
sudo ./main --standard -command "./my_program" -language C -program my_program -n_times 5 -variance 3 -time_out_limit 20 -sleep_time 10 -powercap 15

# Run without power cap (set to -1)
sudo ./main --standard -command "./my_program" -language C -program my_program -n_times 5 -variance 3 -time_out_limit 20 -sleep_time 10 -powercap -1

# Python example with 20W power cap
sudo ./main --standard -command "python3 script.py" -language Python -program script -n_times 3 -variance 5 -time_out_limit 30 -sleep_time 5 -powercap 20
```

The first example will:
- Perform idle measurement for 10 seconds
- Execute the program 5 times with a 15W power cap
- Add 3°C to the temperature variance 
- Terminate executions exceeding 20 hours

---

## CSV Output Format

The CSV file contains the following columns:

|      Column       | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| **Language**      | Programming language                                                        |
| **Program**       | Program name                                                                |
| **Powercap**      | Power cap value applied (Watts)                                             |
| **Package**       | Energy used by the full socket (cores + GPU + other components)            |
| **Core**          | Energy used by CPU cores and caches                                         |
| **GPU**           | Energy used by GPU                                                          |
| **DRAM**          | Energy used by RAM                                                          |
| **Time**          | Execution time (in milliseconds)                                            |
| **Temperature**   | Average core temperature (in Celsius)                                       |
| **Memory**        | Total physical memory used (in KBytes)                                      |

---

## Over-time session mode

This feature allows running a program while a background thread records the energy consumption of the **Package**, **Core**, **DRAM**, and **GPU** components during its execution.  
You can specify an **interval** (in milliseconds) that determines how often the measurements are recorded.

Usage:

```bash
sudo ./main --over-time -command "$(command)" -interval $(interval) -language $(language) -program $(program) -powercap $(powercap) -sleep-secs $(sleep_secs) -variance $(variance)
```

Options:
- `<command>`: Command to execute while logging (quote if it contains spaces).
- `<interval-ms>`: Logging interval in milliseconds (positive integer).
- `<language>`: Programming language label (e.g., `C`, `Python`).
- `<program>`: Program identifier/name used in CSV output.
- `-powercap WATTS`: Optional power cap in watts (use `-1` for no cap). Defaults to `-1`.
- `-sleep-secs SECS`: Optional quick temperature calibration sleep (seconds) used before measuring. Defaults to `30`.

Example:

```bash
# Log every 100 ms while running a program once and do a temperature calibration of 60 seconds
sudo -E ./main --over-time -command "./my_program" -interval 100 -language C -program my_program -powercap 15 -sleep-secs 60
```

Collects the following metrics in a CSV file:

|      Metric       | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| **Language**      | Programming language                                                        |
| **Program**       | Program name                                                                |
| **Powercap**      | Power cap value applied (Watts)                                             |
| **Package**       | Energy used by the full socket (cores + GPU + other components)             |
| **Core**          | Energy used by CPU cores and caches                                         |
| **GPU**           | Energy used by GPU                                                          |
| **DRAM**          | Energy used by RAM                                                          |
| **Timestamp**     | Timestamp for each measurement interval (in milliseconds)                   |
| **Temperature**   | Average core temperature at a certain timestamp (in Celsius)                |

This command runs a program once and, over time, collects all the metrics listed above at each timestamp interval.
