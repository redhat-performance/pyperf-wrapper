# pyperformance (pyperf) Benchmark Wrapper

## Description

This wrapper facilitates the automated execution of the pyperformance benchmark suite. pyperformance is the official Python benchmark suite maintained by the Python project, measuring Python interpreter performance across real-world application workloads rather than synthetic micro-benchmarks. Results are reported as average execution time per benchmark in seconds.

The wrapper provides:
- Automated pyperformance installation, virtual environment setup, and execution.
- Support for x86_64 (AMD/Intel) and aarch64 (ARM) architectures.
- Configurable pyperformance version selection.
- Selective benchmark execution or full-suite runs.
- Automatic Python version detection and dependency management.
- Result collection, CSV/JSON processing, and Pydantic schema validation.
- System configuration metadata capture.
- Integration with test_tools framework.
- Optional Performance Co-Pilot (PCP) integration.

## Command-Line Options

```
pyperf Options:
  --pyperf_version <value>: Version of pyperformance to install and run.
      Defaults to 1.11.0.
  --python_exec <path>: Python executable to use for running benchmarks.
      Defaults to python3.
  --python_pkgs <packages>: Comma-separated list of additional Python packages to install.
  --pyperf_benchmarks <benchmarks>: Comma-separated list of specific benchmarks to run.
      Defaults to all benchmarks. Example: "2to3,nbody,go".
  --install_pip: Install pip if not available on the system (requires pip3_install integration).

General test_tools options:
  --debug: Enables bash -x output, useful for debugging issues with wrappers.
  --home_parent <value>: Parent home directory. If not set, defaults to current working directory.
  --host_config <value>: Host configuration name, defaults to current hostname.
  --iterations <value>: Number of times to run the test, defaults to 1.
  --iteration_default <value>: Value to set iterations to, if default is not set.
  --no_system_packages: Do not install system packages via the system package manager.
  --no_pip_packages: Do not install python pip packages via pip.
  --no_pkg_install: Test is not to install any packages.
  --run_user: User that is actually running the test on the test system. Defaults to current user.
  --sys_type: Type of system working with (aws, azure, hostname). Defaults to hostname.
  --sysname: Name of the system running, used in determining config files. Defaults to hostname.
  --test_tools_release <tag>: Version tag of test tools to use.
  --json_skip: Skip JSON conversion of test CSV results, default is 0.
  --verify_skip: Skip test verifications against output, default is 0.
  --tuned_setting: Used in naming the results directory. For RHEL, defaults to current active tuned profile.
      For non-RHEL systems, defaults to 'none'.
  --use_pcp: Enable Performance Co-Pilot monitoring during test execution.
  --tools_git <value>: Git repo to retrieve the required tools from.
      Default: https://github.com/redhat-performance/test_tools-wrappers
  --usage: Display this usage message.
```

## What the Script Does

The `pyperf_run` script performs the following workflow:

1. **Environment Setup**:
   - Clones the test_tools-wrappers repository if not present (default: ~/test_tools).
   - Attempts download via wget, then curl, then git clone as fallback.
   - Sources error codes and general setup utilities.
   - Collects system hardware information via gather_data.

2. **Python Validation and Package Installation**:
   - Detects the Python version from the configured executable.
   - Validates the Python executable exists.
   - Installs Python runtime dependencies (python3, python3-devel, python3-pip) via `package_tool` using python_deps/python3.json.
   - Installs system packages (bc, git, numactl, etc.) and pip dependencies (psutil, packaging, pyparsing, pyperf, toml) along with `pyperformance==<version>` via a second `package_tool` call using pyperf.json.
   - Any additional packages specified via `--python_pkgs` are passed to the same `package_tool` call.
   - Dependencies are defined for different OS variants (RHEL, Ubuntu, Amazon Linux).

3. **PCP Setup** (optional):
   - If `--use_pcp` is enabled, sources pcp_commands.inc and initializes PCP monitoring.
   - Creates a timestamped PCP data directory.
   - Starts PCP collection with `start_pcp` and `start_pcp_subset`.

4. **Benchmark Validation**:
   - If specific benchmarks are requested (not "all"), validates each name against the list from `pyperformance list`.
   - Exits with an error if any invalid benchmark names are found.

