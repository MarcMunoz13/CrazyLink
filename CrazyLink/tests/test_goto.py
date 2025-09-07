import time
from cf_dronLink.Dron_1 import Dron
from cflib.utils import uri_helper

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

def main():
    dron = Dron()

    dron.move_speed = 0.3  # m/s

    try:
        print("[TEST] Conectando...")
        dron.connect(uri=URI, blocking=True)
        print("[TEST] Conectado.")

        dron.start_position_stream(lambda x, y, z: None, period_in_ms=100)

        print("[TEST] yendo a (0.5, 0.5, 1.0) a 0.3 m/s...")
        dron.goto(1.0, 1.0, 1.0, blocking=True)
        print("[TEST] Llegada al objetivo.")

        time.sleep(1)

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

    except Exception as e:
        print(f"[TEST] Error: {e}")

    finally:
        try:
            dron.disconnect()
        except Exception:
            pass
        print("[TEST] Desconectado.")

if __name__ == "__main__":
    main()