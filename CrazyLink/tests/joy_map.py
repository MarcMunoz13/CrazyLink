import time
import pygame

STEP = 0.5  # metros por pulsación de la cruceta

def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No hay joysticks conectados.")
        return

    js = pygame.joystick.Joystick(0)
    js.init()
    print(f"Usando: {js.get_name()} | buttons={js.get_numbuttons()} hats={js.get_numhats()}")
    print("""
Mapeo:
  B1 -> connect
  B2 -> takeoff
  B3 -> rtl
  B4 -> disconnect
  L1 -> subir (+0.5 m)
  R1 -> bajar (-0.5 m)
  HAT-0 (x,y): x=-1 izq / +1 der (ΔY) | y=+1 adelante (X+) / -1 atrás (X-)
--- Demo en marcha (Ctrl+C para salir) ---
""")

    try:
        while True:
            for e in pygame.event.get():
                if e.type == pygame.JOYBUTTONDOWN:
                    i = e.button
                    if   i == 0: print("B1 -> CONNECT")
                    elif i == 1: print("B2 -> TAKEOFF")
                    elif i == 2: print("B3 -> RTL")
                    elif i == 3: print("B4 -> DISCONNECT")
                    elif i == 4: print("L1 -> SUBIR (+0.5 m)")
                    elif i == 5: print("R1 -> BAJAR (-0.5 m)")
                    else:        print(f"B{i} DOWN (ignorado)")

                elif e.type == pygame.JOYHATMOTION and e.hat == 0:
                    x, y = e.value
                    if (x, y) != (0, 0):
                        dY = STEP * (1 if x > 0 else -1 if x < 0 else 0)
                        dX = STEP * (1 if y > 0 else -1 if y < 0 else 0)
                        dir_txt = []
                        if y ==  1: dir_txt.append("adelante (X+)")
                        if y == -1: dir_txt.append("atrás (X-)")
                        if x ==  1: dir_txt.append("derecha (Y+)")
                        if x == -1: dir_txt.append("izquierda (Y-)")
                        print(f"HAT0 {x:+d},{y:+d} -> ΔX={dX:+.1f}  ΔY={dY:+.1f}  [{', '.join(dir_txt)}]")
                    else:
                        print("HAT0 (0,0) neutro")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Saliendo...")

    finally:
        try: js.quit()
        except Exception: pass
        pygame.joystick.quit()
        pygame.quit()

if __name__ == "__main__":
    main()