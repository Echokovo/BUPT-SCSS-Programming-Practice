from services.serverAPI import serverAPI


def heartbeat_schedule():
    serverAPI.heartbeat()