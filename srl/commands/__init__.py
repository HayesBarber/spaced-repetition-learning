from . import add, audit, config, inprogress, list_, mastered, nextup, remove

DISPATCH = {
    "add": add.handle,
    "remove": remove.handle,
    "list": list_.handle,
    "mastered": mastered.handle,
    "inprogress": inprogress.handle,
    "nextup": nextup.handle,
    "audit": audit.handle,
    "config": config.handle,
}
