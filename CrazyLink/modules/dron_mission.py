import threading
import time
import tkinter.messagebox as mb



def run_mission_points(self, puntos, do_land=True, tol=0.1, on_finish=None):

    def _run():
        # Validación básica
        if not puntos:
            mb.showerror("Error misión", "No hay waypoints.")
            return
        _p = []
        for idx, p in enumerate(puntos, start=1):
            try:
                x, y, z, delay = map(float, p)
            except Exception:
                mb.showerror("Error misión", f"WP{idx}: datos no válidos")
                return
            if z < 0.5:
                mb.showerror("Error misión", f"WP{idx}: Z debe ser ≥ 0.5 m")
                return
            if delay < 0:
                mb.showerror("Error misión", f"WP{idx}: Delay debe ser ≥ 0")
                return
            _p.append((x, y, z, delay))

        # Despegue si es necesario
        if self.state != 'flying':
            print("Misión: Dron en tierra, despegando a 0.5 m")
            self.takeOff(0.5, blocking=True)
            time.sleep(2)

        # Recorrido
        for idx, (x, y, z, delay) in enumerate(_p, start=1):
            print(f"Misión: Yendo a WP{idx} ({x:.2f}, {y:.2f}, {z:.2f}), delay={delay}s")
            self.goto(x, y, z, blocking=False)
            # Espera llegada
            while True:
                time.sleep(0.1)
                if self.state not in ('flying', 'landing'):
                    print("Misión: dron dejó de volar")
                    return
                dx = abs(self.x - x); dy = abs(self.y - y); dz = abs(self.z - z)
                if dx < tol and dy < tol and dz < tol:
                    print(f"Misión: WP {idx} alcanzado")
                    break
            # Espera en el punto
            time.sleep(delay)

        # Fin de misión
        if do_land:
            print("Misión: vuelta a casa (Land)")
            # Pasamos el on_finish para que se ejecute al finalizar el Land
            self.Land(blocking=False, callback=(lambda *args: on_finish and on_finish()))
        else:
            if on_finish:
                on_finish()

    threading.Thread(target=_run, daemon=True).start()






##version para la estacion de tierra
def start_mission(self, wp_entries):
    def _run_mision():
        puntos = []
        # compruebo que las coordenadas sean validas
        for idx, (ex, ey, ez, ed) in enumerate(wp_entries, start=1):
            try:
                x = float(ex.get())
                y = float(ey.get())
                z = float(ez.get())
                delay = float(ed.get())
            except ValueError:
                mb.showerror("Error misión", f"WP{idx}: coordenadas no válidas")
                return
            if z < 0.5:
                mb.showerror("Error misión", f"WP{idx}: Z debe ser ≥ 0.5 m")
                return
            if delay < 0:
                mb.showerror("Error misión", f"WP{idx}: Delay debe ser ≥ 0")
                return
            puntos.append((x, y, z, delay))


        # compruebo que esté volando, y sino despegoa  0.5m
        if self.state != 'flying':
            print("Misión: Dron en tierra, iniciando despegue")
            self.takeOff(0.5, blocking=True)
            time.sleep(2)  # estabilizo

        tol = 0.2  # tolerancia en metros

        # voy a los waypoints
        for idx, (x, y, z, delay) in enumerate(puntos, start=1):
            print(f"Misión: Yendo a WP{idx} ({x:.2f}, {y:.2f}, {z:.2f}), delay={delay}s")
            self.goto(x, y, z, blocking=False)
            # esperar a la llegada
            while True:
                time.sleep(0.1)
                if self.state not in ('flying', 'landing'):
                    print("Misión: dron dejó de volar")
                    return
                dx = abs(self.x - x)
                dy = abs(self.y - y)
                dz = abs(self.z - z)
                if dx < tol and dy < tol and dz < tol:
                    print(f"Misión: WP {idx} alcanzado")
                    break

            #espero el tiempo deseado en el punto
            print(f"Misión: esperando {delay} s en WP{idx}")
            time.sleep(delay)

        # espero 3s antes de volver a casa
        print("Misión: esperando 3 s antes de volver a casa")
        time.sleep(3)



    # lanzar misión en hilo para no bloquear la UI
    threading.Thread(target=_run_mision, daemon=True).start()