5. **Virtual Environment Setup**:
   - Creates a pyperformance-managed virtual environment: `python3 -m pyperformance venv create`.
   - Retrieves the venv path via `python3 -m pyperformance venv show`.
   - For pyperformance versions <= 1.11.0, downgrades setuptools to v81.0.0 inside the venv to work around the pkg_resources removal in setuptools v82.0.0.

6. **Test Execution**:
   - Records start timestamp.
   - Runs pyperformance: `python3 -m pyperformance run --output <file>.json [benchmark flags]`.
   - Records end timestamp.
   - Converts JSON output to human-readable format via `pyperf dump`.

7. **Result Processing**:
   - Parses the pyperf dump output to extract per-benchmark results.
   - Extracts test names, individual run values, and units.
   - Converts all time values to nanoseconds for intermediate calculations to preserve precision.
   - Calculates the average for each benchmark.
   - Converts final averages from nanoseconds to seconds.
   - Generates CSV file with columns: Test, Avg, Unit, Start_Date, End_Date.
   - Publishes metrics to PCP (if enabled) via result2pcp.

8. **Validation**:
   - Converts CSV to JSON via csv_to_json from test_tools.
   - Validates results against the Pydantic schema (pyperf_schema.py).
   - Ensures all required fields are present, Avg is positive and finite, and test names are valid.
   - Uses verify_results from test_tools.

9. **Output**:
    - Saves all results and metadata via save_results.
    - Stores raw JSON, human-readable results, and processed CSV in the python_results directory.
    - Archives results and execution log.
    - Stops PCP monitoring (if enabled).

## Dependencies

**pyperformance**: Installed automatically via pip at the specified version (default: 1.11.0) from PyPI.

**RHEL / Amazon Linux packages**: bc, git, zip, unzip, numactl, perf, wget, python3, python3-devel, python3-pip

**Ubuntu packages**: bc, git, python3-lib2to3, zip, unzip, numactl, python3-pip, wget, python3, python3-dev

**pip packages**: psutil, packaging, pyparsing, pyperf, toml

To run:
```bash
git clone https://github.com/redhat-performance/pyperf-wrapper
cd pyperf-wrapper/pyperf
./pyperf_run
```

The script will automatically detect your Python version and install all required dependencies.

## The pyperformance Benchmark Suite

