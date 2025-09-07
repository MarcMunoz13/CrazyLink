import time
from cf_dronLink.Dron_1 import Dron
from cflib.utils import uri_helper

URI = uri_helper.uri_from_env(default="radio://0/80/2M/E7E7E7E7E7")

def main():
    dron = Dron()
    try:
        dron.connect(uri=URI, blocking=True)
        time.sleep(1)
        dron.takeOff(0.5, blocking=True)
        time.sleep(1)

        dron.go("North"); time.sleep(1)  # +X
        dron.go("South"); time.sleep(1)  # -X
        dron.go("Up");    time.sleep(1)  # +Z
        dron.go("West");  time.sleep(1)  # -Y

        if getattr(dron, "pc", None) is not None:
            dron.pc.land(landing_height=0.0, velocity=0.5)
            time.sleep(2)
            try:
                dron.pc.__exit__(None, None, None)
            except Exception:
                pass
            dron.pc = None
            dron.state = "connected"
        else:
            print("No hay PositionHlCommander activo para aterrizar.")

    finally:
        try:
            dron.disable_local_geofence()
        except Exception:
            pass
        dron.disconnect()

if __name__ == "__main__":
    main()