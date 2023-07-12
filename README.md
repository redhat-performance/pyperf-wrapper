Automation wrapper for pyper

Description:
         From website: The pyperformance project is intended to be an authoritative source of benchmarks
         for all Python implementations. The focus is on real-world benchmarks, rather than synthetic
         benchmarks, using whole applications when possible.

Location of underlying workload: https://github.com/python/pyperformance

Packages required: numactl,perf

To run:
```
[root@hawkeye ~]# git clone https://github.com/redhat-performance/pyperf-wrapper
[root@hawkeye ~]# pyperf-wrapper/pyperf/pyperf_run
```

The script will set the buffer sizes based on the hardware it is being executed on.

```
Options
General options
  --home_parent <value>: Our parent home directory.  If not set, defaults to current working directory.
  --host_config <value>: default is the current host name.
  --iterations <value>: Number of times to run the test, defaults to 1.
  --pbench: use pbench-user-benchmark and place information into pbench, defaults to do not use.
  --pbench_user <value>: user who started everything. Defaults to the current user.
  --pbench_copy: Copy the pbench data, not move it.
  --pbench_stats: What stats to gather. Defaults to all stats.
  --run_label: the label to associate with the pbench run. No default setting.
  --run_user: user that is actually running the test on the test system. Defaults to user running wrapper.
  --sys_type: Type of system working with, aws, azure, hostname.  Defaults to hostname.
  --sysname: name of the system running, used in determining config files.  Defaults to hostname.
  --tuned_setting: used in naming the tar file, default for RHEL is the current active tuned.  For non
    RHEL systems, default is none.
  --usage: this usage message.
```

Note: The script does not install pbench for you.  You need to do that manually.
