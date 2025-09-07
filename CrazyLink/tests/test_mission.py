import time
import threading

from cf_dronLink.Dron_1 import Dron

URI = "radio://0/80/2M/E7E7E7E7E7"

def main():
    dron = Dron()

    if not hasattr(dron, "run_mission_points"):
        try:
            from cf_dronLink.modules.dron_mission import run_mission_points
            dron.run_mission_points = run_mission_points.__get__(dron, Dron)
        except Exception as e:
            print(f"[TEST] No pude enlazar run_mission_points: {e}")
            return

    # Velocidad de misión
    dron.move_speed = 0.3  # m/s

    # Waypoints (x, y, z, delay_s)
    puntos = [
        (0.5, 0.5, 0.5, 1.0),
        (0.5, -0.5, 0.5, 1.0),
        (0.0, 0.0, 0.5, 1.0),
        (-0.5, 0.0, 1.0, 1.0),
    ]

    finished = threading.Event()
    def on_finish():
        print("[TEST] Misión finalizada (Land completado).")
        finished.set()

    try:
        print("[TEST] Conectando...")
        dron.connect(uri=URI, blocking=True)
        print("[TEST] Conectado.")

        dron.start_position_stream(lambda x, y, z: None, period_in_ms=100)

        print("[TEST] Iniciando misión...")
        dron.run_mission_points(puntos, do_land=True, tol=0.2, on_finish=on_finish)

        if not finished.wait(timeout=180):
            print("[TEST] Timeout de misión. Intentando Land forzado...")
            try:
                dron.Land(blocking=True)
            except Exception as e:
                print(f"[TEST] Falló Land forzado: {e}")

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