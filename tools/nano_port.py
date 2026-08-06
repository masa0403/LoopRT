import glob


def detect_nano_port():
    ports = glob.glob("/dev/ttyUSB*")
    ports.sort()

    if not ports:
        raise RuntimeError(
            "Nanoのシリアルポートが見つかりません。"
        )

    return ports[0]