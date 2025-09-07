import json
import tkinter as tk
#from CrazyLink.Dron_1 import Dron
from CrazyLink.Dron_1 import Dron
import random
import paho.mqtt.client as mqtt
import tkinter.messagebox as mb

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper
from map_canvas import MapCanvas




def update_position(x, y, z):
    pos_label.config(text=f"X: {x:.2f}   Y: {y:.2f}   Z: {z:.2f}")
    if 'map_canvas' in globals() and map_canvas is not None:
        map_canvas.update_drone(x, y)

def allowExternal ():
    global client
    clientName = "demoDash" + str(random.randint(1000, 9000))
    client = mqtt.Client(clientName, transport="websockets")

    broker_address = 'broker.hivemq.com'
    broker_port = 8000

    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(broker_address, broker_port)
    print('Conectado a broker.hivemq.com:8000')

    # me subscribo a cualquier mensaje  que venga del mobileFlask
    client.subscribe('mobileFlask/demoDash/#')
    print('demoDash esperando peticiones ')
    client.loop_start()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK Returned code=", rc)
    else:
        print("Bad connection Returned code=", rc)




def publish_event ( event):
    # publico en el broker el evento, que en este caso será 'flying' porque es el único que se
    # considera en esta aplicación
    print ('en el aire')
    client.publish('demoDash/mobileFlask/'+event)



# aqui recibimos los mensajes de la web app
def on_message(client, userdata, message):
        global dron

        parts = message.topic.split ('/')
        command = parts[2]
        print ('recibo ', command)
        if command == 'connect':
            dron.connect(uri="radio://0/80/2M/E7E7E7E7E7", callback=None, params=None)
            print('conectado')
            dron.start_position_stream(update_position, period_in_ms=200)


        if command == 'arm_takeOff':
            if dron.state == 'connected':
                # recupero la altura a alcanzar, que viene como payload del mensaje
                alt = int( message.payload.decode("utf-8"))
                # operación no bloqueante. Cuando acabe publicará el evento correspondiente
                dron.takeOff(alt, blocking=False, callback=publish_event, params='flying')

        if command == 'go':
            if dron.state == 'flying':
                direction = message.payload.decode("utf-8")
                print ('vamos al: ', direction)
                dron.go(direction)

        if command == 'Land':
            if dron.state == 'flying':
                print ('voy a aterrizar')
                # operación no bloqueante
                dron.Land(blocking=False)


def on_goto():
    try:
        x = float(x_entry.get())
        y = float(y_entry.get())
        z = float(z_entry.get())
    except:
        mb.showerror("Error", "Datos no válidos")
        return
    if z < 0.5:
        mb.showerror("Error", "Z debe ser ≥ 0.5 m")
        return
    if dron.state != 'flying' and x == 0 and y == 0 and z == 0:
        mb.showerror("Error", "Datos no válidos")
        return

    dron.goto(x, y, z, blocking=False, callback=lambda: mb.showinfo("Info", "¡Ya estoy aquí!"))



def toggle_geofence():
    if gf_enabled.get():
        try:
            mx = float(max_x_var.get())
            my = float(max_y_var.get())
            mz = float(max_z_var.get())
        except ValueError:
            mb.showerror("Error", "Geofence: valores no válidos")
            gf_enabled.set(False)
            return
        dron.set_local_geofence(mx, my, mz)
        print(f"Geofence Activada: x±{mx}, y±{my}, z≤{mz}")


        if 'map_canvas' in globals() and map_canvas is not None:
            map_canvas.draw_geofence(mx, my)
            map_canvas.draw_exclusions(dron.get_exclusion_polys())
    else:
        dron.disable_local_geofence()
        print("Geofence OFF")
        if 'map_canvas' in globals() and map_canvas is not None:
            map_canvas.clear_geofence()


def open_map():
    global map_canvas
    if 'map_canvas' not in globals() or map_canvas is None:
        map_canvas = MapCanvas(ventana, dron, size_pixels=600)

    # Si la geofence está activada, dibujamos su contorno en rojo
    if gf_enabled.get():
        mx = float(max_x_var.get())
        my = float(max_y_var.get())
        map_canvas.draw_geofence(mx, my)
        map_canvas.draw_exclusions(dron.get_exclusion_polys())






dron = Dron()



ventana = tk.Tk()
ventana.geometry ('600x600')
ventana.title("Estación de Tierra del Crazyflie")

##Valores predeterminados de la geofence
gf_enabled = tk.BooleanVar(value=False)
max_x_var = tk.StringVar(value="10")
max_y_var = tk.StringVar(value="10")
max_z_var = tk.StringVar(value="10")


dron._tk_root = ventana

###########------------ TAMAÑO DE LA GEOFENCE-------------------#####################
#dron.set_local_geofence(max_x=20, max_y=20, max_z=20)


# La interfaz tiene 13 filas y una columna

for i in range(20):
    ventana.rowconfigure(i, weight=1)
ventana.columnconfigure(0, weight=1)
ventana.columnconfigure(1, weight=1)



