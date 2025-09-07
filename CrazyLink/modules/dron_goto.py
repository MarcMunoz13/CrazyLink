import threading
import time
from cflib.positioning.position_hl_commander import PositionHlCommander

# tolerancia en metros para determinar si realizar el movimento
_TOL = 0.2

def _goto(self, x, y, z, callback=None, params=None):

    # Aseguro de que hay un PositionHlCommander activo y sino, lo creo
    if not hasattr(self, 'pc') or self.pc is None:
        self.pc = PositionHlCommander(
            self.scf,
            x=0.0, y=0.0, z=0.0,
            default_height=max(0.5, z),
            default_velocity=getattr(self, 'move_speed', 0.5),
            default_landing_height=0.0,
            controller=PositionHlCommander.CONTROLLER_PID
        )
        print("PositionHlCommander (re)creado")

    # Si el geofence se ha excedido, abortamos antes de mandar cualquier setpoint
    if not getattr(self, '_gf_monitoring', True):
        print("Goto abortado: geofence ya excedido.")
        return


    ##compruebo que el punto esté a una distancia mas alejada que _TOL para hacer el movimiento
    if all(getattr(self, a, None) is not None for a in ('x', 'y', 'z')):
        dx0 = abs(self.x - x)
        dy0 = abs(self.y - y)
        dz0 = abs(self.z - z)
        if dx0 < _TOL and dy0 < _TOL and dz0 < _TOL:
            print("Ya estoy en la posición.")
            if callback:
                try: callback(params)
                except TypeError: callback()
            return

    # si no estoy volando doy la orden de despegar a 0.5m y espero 2s a estabilizar
    if self.state != 'flying':
        self.takeOff(0.5, blocking=True)
        time.sleep(0.5)

    vel = getattr(self, 'move_speed', 0.5)

    # voy a las coordenadas marcadas a velocidad configurada
    try:
        print(f"Moviéndome a ({x:.1f}, {y:.1f}, {z:.1f})...")
        self.pc.go_to(x, y, z, velocity=vel)
    except Exception as e:
        print(f"Error en go_to: {e}")
        return

    # espero a la llegada
    while True:
        #compruebo que no haya roto geofence
        if not getattr(self, '_gf_monitoring', True):
            print("Goto interrumpido por geofence")
            return
        #si no hay posicion, espero
        if not hasattr(self, 'x'):
            time.sleep(0.1)
            continue


        dx = abs(self.x - x)
        dy = abs(self.y - y)
        dz = abs(self.z - z)
        if dx < _TOL and dy < _TOL and dz < _TOL:
            break
        time.sleep(0.1)

    print(f"He llegado a ({x:.1f}, {y:.1f}, {z:.1f})!")
    if callback:
        try:
            callback(params)
        except TypeError:
            callback()


def goto(self, x, y, z, blocking=True, callback=None, params=None):
    t = threading.Thread(
        target=_goto,
        args=(self, x, y, z, callback, params),
        daemon=True
    )
    t.start()
    if blocking:
        t.join()
