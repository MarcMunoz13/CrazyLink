from .modules.dron_localGeofence import set_local_geofence, disable_local_geofence, add_exclusion_poly, add_exclusion_rect, get_exclusion_polys, clear_exclusions
from .modules.dron_nav import go
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
import cflib.crtp
from .modules.dron_local_telemetry import start_local_telemetry, stop_local_telemetry, _process_position
#from .modules.dron_mission import start_mission
from .modules.dron_joystick import start_joystick, stop_joystick
from .modules.dron_mission import start_mission, run_mission_points


class Dron(object):
    def __init__(self):

        self.state = "disconnected"
        self.x = None
        self.y = None
        self.z = None
        ''' los otros estados son:
            connected
            arming
            armed
            takingOff
            flying
            returning
            landing
        '''

        self.going = False # se usa en dron_nav
        self.navSpeed = 5 # se usa en dron_nav
        self.direction = 'Stop' # se usa en dron_nav
        self.id = None


        self.step = 1 # se usa en dron_mov. Son los metros que mueve en cada paso
        self.localGeofence = None # se usa en dron_mov para evitar que el dron se salga del espacio
        self.position = [0,0,0] # se usa en dron_mov para identificar la posición del dron dentro del espacio
        self.heading = None

        ###########-------------para crazyflie----------################
        self.move_speed = 0.5


        self.go = go.__get__(self)
        self.start_local_telemetry = start_local_telemetry.__get__(self, Dron)
        self.stop_local_telemetry = stop_local_telemetry.__get__(self, Dron)
        self.start_position_stream = self.start_local_telemetry
        self.set_local_geofence = set_local_geofence.__get__(self, Dron)
        self.disable_local_geofence = disable_local_geofence.__get__(self, Dron)
        self.start_mission = start_mission.__get__(self, Dron)

        #exclusiones múltiples
        self._gf_exclusion_polys = []
        self.add_exclusion_rect     = add_exclusion_rect.__get__(self, Dron)
        self.add_exclusion_poly     = add_exclusion_poly.__get__(self, Dron)
        self.get_exclusion_polys    = get_exclusion_polys.__get__(self, Dron)
        self.clear_exclusions       = clear_exclusions.__get__(self, Dron)

        #joystick
        self._joy_running = False
        self._joy_thread  = None
        self.start_joystick = start_joystick.__get__(self, Dron)
        self.stop_joystick = stop_joystick.__get__(self, Dron)

        self.start_mission = start_mission.__get__(self, Dron)
        self.run_mission_points = run_mission_points.__get__(self, Dron)


    # aqui se importan los métodos de la clase Dron, que están organizados en ficheros.
    # Así podría orgenizarse la aportación de futuros alumnos que necesitasen incorporar nuevos servicios
    # para sus aplicaciones. Crearían un fichero con sus nuevos métodos y lo importarían aquí
    # Lo que no me gusta mucho es que si esa contribución nueva requiere de algún nuevo atributo de clase
    # ese atributo hay que declararlo aqui y no en el fichero con los métodos nuevos.
    # Ese es el caso del atributo going, que lo tengo que declarar aqui y preferiría poder declararlo en el fichero dron_goto



    from .modules.dron_connect import connect, _connect, disconnect
    from .modules.dron_takeOff import takeOff, _takeOff
    from .modules.dron_RTL_Land import  Land, _goDown
    from .modules.dron_goto import goto, _goto


