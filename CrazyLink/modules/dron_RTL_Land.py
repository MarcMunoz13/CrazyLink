import threading
import time
from cflib.positioning.position_hl_commander import PositionHlCommander



def _goDown(self, mode, callback=None, params = None):


    print(f"Iniciando aterrizaje")

    try:
        if not hasattr(self, 'pc'):
            print("No existe un PositionHlCommander activo.")
            return False

        vel = getattr(self, 'move_speed', 0.5)


        print("Volviendo a casa")
        self.pc.go_to(0.0, 0.0, 1.0, velocity=vel)


        # MIRO SI EL DRON HA LLEGADO A LA POSICION SEGURA, SI CAMBIO LA ALTURA TENDRÉ QUE CAMBIAR EL (((((self.z-h)))))
        tol = 0.05  # tolerancia en metros
        while True:
            # Aseguramos que self.x/y/z ya existen
            if not hasattr(self, 'x'):
                time.sleep(0.1)
                continue
            # Salimos del bucle cuando estamos dentro de la tolerancia de la posición segura
            if abs(self.x) < tol and abs(self.y) < tol and abs(self.z - 1) < tol:
                print("Posición segura alcanzada (0, 0, 1)")
                break
            time.sleep(0.1)



        print("Iniciando aterrizaje")
        self.pc.land(landing_height=0.0, velocity=0.5)
        time.sleep(2)  # Espera hasta completar accion

        #cierro el PositionHlCommander
        try:
            self.pc.__exit__(None, None, None)
        except Exception:
            pass
        self.pc = None

        self.state = "connected"
        print("Aterrizaje completado.")



        if callback != None:
            if self.id == None:
                if params == None:
                    callback()
                else:
                    callback(params)
            else:
                if params == None:
                    callback(self.id)
                else:
                    callback(self.id, params)


    except Exception as e:
        self.state = "error"
        print(f"Error en aterrizaje: {e}")
        return False



def Land (self, blocking=True, callback=None, params = None):
    if self.state == 'flying' or self.state == 'returning':
        self.state = 'landing'
        if blocking:
            self._goDown('LAND', callback, params)
        else:
            goingDownThread = threading.Thread(target=self._goDown, args=['LAND', callback, params])
            goingDownThread.start()
        return True
    else:
        return False

