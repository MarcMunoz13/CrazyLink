from cflib.crazyflie.log import LogConfig

_GROUND_Z = 0.06

def _process_position(drone, user_cb, timestamp, data, logconf):
    x = data['stateEstimate.x']
    y = data['stateEstimate.y']
    z = data['stateEstimate.z']

    # Si estamos en suelo (z muy baja) y no en vuelo, fija posición a (0,0,0)
    if (z is not None) and (z < _GROUND_Z) and (drone.state in ('connected', 'landing')):
        x, y, z = 0.0, 0.0, 0.0

    drone.x, drone.y, drone.z = x, y, z
    drone._tk_root.after(0, lambda: user_cb(drone.x, drone.y, drone.z))

def start_local_telemetry(self, user_cb, period_in_ms=100):

    self._telemetry_cb = user_cb
    self._telemetry_period = period_in_ms

    log_conf = LogConfig(name='LocalPosition', period_in_ms=period_in_ms)
    log_conf.add_variable('stateEstimate.x', 'float')
    log_conf.add_variable('stateEstimate.y', 'float')
    log_conf.add_variable('stateEstimate.z', 'float')

    self._pos_log = log_conf
    self.cf.log.add_config(log_conf)

    log_conf.data_received_cb.add_callback(lambda timestamp, data, logconf: _process_position(self, user_cb, timestamp, data, logconf))
    log_conf.start()


def stop_local_telemetry(self):
    if hasattr(self, '_pos_log'):
        # Primero detengo la captura
        try:
            self._pos_log.stop()
        except Exception:
            pass
        # Intenta eliminar la configuración; si no existe, ignora
        try:
            self.cf.log.remove_config(self._pos_log)
        except AttributeError:
            pass
        # Borro la referencia
        del self._pos_log



