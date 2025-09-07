import threading
import time

##miro si x,y está dentro del poligono definido
def _point_in_poly(x, y, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside



def set_local_geofence(self, max_x, max_y, max_z, poll_interval=0.1):
    self._gf_limits = {
        'max_x': float(max_x),
        'max_y': float(max_y),
        'max_z': float(max_z),
    }



    #lista de poligonos de exclusion
    if not hasattr(self, '_gf_exclusion_polys'):
        self._gf_exclusion_polys = []
    self._gf_enabled = True
    self._gf_monitoring = True

    def _monitor():
        while self._gf_monitoring:
            if self.state == 'flying':
                x, y, z = getattr(self, 'x', None), getattr(self, 'y', None), getattr(self, 'z', None)
                if None in (x, y, z):
                    time.sleep(poll_interval)
                    continue

                #compruebo geofence de inclusion
                if (abs(x) > self._gf_limits['max_x'] or
                    abs(y) > self._gf_limits['max_y'] or
                    z       > self._gf_limits['max_z']):
                    print("Geofence de inclusión excedido. Aterrizando.")
                    #desactivo el geofence
                    self._gf_monitoring = False
                    try:
                        self.Land(blocking= True)
                    except Exception as e:
                        print(f"Error Aterrizando por geofence de inclusión: {e}")
                    break

                #compruebo geofences de exclusion
                try:
                    polys = list(self._gf_exclusion_polys)
                except Exception:
                    polys = []
                for poly in polys:
                    if _point_in_poly(x, y, poly):
                        print("Geofence de exclusión violada. Aterrizando.")
                        self._gf_monitoring = False
                        try:
                            self.Land(blocking=True)
                        except Exception as e:
                            print(f"Error Aterrizando por geofence de exclusión: {e}")
                        polys = None
                        break



            time.sleep(poll_interval)

    t = threading.Thread(target=_monitor, daemon=True)
    t.start()
    self._gf_monitor = t

#aqui acabo con el geofence
def disable_local_geofence(self):
    self._gf_enabled = False
    self._gf_monitoring = False
    if hasattr(self, '_gf_monitor'):
        self._gf_monitor.join(timeout=1)
        del self._gf_monitor
    print("Geofence desactivada.")

########---------EXCLUSIONES MULTIPLES-------------------########

def add_exclusion_rect(self, x_min, y_min, size_x, size_y):
    #añade rectangulo de exclusión centrado en (x_min, y_min) con tamaño (size_x, size_y)
    if not hasattr(self, '_gf_exclusion_polys'):
        self._gf_exclusion_polys = []
    sx = abs(float(size_x)); sy = abs(float(size_y))
    x0, y0 = float(x_min), float(y_min)
    x1, y1 = x0 + sx, y0 + sy
    poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    self._gf_exclusion_polys.append(poly)
    return poly

def add_exclusion_poly(self, points):
    #añado exclusión de polígono
    if not hasattr(self, '_gf_exclusion_polys'):
        self._gf_exclusion_polys = []
    self._gf_exclusion_polys.append(list(points))
    return points

def get_exclusion_polys(self):
    return list(getattr(self, '_gf_exclusion_polys', []))

def clear_exclusions(self):
    self._gf_exclusion_polys = []