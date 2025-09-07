import threading
import time

try:
    import pygame
    _HAS_PYGAME = True
except Exception:
    _HAS_PYGAME = False


def _joy_loop(self):
    dt = 0.02  # ~50 Hz
    print("[joy] loop iniciado")

    try:
        if not _HAS_PYGAME:
            raise RuntimeError("pygame no está instalado (pip install pygame)")
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            raise RuntimeError("No se detectó ningún joystick.")
        js = pygame.joystick.Joystick(0)
        js.init()
        print(f"[joy] usando: {js.get_name()}  (buttons={js.get_numbuttons()}  hats={js.get_numhats()})")

        prev_hat = (0, 0)

        while getattr(self, "_joy_running", False):
            for ev in pygame.event.get():
                #botones
                if ev.type == pygame.JOYBUTTONDOWN:
                    b = ev.button
                    #Mapeo:
                    #B1 connect
                    if b == 0:
                        if self.state == "disconnected":
                            print("[joy] B0 -> connect")
                            try:
                                self.connect(blocking=True)
                            except Exception as e:
                                print(f"[joy] connect fallo: {e}")

                    #B2 takeoff
                    elif b == 1:
                        if self.state == "connected":
                            print("[joy] B1 -> takeoff 0.5")
                            try:
                                self.takeOff(0.5, blocking=True)
                            except Exception as e:
                                print(f"[joy] takeoff fallo: {e}")

                    #B3 RTL
                    elif b == 2:
                        if self.state == "flying":
                            print("[joy] B2 -> RTL/Land")
                            try:
                                self.Land(blocking=False)
                            except Exception as e:
                                print(f"[joy] land fallo: {e}")

                    #B4 disconnect
                    elif b == 3:
                        print("[joy] B3 -> disconnect")
                        try:
                            if self.state == "flying":
                                self.Land(blocking=True)
                            try:
                                self.disable_local_geofence()
                            except Exception:
                                pass
                            self.disconnect()
                        except Exception as e:
                            print(f"[joy] disconnect fallo: {e}")
                        self._joy_running = False

                    #L1 subir +0.5
                    elif b == 4:
                        if self.state == "flying":
                            print("[joy] B4 -> subir +0.5")
                            try:
                                self.go('Up')
                            except Exception as e:
                                print(f"[joy] subir fallo: {e}")

                    #R1 bajar -0.5
                    elif b == 5:
                        if self.state == "flying":
                            print("[joy] B5 -> bajar -0.5")
                            try:
                                self.go('Down')
                            except Exception as e:
                                print(f"[joy] bajar fallo: {e}")

                # HAT cruz
                elif ev.type == pygame.JOYHATMOTION and ev.hat == 0:
                    curr = ev.value
                    if curr != prev_hat:
                        x, y = curr
                        #actua en cambios diferentes de (0,0) y si está volando
                        if self.state == "flying" and curr != (0, 0):
                            #y=+1 => adelante (X+) => 'North'
                            if y == 1:
                                print("[joy] HAT up -> North (X+)")
                                try: self.go('North')
                                except Exception as e: print(f"[joy] go North fallo: {e}")
                            # y=-1 => atrás (X-) => 'South'
                            if y == -1:
                                print("[joy] HAT down -> South (X-)")
                                try: self.go('South')
                                except Exception as e: print(f"[joy] go South fallo: {e}")
                            # x=+1 => derecha (Y+) => 'East'
                            if x == 1:
                                print("[joy] HAT right -> East (Y+)")
                                try: self.go('East')
                                except Exception as e: print(f"[joy] go East fallo: {e}")
                            # x=-1 => izquierda (Y-) => 'West'
                            if x == -1:
                                print("[joy] HAT left -> West (Y-)")
                                try: self.go('West')
                                except Exception as e: print(f"[joy] go West fallo: {e}")

                        prev_hat = curr

            time.sleep(dt)

    except Exception as e:
        print(f"[joy] error: {e}")

    finally:
        print("[joy] loop terminado")
        try:
            if 'js' in locals():
                js.quit()
        except Exception:
            pass
        try:
            pygame.joystick.quit()
            pygame.quit()
        except Exception:
            pass


def start_joystick(self):
    """Arranca el control por joystick (botones + HAT en pasos de 0.5m)."""
    if getattr(self, "_joy_running", False):
        print("[joy] ya estaba activo")
        return False
    self._joy_running = True
    t = threading.Thread(target=_joy_loop, args=(self,), daemon=True)
    self._joy_thread = t
    t.start()
    print("[joy] iniciado")
    return True


def stop_joystick(self):
    """Detiene el control por joystick (no hace land)."""
    if not getattr(self, "_joy_running", False):
        print("[joy] no estaba activo")
        return False
    self._joy_running = False
    try:
        t = getattr(self, "_joy_thread", None)
        import threading as _th
        if t is not None and _th.current_thread() is not t:
            t.join(timeout=1.5)
    except Exception:
        pass
    self._joy_thread = None
    return True