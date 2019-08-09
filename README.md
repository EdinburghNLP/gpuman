## gpuman - program for monitoring GPU temperature and killing processes

This program monitors NVIDIA GPU temperature and acts according to its 
configuration file. If the temperature is above the "notify" threshold,
it sends notifications. If it is above the "kill" threshold, it kills
processes (using SIGABRT) in the hope of cooling down the system before
damage occurs. See `examples/gpuman.cfg` for an example configuration 
file.

