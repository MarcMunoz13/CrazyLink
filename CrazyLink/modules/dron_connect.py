import math
import threading
import logging
import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.crazyflie.log import LogConfig

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

def _connect(self, uri=URI, callback=None, params=None):
    cflib.crtp.init_drivers()

    try:
        self.cf = Crazyflie(rw_cache='./cache')
        self.scf = SyncCrazyflie(uri, cf=self.cf)
        self.scf.open_link()


        self.state = "connected"
        print(" Conectado con Crazyflie")

        self.pc = None

        self.pc = PositionHlCommander(
            self.scf,
            x=0.0, y=0.0, z=0.0,
            default_height=0.5,
            default_velocity=0.5,  # velocidad de vuelo en m/s
            default_landing_height=0.0,
            controller=PositionHlCommander.CONTROLLER_PID  # usa controlador PID
        )
        print(" PositionHlCommander listo ")


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
        self.state = "disconnected"
        print(f"Error al conectar con Crazyflie: {e}")








def connect(self,
            uri=URI,
            freq=4,
            blocking=True,
            callback=None,
            params=None
            ):
    if self.state == 'disconnected':
        self.frequency = freq
        if blocking:
            self._connect(uri, callback, params)
        else:
            connectThread = threading.Thread(target=self._connect, args=[uri, callback, params])
            connectThread.start()
        return True
    else:
        return False


def disconnect(self):
    if self.state == 'connected':
        self.state = "disconnected"
        time.sleep(0.2)
        #detengo telemetría
        try:
            if hasattr(self, '_pos_log'):
                self.stop_local_telemetry()
        except Exception:
            pass
        # Cierra commander si existía
        if getattr(self, 'pc', None) is not None:
            try:
                self.pc.__exit__(None, None, None)
            except Exception:
                pass
            self.pc = None

        try:
            self.scf.close_link()
        except Exception:
            pass
        print("Desconectado de Crazyflie")
        return True
    else:
        return False