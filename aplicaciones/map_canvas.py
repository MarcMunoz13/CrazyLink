import tkinter as tk
from PIL import Image, ImageTk
import time
from tkinter import messagebox, simpledialog
import threading


class MapCanvas:
    def __init__(self, parent, dron, size_pixels=600):

        self.dron = dron

        # vista de +/-5m ejes
        self.view_max_x = 5.0
        self.view_max_y = 5.0
        self.size = size_pixels

        ##Hago lista de waypoints, cada uno guarda valor X, Y, Z, Delay y marker_id
        self._waypoints = []  # almaceno waypoints
        self._planning = False  # flag para cuando entro en planificación de misión
        self.window = tk.Toplevel(parent)
        self.window.title("Mapa del Dron")
        self.window.geometry(f"{self.size}x{self.size + 40}")
        self.window.resizable(True, True)
        self._wp_line_id = None

        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        ###-------- Botonera superior------
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(side="top", fill="x")

        self.mission_btn = tk.Button(
            btn_frame, text="Misión", bg="dark orange",
            command=self._on_mission_button
        )
        self.mission_btn.pack(side="left", padx=5, pady=5)

        self.clear_btn = tk.Button(
            btn_frame, text="Limpiar misión", bg="light grey",
            command=self._clear_mission
        )
        self.clear_btn.pack(side="left", padx=5, pady=5)


        self.speed_var = tk.DoubleVar(value=getattr(self.dron, "move_speed", 0.5))
        self.speed_scale = tk.Scale(
            btn_frame,
            from_=0.1, to=0.5,
            resolution=0.1,
            orient="horizontal",
            variable=self.speed_var,
            label="Vel (m/s)",
            command=self._on_speed_changed
        )
        self.speed_scale.pack(side="left", padx=10)

        self.joy_on_btn = tk.Button(
            btn_frame, text="Joystick ON", bg="light green",
            command=self._joy_on
        )
        self.joy_on_btn.pack(side="left", padx=5, pady=5)

        self.joy_off_btn = tk.Button(
            btn_frame, text="Joystick OFF", bg="light grey",
            state="disabled",                # empieza desactivado
            command=self._joy_off
        )
        self.joy_off_btn.pack(side="left", padx=5, pady=5)

        ##############---- Genero el Canvas Gris---------

        self.canvas = tk.Canvas(
            self.window,
            width=self.size,
            height=self.size,
            bg="light grey"
        )
        self.canvas.pack(fill="both", expand=True)


        self.cx = self.size / 2
        self.cy = self.size / 2
        self.scale_x = self.size / (2 * self.view_max_x)
        self.scale_y = self.size / (2 * self.view_max_y)

        # geofence y dron
        self.geofence_rect = None
        self.drone_marker = None
        self.exclusion_poly_id = None
        self.exclusion_poly_ids = []

        # icono de dron y marker
        drone_img = Image.open("assets/drone.png").resize((20, 20), Image.LANCZOS)
        self.drone_icon = ImageTk.PhotoImage(drone_img)

        mkr_img = Image.open("assets/marker_icon.png").resize((20, 20), Image.LANCZOS)
        self.marker_icon = ImageTk.PhotoImage(mkr_img)

        # popups para el boton derecho diferenciados
        self.popup_fly = tk.Menu(self.window, tearoff=0)
        self.popup_fly.add_command(label="Volar aquí", command=self._fly_here)
        self.popup_fly.add_separator()
        self.popup_fly.add_command(
            label="Configurar geofence",
            command=self._set_geofence_from_map
        )
        self.popup_fly.add_separator()
        self.popup_fly.add_command(label="Configurar geofence de exclusión", command=self._add_exclusion_from_map)
        self.popup_fly.add_separator()
        self.popup_fly.add_command(
            label="Desactivar geofence",
            command=self._disable_geofence_from_map
        )



        # popup para planificar misión
        self.popup_mission = tk.Menu(self.window, tearoff=0)
        self.popup_mission.add_command(label="Establecer waypoint", command=self._add_waypoint)

        # bind clic derecho
        self._click_px = (0, 0)
        self.canvas.bind("<Button-3>", self._on_right_click)

        # posicion inicial de dron
        self._draw_axes()
        self.update_drone(0.0, 0.0)

    ###empiezan funciones del mapa

    def _on_mission_button(self):
        if not self._planning:
            # empiezo planificación
            self._clear_mission()
            self._planning = True
            messagebox.showinfo(
                "Planificar misión",
                "Marca los 4 waypoints con botón derecho y vuelve a clicar Misión."
            )
        else:
            # compruebo si tengo los 4 waypoints
            if len(self._waypoints) < 4:
                messagebox.showwarning(
                    "Faltan waypoints",
                    f"Has marcado {len(self._waypoints)}/4 waypoints.\n"
                    "Sigue marcando hasta completar."
                )
            else:
                # lanzo la misión al volver a clicar
                self._planning = False

                puntos = [(x, y, z, delay) for (x, y, z, delay, *_rest) in self._waypoints]

                # Llama a la función común del módulo, con Land + callback de fin
                self.dron.run_mission_points(
                    puntos,
                    do_land=True,
                    on_finish=self._on_mission_complete
                )


    def _on_speed_changed(self, val):
        try:
            sp = round(float(val), 2)
        except Exception:
            return
        # clamp por seguridad
        sp = max(0.1, min(0.5, sp))
        self.dron.move_speed = sp
        # (opcional) reflejar redondeo/clamp en el propio slider
        if abs(self.speed_var.get() - sp) > 1e-6:
            self.speed_var.set(sp)

    def _on_right_click(self, event):
        # guardo posicion de click
        self._click_px = (event.x, event.y)
        # seleccino el menú de modo misión
        if self._planning:
            self.popup_mission.tk_popup(event.x_root, event.y_root)
        else:
            self.popup_fly.tk_popup(event.x_root, event.y_root)

    ##-----mét_odo para recoger los datos necesarios de altura y delay que usaré para definir los WP
    def _ask_alt_delay(self):
        dlg = tk.Toplevel(self.window)
        dlg.title("Parámetros Waypoint")
        dlg.transient(self.window)
        dlg.grab_set()

        tk.Label(dlg, text="Altitud (m ≥ 0.5):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        alt_entry = tk.Entry(dlg)
        alt_entry.insert(0, "0.5")
        alt_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dlg, text="Delay (s ≥ 0):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        delay_entry = tk.Entry(dlg)
        delay_entry.insert(0, "1.0")
        delay_entry.grid(row=1, column=1, padx=5, pady=5)

        result = {"z": None, "delay": None}

        def on_ok():
            try:
                z = float(alt_entry.get())
                delay = float(delay_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Ambos valores deben ser numéricos.")
                return
            if z < 0.5:
                messagebox.showerror("Error", "Altitud debe ser ≥ 0.5 m.")
                return
            if delay < 0:
                messagebox.showerror("Error", "Delay debe ser ≥ 0 s.")
                return
            result["z"], result["delay"] = z, delay
            dlg.destroy()

        def on_cancel():
            dlg.destroy()

        btn_frame = tk.Frame(dlg)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))

        tk.Button(btn_frame, text="OK", width=8, command=on_ok).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancelar", width=8, command=on_cancel).pack(side="right", padx=5)

        self.window.wait_window(dlg)
        if result["z"] is None:
            return None
        return result["z"], result["delay"]

    ##funcion para crear los waypoints
    def _add_waypoint(self):
        if len(self._waypoints) >= 4:
            messagebox.showwarning("Waypoints", "Ya has marcado 4 waypoints.")
            return

        px, py = self._click_px
        x = (px - self.cx) / self.scale_x
        y = (self.cy - py) / self.scale_y

        params = self._ask_alt_delay()
        if not params:
            return
        z, delay = params

        idx = len(self._waypoints) + 1

        marker_id = self.canvas.create_image(px, py, image=self.marker_icon, anchor="center")
        # etiqueta numérica encima del icono
        label_id = self.canvas.create_text(px, py - 14, text=str(idx),
                                           font=("Arial", 10, "bold"))
        self._waypoints.append((x, y, z, delay, marker_id, label_id))


        if len(self._waypoints) == 4:
            messagebox.showinfo(
                "Waypoints OK",
                "Has marcado los 4 waypoints.\nPulsa 'Misión' para ejecutar."
            )

        self._redraw_wp_path()

    def _redraw_wp_path(self):
        # borra la polilínea anterior si existe
        if self._wp_line_id:
            try:
                self.canvas.delete(self._wp_line_id)
            except Exception:
                pass
            self._wp_line_id = None

        if len(self._waypoints) >= 2:
            coords = []
            for (x, y, *_rest) in self._waypoints:
                px, py = self._to_canvas(x, y)
                coords.extend([px, py])
            # línea discontinua que une los WPs en orden
            self._wp_line_id = self.canvas.create_line(*coords, dash=(4, 2), width=2)

    def _clear_mission(self):
        # Cada wp es (x, y, z, delay, marker_id, label_id)
        for wp in self._waypoints:
            try:
                self.canvas.delete(wp[4])  # marker_id
            except Exception:
                pass
            try:
                self.canvas.delete(wp[5])  # label_id
            except Exception:
                pass

        self._waypoints.clear()

        # borra la polilínea si existía
        if self._wp_line_id:
            try:
                self.canvas.delete(self._wp_line_id)
            except Exception:
                pass
            self._wp_line_id = None

        self._planning = False


    def _on_mission_complete(self, *args):
        messagebox.showinfo("Misión", "Misión completada!")
        # limpiamos todo y salimos de planificacion
        self._clear_mission()
        self._planning = False

    ## funcion para "volar aquí" pidiendo altura
    def _fly_here(self):
        px, py = self._click_px
        x = (px - self.cx) / self.scale_x
        y = (self.cy - py) / self.scale_y

        # pido altura, mínima y por defecto 0.5m
        z = simpledialog.askfloat(
            "Volar aquí: Altitud",
            "Introduce altitud (m) (≥ 0.5):",
            initialvalue=0.5,
            minvalue=0.5)

        if z is None:
            return

        #mando el goto, que ya comprueba si estoy volando
        self.dron.goto(x, y, z, blocking=False)



    ##aqui definimos el geofence des del mapa
    def _set_geofence_from_map(self):
        # pido valores absolutos para ±X y ±Y, y Zmax
        try:
            xabs = simpledialog.askfloat(
                "Geofence", "Xabs (m):",
                initialvalue=3.0, minvalue=0.1, parent=self.window
            )
            if xabs is None:
                return

            yabs = simpledialog.askfloat(
                "Geofence", "Yabs(m):",
                initialvalue=3.0, minvalue=0.1, parent=self.window
            )
            if yabs is None:
                return

            zmax = simpledialog.askfloat(
                "Geofence", "Zmax (m):",
                initialvalue=10.0, minvalue=0.1, parent=self.window
            )
            if zmax is None:
                return
        except Exception:
            messagebox.showerror("Geofence", "Valores no válidos.")
            return

        # Activamos la geofence con modulo
        try:
            self.dron.set_local_geofence(xabs, yabs, zmax)
        except Exception as e:
            messagebox.showerror("Geofence", f"Error al activar geofence: {e}")
            return

        # dibujamos geofence en el mapa
        self.draw_geofence(xabs, yabs)

        # Si tienes polígonos de exclusión definidos, los re-dibujamos también
        try:
            self.draw_exclusions(self.dron.get_exclusion_polys())
        except Exception:
            pass

        messagebox.showinfo(
            "Geofence",
            f"Geofence activada:\nX ∈ [−{xabs}, +{xabs}] m\nY ∈ [−{yabs}, +{yabs}] m\nZ ≤ {zmax} m"
        )

    def _add_exclusion_from_map(self):
        # requiere geofence de inclusión activa
        if not getattr(self.dron, "_gf_enabled", False):
            messagebox.showerror("Geofence", "Primero activa la geofence de inclusión.")
            return

        # punto clicado = esquina inferior izquierda
        px, py = self._click_px
        x0 = (px - self.cx) / self.scale_x
        y0 = (self.cy - py) / self.scale_y

        try:
            sx = simpledialog.askfloat(
                "Geofence de exclusión", "Tamaño X (m):",
                initialvalue=0.5, minvalue=0.1, parent=self.window
            )
            if sx is None: return
            sy = simpledialog.askfloat(
                "Geofence de exclusión", "Tamaño Y (m):",
                initialvalue=0.5, minvalue=0.1, parent=self.window
            )
            if sy is None: return
        except Exception:
            messagebox.showerror("Geofence", "Valores no válidos.")
            return

        # registra en el dron y dibuja
        poly = self.dron.add_exclusion_rect(x0, y0, sx, sy)
        self._draw_one_exclusion(poly)
        messagebox.showinfo("Geofence", "Exclusión añadida.")

    def _draw_one_exclusion(self, poly_points):
        coords = []
        for x, y in poly_points:
            px, py = self._to_canvas(x, y)
            coords += [px, py]
        pid = self.canvas.create_polygon(*coords, outline="blue", fill="", width=2)
        self.exclusion_poly_ids.append(pid)

    def draw_exclusions(self, polys):
        # borra dibujos anteriores y pinta todos
        for pid in self.exclusion_poly_ids:
            self.canvas.delete(pid)
        self.exclusion_poly_ids.clear()
        for poly in polys:
            self._draw_one_exclusion(poly)

    def clear_geofence(self):
        if self.geofence_rect:
            self.canvas.delete(self.geofence_rect)
            self.geofence_rect = None
        # limpia TODAS las exclusiones dibujadas
        for pid in self.exclusion_poly_ids:
            self.canvas.delete(pid)
        self.exclusion_poly_ids.clear()

    def _disable_geofence_from_map(self):
        if not hasattr(self.dron, '_gf_monitor'):
            messagebox.showerror("Geofence", "No hay una geofence activo.")
            return
        try:
            self.dron.disable_local_geofence()
        except Exception as e:
            messagebox.showerror("Geofence", f"No se pudo desactivar: {e}")
            return

        # borra todos los dibujos de geofence
        self.clear_geofence()
        messagebox.showinfo("Geofence", "Geofence desactivada.")

    def _draw_axes(self):
        self.canvas.create_line(0, self.cy, self.size, self.cy)
        self.canvas.create_line(self.cx, 0, self.cx, self.size)
        step = 0.5
        nx = int(self.view_max_x / step)
        ny = int(self.view_max_y / step)

        # eje X
        for i in range(-ny, ny + 1):
            ym = i * step
            px = self.cx + ym * self.scale_x
            self.canvas.create_line(px, self.cy - 5, px, self.cy + 5)
            lbl = f"{ym:.1f}" if ym % 1 else f"{int(ym)}"
            self.canvas.create_text(px, self.size - 10, text=lbl)

        # eje Y
        for i in range(-nx, nx + 1):
            xm = i * step
            py = self.cy - xm * self.scale_y
            self.canvas.create_line(self.cx - 5, py, self.cx + 5, py)
            lbl = f"{xm:.1f}" if xm % 1 else f"{int(xm)}"
            self.canvas.create_text(10, py, text=lbl, anchor="w")

    def _to_canvas(self, x, y):
        px = self.cx + x * self.scale_x
        py = self.cy - y * self.scale_y
        return px, py

    def update_drone(self, x, y):
        px, py = self._to_canvas(x, y)
        if self.drone_marker:
            self.canvas.delete(self.drone_marker)
        self.drone_marker = self.canvas.create_image(
            px, py, image=self.drone_icon, anchor="center"
        )

    ## geofence de inclusión en rojo
    def draw_geofence(self, max_x, max_y):
        if self.geofence_rect:
            self.canvas.delete(self.geofence_rect)
        p1 = self._to_canvas(-max_x, -max_y)
        p2 = self._to_canvas(max_x, max_y)
        self.geofence_rect = self.canvas.create_rectangle(
            p1[0], p1[1], p2[0], p2[1],
            outline="red", width=2
        )

    # geofence de exclusión en azul
    def draw_exclusion(self, poly_points):
        if self.exclusion_poly_id:
            self.canvas.delete(self.exclusion_poly_id)
        coords = []
        for x, y in poly_points:
            px, py = self._to_canvas(x, y)
            coords += [px, py]
        self.exclusion_poly_id = self.canvas.create_polygon(
            *coords, outline="blue", fill="", width=2
        )

    def _joy_on(self):
        try:
            # Arranca el hilo del joystick
            ok = getattr(self.dron, "start_joystick", None)
            if not (callable(ok) and self.dron.start_joystick()):
                messagebox.showerror("Joystick", "No se pudo iniciar el joystick.")
                return

            # Si ya está conectado, inicia telemetría; si no, la enganchamos cuando conecte
            def ensure_telemetry():
                # Ya activa -> salimos
                if hasattr(self.dron, "_pos_log"):
                    return
                # Si está conectado y tiene cf, arrancamos
                if self.dron.state == "connected" and hasattr(self.dron, "cf"):
                    try:
                        self.dron.start_position_stream(self._telemetry_to_map, period_in_ms=100)
                    except Exception as e:
                        print(f"[joy] No pude iniciar telemetría: {e}")
                    return
                # Reintenta mientras el modo joystick siga activo
                if getattr(self.dron, "_joy_running", False):
                    self.window.after(300, ensure_telemetry)

            ensure_telemetry()

            self.joy_on_btn.configure(state="disabled", bg="light grey")
            self.joy_off_btn.configure(state="normal", bg="tomato")
            messagebox.showinfo(
                "Joystick",
                "Joystick ACTIVADO.\n\nMapeo:\n"
                "B1: connect | B2: takeoff | B3: RTL | B4: disconnect\n"
                "L1: subir (+0.5 m) | R1: bajar (-0.5 m)\n"
                "Cruces: ↑ X+ (North), ↓ X- (South), → Y+ (East), ← Y- (West)"
            )
        except Exception as e:
            messagebox.showerror("Joystick", f"No se pudo iniciar: {e}")

    def _joy_off(self):
        try:
            ok = getattr(self.dron, "stop_joystick", None)
            if callable(ok) and self.dron.stop_joystick():
                # UI: reactivo slider y botones
                #try:
                #    self.speed_scale.configure(state="normal")
                #except Exception:
                #    pass
                self.joy_on_btn.configure(state="normal", bg="light green")
                self.joy_off_btn.configure(state="disabled", bg="light grey")
                messagebox.showinfo("Joystick", "Joystick DESACTIVADO.")
            else:
                messagebox.showwarning("Joystick", "El joystick no estaba activo.")
        except Exception as e:
            messagebox.showerror("Joystick", f"No se pudo detener: {e}")

    def _on_close(self):
        # intenta apagar joystick si quedó activo
        try:
            if getattr(self.dron, "_joy_running", False):
                self.dron.stop_joystick()
        except Exception:
            pass
        self.window.destroy()

    def _telemetry_to_map(self, x, y, z):
        # actualizar el dibujo del dron en el hilo de Tk
        self.window.after(0, lambda: self.update_drone(x, y))