import threading
import time
from cflib.positioning.position_hl_commander import PositionHlCommander


def go(self, direction):

    if self.state != "flying":
        print("Dron no está volando.")
        return False

    # Aseguro de que hay un PositionHlCommander activo
    if not hasattr(self, 'pc') or self.pc is None:
        print("No existe un PositionHlCommander activo.")
        return False



    # guardo variable de distancia para poderla editar en eñ futuro
    dist = 0.5
    vel = getattr(self, 'move_speed', 0.5)

    try:
        if direction == "North":
            self.pc.forward(dist, velocity=vel)
        elif direction == "South":
            self.pc.back(dist, velocity=vel)
        elif direction == "East":
            self.pc.right(dist, velocity=vel)
        elif direction == "West":
            self.pc.left(dist, velocity=vel)
        elif direction == "Up":
            self.pc.up(dist, velocity=vel)
        elif direction == "Down":
            self.pc.down(dist, velocity=vel)
        elif direction == "Stop":
            # parar de forma explícita
            try:
                self.pc.stop()
            except Exception:
                try:
                    self.cf.commander.send_stop_setpoint()
                except Exception:
                    pass
        else:
            print(f" ERROR")
            return False

        return True

    except Exception as e:
        self.state = "error"
        print(f"Error al mover en dirección {direction}: {e}")
        return False


