import threading
import time
from cflib.positioning.position_hl_commander import PositionHlCommander


def _takeOff(self, aTargetAltitude,callback=None, params = None):

    try:
        if self.state in ("flying", "takingOff"):
            print(f"Estado {self.state}: no se inicia un nuevo despegue.")
            return False

        alt = max(0.5, float(aTargetAltitude))


        #creo o recreo PositionHlCommander si no existe
        if not hasattr(self, 'pc') or self.pc is None:
            self.pc = PositionHlCommander(
                self.scf,
                x=0.0, y=0.0, z=0.0,
                default_height=alt,
                default_velocity=0.5,
                default_landing_height=0.0,
                controller=PositionHlCommander.CONTROLLER_PID
            )
            print("PositionHlCommander (re)creado")

        self.state = "takingOff"
        print('empezamos a despegar')



        #despego a la altura en 1m/s
        self.pc.take_off(alt, 1.0)
        time.sleep(2) #estabilizo

        try:
            self._gf_grace_until = time.time() + 1.0
        except Exception:
            pass

        self.state = "flying"
        print(f" Crazyflie volando")

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
        print(f"No se pudo despegar Crazyflie: {e}")


def takeOff(self, aTargetAltitude, blocking=True, callback=None, params = None):
    print ('vamos a despegar')
    if self.state == 'connected':
        if blocking:
            self._takeOff(aTargetAltitude, callback, params)
        else:
            takeOffThread = threading.Thread(target=self._takeOff, args=[aTargetAltitude, callback, params])
            takeOffThread.start()
        return True
    else:
        return False
