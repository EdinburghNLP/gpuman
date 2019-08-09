import fire
import pynvml as nv
import yaml
from time import sleep
from gpuman.pushover import Pushover
import socket
import os
import signal
import logging

def temperatures():
    ret = {}
    for i in range(nv.nvmlDeviceGetCount()):
        hdl = nv.nvmlDeviceGetHandleByIndex(i)
        temp = nv.nvmlDeviceGetTemperature(hdl, nv.NVML_TEMPERATURE_GPU)
        ret[i] = temp
    return ret

def pushover_notify(cfg, who, msg, **kw):
    pusher = Pushover(cfg["pushover"]["key"])
    pusher.message(who["user"], msg, timestamp=True, **kw)

def logging_notify(cfg, who, msg, **kw):
    m = "%s: %s" % (kw["title"], msg)
    logging.info(m)

def notify(cfg, msg, **kw):
    for who in cfg["notify"]:
        if who["type"] == "pushover":
            pushover_notify(cfg, who, msg, **kw)
        elif who["type"] == "log":
            logging_notify(cfg, who, msg, **kw)

def getprocs():
    for i in range(nv.nvmlDeviceGetCount()):
        hdl = nv.nvmlDeviceGetHandleByIndex(i)
        for p in nv.nvmlDeviceGetComputeRunningProcesses(hdl):
            yield p.pid

def cmd(config):
    with open(config) as fp:
        cfg = yaml.load(fp)

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

    nv.nvmlInit()

    hostname = socket.gethostname()

    notified = False
    while True:
        temps = temperatures()
        maxtemp = max(temps.values())
        if not notified and maxtemp >= cfg["thresholds"]["notify"]:
            title = "%s has hot GPUs" % hostname
            msg = "\n".join("GPU%d: %d" % (i, temps[i]) for i in sorted(temps.keys()))
            notify(cfg, msg, title=title)
            notified = True
        if notified and maxtemp < cfg["thresholds"]["notify"]:
            title = "%s GPUs have cooled down" % hostname
            msg = "\n".join("GPU%d: %d" % (i, temps[i]) for i in sorted(temps.keys()))
            notify(cfg, msg, title=title)
            notified = False
        if maxtemp >= cfg["thresholds"]["kill"]:
            procs = list(getprocs())
            title = "%s critically hot GPUs" % hostname
            msg = "killing %d processes" % len(procs)
            notify(cfg, msg, title=title)
            for proc in procs:
                os.kill(proc, signal.SIGABRT)
		
        sleep(1)

def main():
    fire.Fire(cmd)