pyperformance (https://github.com/python/pyperformance) is the official benchmark suite maintained by the Python project. It measures the performance of Python implementations using real-world application workloads rather than synthetic micro-benchmarks. The suite is built on top of the pyperf framework, which handles reliable benchmarking with warmup, calibration, and statistical analysis.

### Benchmarks

For the full list of benchmarks included in the default pyperformance version (1.11.0), see the [pyperformance benchmark documentation](https://pyperformance.readthedocs.io/benchmarks.html). You can also list available benchmarks locally by running:

```bash
python3 -m pyperformance list
```

### Key Concepts

1. **Execution Model**: Each benchmark runs multiple times with warmup iterations. The pyperf framework handles calibration automatically to produce statistically reliable results.

2. **Copies/Concurrency**: Unlike HPL or SPEC CPU, pyperformance benchmarks run sequentially (single-threaded per benchmark). The suite measures per-benchmark execution time, not parallel throughput.

3. **Virtual Environment**: pyperformance creates and manages its own virtual environment to isolate benchmark dependencies from the system Python environment.

4. **Performance Metric**: Results are reported as average execution time per benchmark. Lower values indicate better performance. The wrapper converts all results to seconds for consistency.

## Output Files

The `python_results/` directory contains:

- **pyperf_out_\<timestamp\>.json**: Raw pyperformance JSON output containing all benchmark runs with statistical data.
- **pyperf_out_\<timestamp\>.results**: Human-readable pyperf dump output showing per-run values for each benchmark.
- **pyperf_out_\<timestamp\>.csv**: Processed CSV file with averaged results (Test, Avg, Unit, Start_Date, End_Date).
- **PCP data** (if `--use_pcp` option used): Performance Co-Pilot monitoring data with per-benchmark metric values.

Other output files (written to the working directory):

- **pyperf.json**: Final validated JSON results checked against the Pydantic schema.
- **/tmp/pyperf.out**: Complete execution log capturing all wrapper output.

## Examples

### Basic run with defaults
```bash
./pyperf_run
```
This runs with:
- pyperformance version 1.11.0
- System default python3
- All benchmarks
- 1 iteration
- Automatic dependency installation

### Run with a specific pyperformance version
```bash
./pyperf_run --pyperf_version 1.12.0
```
Installs and runs pyperformance version 1.12.0 instead of the default.

### Run with a specific Python executable
```bash
./pyperf_run --python_exec /usr/bin/python3
```
Uses a specific Python interpreter for running benchmarks. The executable's basename must have a matching `python_deps/<basename>.json` file (e.g., `python_deps/python3.json` for `python3`).

### Run specific benchmarks only
```bash
./pyperf_run --pyperf_benchmarks "2to3,nbody,go,float,richards"
```
Runs only the specified benchmarks instead of the full suite.

### Run multiple iterations (via external harness)
```bash
./pyperf_run --iterations 3
```
The `--iterations` option is parsed by the general_setup framework and may be used by external harnesses to repeat the run. The script itself executes a single pyperformance invocation per call.

### Run with PCP monitoring
```bash
./pyperf_run --use_pcp
```
Collects Performance Co-Pilot data during the run, with per-benchmark metric tracking.

### Install pip before running
```bash
./pyperf_run --install_pip
```
**Note**: The `--install_pip` flag is parsed but the `pip3_install()` function that checks it is currently not called in the main flow. pip must be available for `package_tool` to install pyperformance. Install `python3-pip` via your package manager if pip is not present.

### Combination example
```bash
./pyperf_run --pyperf_version 1.11.0 --python_exec /usr/bin/python3 \
    --pyperf_benchmarks "nbody,float,scimark_fft,scimark_lu" \
    --use_pcp
```
Runs selected scientific benchmarks with pyperformance 1.11.0 and PCP monitoring.

## How Result Processing Works

### Unit Conversion and Averaging

The wrapper processes raw pyperf dump output through several conversion steps to produce consistent results:

1. **Parsing**: Reads the pyperf dump output, which contains per-run timing values for each benchmark.
2. **Unit Normalization**: Converts all intermediate values to nanoseconds using the convert_val utility from test_tools. This preserves precision during averaging.
3. **Averaging**: Calculates the arithmetic mean across all runs for each benchmark: `average = sum_of_values / run_count`.
4. **Final Conversion**: Converts averaged nanosecond values to seconds for the output CSV.

This two-stage conversion (to nanoseconds for calculation, to seconds for output) avoids floating-point precision loss that would occur when averaging very small time values directly.

### CSV Output Format

The generated CSV contains one row per benchmark:

| Column | Description |
|--------|-------------|
| Test | Benchmark name (e.g., `2to3`, `nbody`) |
| Avg | Average execution time in seconds |
| Unit | Time unit (always `sec` in final output) |
| Start_Date | Timestamp when the benchmark run started |
| End_Date | Timestamp when the benchmark run completed |

## How Virtual Environment Setup Works

pyperformance manages its own virtual environment to isolate benchmark dependencies:

1. The wrapper calls `python3 -m pyperformance venv create` to create the venv.
2. The venv path is retrieved via `python3 -m pyperformance venv show`.
3. For pyperformance versions <= 1.11.0, a setuptools compatibility fix is applied:
   - setuptools v82.0.0 removed `pkg_resources`, which breaks several benchmarks.
   - The wrapper downgrades setuptools to v81.0.0 inside the venv.
   - This is done using the venv's own Python: `<venv>/bin/python3 -m pip install --upgrade setuptools==81.0.0`.

## PCP Metrics

When `--use_pcp` is enabled, the wrapper tracks the following Performance Co-Pilot metrics:

- **Generic metrics**: iteration, running, numthreads, runtime, throughput, latency
- **Per-benchmark metrics**: One metric per benchmark prefixed with `pyperf_` (e.g., `pyperf_2to3`, `pyperf_nbody`, `pyperf_go`) — 90 benchmark metrics defined in the reset file.

Metrics are initialized to NaN before execution and updated with actual averaged timing values as results become available.

## Return Codes

The script uses standardized error codes from the test_tools error_codes module:

- **0 (E_SUCCESS)**: Success
- **1 (E_PACKAGE_TOOL_PACKAGING)**: Package tool packaging error
- **101 (E_GENERAL)**: General execution errors including:
  - Git clone failure (test_tools-wrappers download)
  - Python executable not found
  - Package installation failures
  - Invalid benchmark names
  - pyperformance venv creation failures
  - CSV-to-JSON conversion failures
  - Schema validation failures
- **102 (E_PACKAGE_TOOL_NO_REMOVE)**: Package tool removal error
- **103 (E_USAGE)**: Invalid arguments or usage errors
- **104 (E_PARSE_ARGS)**: Argument parsing error
- **105 (E_PCP_FAILURE)**: PCP monitoring failure
- **106 (E_INVAL_DATA)**: Invalid data
- **107 (E_NO_ARGS)**: Missing required arguments
- **127 (E_NO_CMD)**: Command not found

The exit code from verify_results (schema validation) is propagated as the final return code when result processing fails.

## Notes

### Architecture Support
- **x86_64**: Full support for AMD and Intel CPUs.
- **aarch64**: Full support for ARM CPUs using the same dependency configuration.

### Python Version Compatibility
- The wrapper works with Python 3 interpreters that have a matching `python_deps/<basename>.json` file. By default, only `python3` is supported.
- Use `--python_exec` to specify a different Python executable. To support additional versions (e.g., python3.12), create a corresponding `python_deps/python3.12.json` dependency file.
- Python development headers (python3-devel/python3-dev) are required for compiling C extension benchmarks.

### pyperformance Version Selection
- Default version is 1.11.0.
- Use `--pyperf_version` to test with different pyperformance releases.
- Versions <= 1.11.0 receive automatic setuptools compatibility fixes.
- Newer versions may add or remove benchmarks; the schema validates against known benchmark names.

### Benchmark Selection
- By default, all benchmarks in the pyperformance suite are executed.
- Use `--pyperf_benchmarks` with a comma-separated list to run specific benchmarks.
- Benchmark names are validated against the pyperformance installation before execution.
- Running the full suite takes significant time (30+ minutes depending on hardware).

### Special Cases
- **setuptools v82.0.0**: Removed `pkg_resources`, breaking benchmarks that depend on it. The wrapper automatically downgrades setuptools to v81.0.0 in the pyperformance venv for affected versions.
- **Ubuntu**: Requires the `python3-lib2to3` package for the 2to3 benchmark, which is not bundled with Python on Ubuntu.
- **pip availability**: The `--install_pip` flag exists but the `pip3_install()` function that checks it is not invoked in the current script flow. Ensure `python3-pip` is installed via your system package manager before running the wrapper.

### Performance Tips
- Run multiple iterations to verify consistency, as Python benchmark variance can be significant.
- Ensure the system is idle (no competing workloads) for best results.
- Disable CPU frequency scaling (use performance governor) for reproducible results.
- Consider the active tuned profile on RHEL systems.
- Use `--use_pcp` to collect detailed system-level performance counters alongside benchmark timings.
- For quick regression testing, select a subset of representative benchmarks instead of the full suite.

### Troubleshooting
- **Python executable not found**: Verify the path specified with `--python_exec` exists and is executable. Run `which python3` to find available interpreters.
- **pip installation failures**: Install `python3-pip` via your system package manager. The `--install_pip` flag exists but is not active in the current script flow.
- **Benchmark validation errors**: Run `python3 -m pyperformance list` to see available benchmarks for the installed version. Benchmark names may differ between pyperformance versions.
- **setuptools errors**: If benchmarks fail with `pkg_resources` import errors, the automatic setuptools downgrade may not have applied. Check the venv path and manually install setuptools==81.0.0.
- **Schema validation failures**: If new benchmarks are added in newer pyperformance versions, the schema (pyperf_schema.py) may need updating with the new benchmark names.
- **Low or inconsistent results**: Python benchmarks are sensitive to system load, CPU frequency, and memory pressure. Ensure the system is idle and CPU governor is set to "performance".