############--------Columna 0-------------------------------
connectBtn = tk.Button(ventana, text="Conectar", bg="dark orange", command = lambda: (dron.connect(uri="radio://0/80/2M/E7E7E7E7E7"), dron.start_position_stream(update_position, period_in_ms=200)))
connectBtn.grid(row=0, column=0, padx=3, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

takeOffBtn = tk.Button(ventana, text="Despegar", bg="dark orange", command=lambda: dron.takeOff(0.5))
takeOffBtn.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

NorthBtn = tk.Button(ventana, text="Avanza", bg="dark orange", command=lambda: dron.go('North'))
NorthBtn.grid(row=2, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

SouthBtn = tk.Button(ventana, text="Retrocede", bg="dark orange", command=lambda: dron.go('South'))
SouthBtn.grid(row=3, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

EastBtn = tk.Button(ventana, text="Derecha", bg="dark orange", command=lambda: dron.go('East'))
EastBtn.grid(row=4, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

WestBtn = tk.Button(ventana, text="Izquierda", bg="dark orange", command=lambda: dron.go('West'))
WestBtn.grid(row=5, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

UpBtn = tk.Button(ventana, text="Sube", bg="dark orange", command=lambda: dron.go('Up'))
UpBtn.grid(row=6, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

DwnBtn = tk.Button(ventana, text="Baja", bg="dark orange", command=lambda: dron.go('Down'))
DwnBtn.grid(row=7, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

StopBtn = tk.Button(ventana, text="Para", bg="dark orange", command=lambda: dron.go('Stop'))
StopBtn.grid(row=8, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

RTLBtn = tk.Button(ventana, text="Land", bg="dark orange", command=lambda: dron.Land(blocking=False))
RTLBtn.grid(row=9, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

disconnectBtn = tk.Button(ventana, text="Desconectar", bg="dark orange", command=lambda: (dron.disable_local_geofence(), dron.disconnect()))
disconnectBtn.grid(row=10, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

tk.Label(ventana, text="X destino (m):").grid(row=11, column=0, sticky="w", padx=5)
x_entry = tk.Entry(ventana); x_entry.grid(row=12, column=0, sticky="we", padx=5)

tk.Label(ventana, text="Y destino (m):").grid(row=13, column=0, sticky="w", padx=5)
y_entry = tk.Entry(ventana); y_entry.grid(row=14, column=0, sticky="we", padx=5)

tk.Label(ventana, text="Z destino (m):").grid(row=15, column=0, sticky="w", padx=5)
z_entry = tk.Entry(ventana); z_entry.grid(row=16, column=0, sticky="we", padx=5)

gotoBtn = tk.Button(ventana, text="Ir a coordenadas", bg="dark orange", command=on_goto)
gotoBtn.grid(row=17, column=0, padx=5, pady=10, sticky="we")

pos_label = tk.Label(ventana, text="X: –  Y: –  Z: –", font=("Arial", 14))
pos_label.grid(row=18, column=0, pady=10)

#####################---------------Columna 1----------------
# Geofence
tk.Checkbutton(ventana, text="Activar Geofence", variable=gf_enabled, command=toggle_geofence).grid(row=0, column=1, sticky="w", padx=5)
tk.Label(ventana, text="Max X (m):").grid(row=1, column=1, sticky="w", padx=5)
tk.Entry(ventana, textvariable=max_x_var).grid(row=2, column=1, sticky="we", padx=5)
tk.Label(ventana, text="Max Y (m):").grid(row=3, column=1, sticky="w", padx=5)
tk.Entry(ventana, textvariable=max_y_var).grid(row=4, column=1, sticky="we", padx=5)
tk.Label(ventana, text="Max Z (m):").grid(row=5, column=1, sticky="w", padx=5)
tk.Entry(ventana, textvariable=max_z_var).grid(row=6, column=1, sticky="we", padx=5)

##mapa
mapBtn = tk.Button(ventana, text="Abrir mapa", bg="dark orange", command=open_map)  # CAMBIO
mapBtn.grid(row=7, column=1, padx=5, pady=5, sticky=tk.W+tk.E)

######MISSION

wp_entries = []
for i in range(4):
    # Un frame por fila de entradas
    frame = tk.Frame(ventana)
    frame.grid(row=8+i, column=1, padx=5, pady=2, sticky="we")
    # X
    tk.Label(frame, text=f"WP{i+1} X:").grid(row=0, column=0)
    ex = tk.Entry(frame, width=5); ex.grid(row=0, column=1)
    # Y
    tk.Label(frame, text="Y:").grid(row=0, column=2)
    ey = tk.Entry(frame, width=5); ey.grid(row=0, column=3)
    # Z
    tk.Label(frame, text="Z:").grid(row=0, column=4)
    ez = tk.Entry(frame, width=5); ez.grid(row=0, column=5)
    # Delay
    tk.Label(frame, text="Delay:").grid(row=0, column=6)
    ed = tk.Entry(frame, width=5); ed.grid(row=0, column=7)

    wp_entries.append((ex, ey, ez, ed))


# Botón para lanzar la misión
missionBtn = tk.Button(ventana, text="Hacer misión", bg="dark orange", command=lambda: dron.start_mission(wp_entries))
missionBtn.grid(row=12, column=1, padx=5, pady=10, sticky="we")








##### Código para la recepción de peticiones a través de MQTT

'''client.on_message = on_message
client.on_connect = on_connect
client.connect(broker_address, broker_port)
print('Conectado a broker.hivemq.com:8000')

# me subscribo a cualquier mensaje  que venga del mobileFlask
client.subscribe('mobileFlask/demoDash/#')
print('demoDash esperando peticiones ')
client.loop_start()'''

ventana.mainloop()