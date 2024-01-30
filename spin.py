# -*- utf-8 -*-

from rich.status import Status
from time import sleep

status_list = ["First status","Second status","Third status"]
with Status("Initial status") as status:
    sleep(3)  # or do some work
    for stat in status_list:
        status.update(stat)
        sleep(3)  # or do some more work