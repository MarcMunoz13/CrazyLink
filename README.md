# La librería CrazyLink
CrazyLink es una librería que pretende facilitar el desarrollo de aplicaciones de control del dron. Ofrece una amplia variedad de funcionalidades y se está diseñando con la mente puesta en las posibles necesidades del Drone Engineering Ecosystem (DEE).    
En este repositorio puede encontrarse el código de la librería y varias aplicaciones que demuestran su uso, en una variedad de contextos. Es importante tener presente que CrazyLink está en desarrollo y, por tanto, no exenta de errores.
## 1. Alternativa a DronLink
En el DDE encontramos la librería DronLink, una adaptación de DroneKit creada específicamente en el ecosistema mencionado para trabajar con drones basados en ArduPilot. Sin embargo, DronLink está estrechamente ligada a esa plataforma de paquetes y no resulta compatible con el dron Crazyflie, que cuenta con un sistema de posicionamiento relativo incompatible con GPS. Esta limitación ha sido la motivación que ha impulsado la creación de una librería alternativa, orientada a la integración del Crazyflie dentro del DDE para ofrecer una experiencia de usuario similar a la de los módulos que propone DronLink.
No obstante, DronLink sigue siendo plenamente operativa y dispone de abundante documentación y ejemplos. La filosofía de la nueva librería, se basa en aprovechar los conceptos y estructuras que se han desarrollado en la librería original, sirviendo esta de inspiración y pauta que dicta la coherencia y el flujo de datos para adaptar el sistema al Crazyflie. De este modo, se facilita la transición y se asegura que tanto estudiantes como desarrolladores puedan trabajar de manera homogénea en futuros proyectos.
## 2. Modelo de programación de CrazyLink
CrazyLink está implementada en forma de clase **(la clase Dron)** con sus atributos y una
variedad de métodos para operar con el dron. La clase con los atributos está definida en el
fichero _Dron_1.py_ y los métodos están en los diferentes ficheros de la carpeta _modules_
(connect.py, takeOff.py, etc.).

Muchos de los métodos pueden activarse **de forma bloqueante o de forma no bloqueante**. En
el primer caso, **el control no se devuelve al programa que hace la llamada hasta que la
operación ordenada haya acabado**. Si la llamada es no bloqueante entonces **el control se
devuelve inmediatamente** para que el programa pueda hacer otras cosas mientras se realiza la
operación.

Un buen ejemplo de método con estas dos opciones es _takeOff_, que tiene la siguiente cabecera:

```
def takeOff(self, aTargetAltitude, blocking=True, callback=None , params = None)
```

Al llamar a este método hay que pasarle como parámetro la **altura de despegue**. Por defecto la
operación es **bloqueante**. Por tanto, el programa que hace la llamada no se reanuda hasta que 
el dron esté a la altura indicada. En el caso de usar la opción no bloqueante se puede indicar el
nombre de la función que queremos que se ejecute cuando la operación haya acabado (función a la que
llamamos habitualmente **callback**). En el caso de takeOff, cuando el dron esté a la altura indicada
se activará la función callback. Incluso podemos indicar los parámetros que queremos que
se le pasen a ese callback  en el momento en que se active. **Recuerda que self no es ningún parámetro**. 
Simplemente **indica que este es un método de una clase** (en este caso, la clase Dron).

Los siguientes ejemplos aclararán estas cuestiones.

_Ejemplo 1_

```
from Dron_1 import Dron
dron = Dron()
URI = "radio://0/80/2M/E7E7E7E7E7"
dron.connect(uri=URI, blocking=True) # me conecto al dron
print (‘Conectado’)
dron.takeOff(2.0)
print (‘En el aire a 2 metros de altura’)
```

En este ejemplo todas las llamadas son bloqueantes.

_Ejemplo 2_

```
from Dron_1 import Dron
dron = Dron()
URI = "radio://0/80/2M/E7E7E7E7E7"
dron.connect(uri=URI, blocking=True) # me conecto al dron
print (‘Conectado’)
dron.takeOff (2, blocking = False) # llamada no bloqueante, sin callback
print (‘Hago otras cosas mientras se realiza el despegue’)
```
En este caso la llamada no es bloqueante. El programa continúa su ejecución 
mientras el dron realiza el despegue. 

_Ejemplo 3_

```
from Dron_1 import Dron
dron = Dron()
URI = "radio://0/80/2M/E7E7E7E7E7"
dron.connect(uri=URI, blocking=True) # me conecto al dron
print (‘Conectado’)
    
def enAire (): # esta es la función que se activa al acabar la operación (callback)
    print (‘Por fin ya estás en el aire a 2 metros de altura’)
      
# llamada no bloqueante con callback
dron.takeOff (8, blocking = False, callback= enAire)
print (‘Hago otras cosas mientras se realiza el despegue’)
```
De nuevo una llamada no bloqueante. Pero en este caso le estamos indicando que cuando 
el dron esté a la altura indicada ejecute la función enAire, que en este caso simplemente
nos informa del evento.     
       
_Ejemplo 4_

```
from Dron import Dron
dron = Dron()
URI = "radio://0/80/2M/E7E7E7E7E7"
dron.connect(uri=URI, blocking=True) # me conecto al dron
print (‘Conectado’)

def informar (param):
   print (‘Mensaje del dron: ‘, param)

# Llamada no bloqueante, con callback y parámetro para el callback
dron.takeOff (2, blocking = False, callback= informar, params= ‘En el aire a 2 metros de altura’)
print (‘Hago otras cosas mientras se realiza el despegue. Ya me avisarán’)
```
En este caso, en la llamada no bloqueante añadimos un parámetro que se le pasará al callback en 
en el momento de activarlo. De esta forma, la misma función _informar_ se puede usar  como callback
para otras llamadas no bloqueantes. Por ejemplo, podríamos llamar de forma no bloqueante al método 
para aterrizar y pasarle como callback también la función _informar_, pero ahora con el  parámetro
'Ya estoy en tierra', que es lo que escribiría en consola la función  _informar_ en el momento del aterrizaje.

La modalidad no bloqueante en las llamadas a la librería es especialmente útil **cuando
queremos interactuar con el dron mediante una interfaz gráfica**. Por ejemplo, no vamos a
querer que se bloquee la interfaz mientras el dron despega. Seguramente querremos seguir
procesando los datos de telemetría mientras el dron despega, para mostrar al usuario, por
ejemplo, la altura del dron en todo momento.

En el siguiente vídeo se hace uso de la función takeOff para demostrar de manera sencilla el efecto de las llamadas bloqueantes o no bloqueantes.

[![](https://img.youtube.com/vi/Oi9jYxCv_Zk/0.jpg)](https://www.youtube.com/watch?v=Oi9jYxCv_Zk)

## 3. Métodos de la clase Dron
En la tabla que se enlaza más abajo se describen los métodos de la clase Dron de la versión actual de CrazyLink.

El siguiente vídeo será una navegación por el código de CrazyLink para entender su lógica y poder empezar a trabajar con él.
[![](https://img.youtube.com/vi/SIRw1PJkhDY/0.jpg)](https://www.youtube.com/watch?v=SIRw1PJkhDY)


## 4. Instalación de CrazyLink
Para poder usar la librería CrazyLink en un proyecto PyCharm es necesario copiar la carpeta CrazyLink que hay en este repositorio en la carpeta del proyecto en el que se quiere usar. Para ello basta clonar este repositorio y luego copiar la carpeta CrazyLink (y posiblemente borrar después el repositorio clonado).

## 5. Inicio de Crazyflie
Para empezar a usar el Crazyflie a través de la radio Crazyradio PA es necesario el instalador de driver que me permitirá controlar el dongle. Para ello, deberemos instalar el ejecutable Zadig des de este enlace <a href="https://zadig.akeo.ie/" target="_blank">Zadig</a> y configurarlo para instalar el driver libusb. El siguiente paso es generar un proyecto con PyCharm e instalar la lista de librerías que se detallan a continuación.
- cfclient
- pygame
- pillow
- paho-mqtt v1.6.1

Una vez con las librerías instaladas y nuestro proyecto de PyCharm creado, podremos ejecutar el comando cfclient en la consola del proyecto para hacer las primeras pruebas de vuelo desde la interfaz ofrecida por Bitcraze.
<img width="1539" height="922" alt="image" src="https://github.com/user-attachments/assets/49de15ff-544d-4db7-b0a4-237eae8b52a7" />

## 6. Demostradores
En este repositorio se proporcionan dos aplicaciones que demuestran el uso de la librería CrazyLink para diferentes funcionalidades, una de ellas tiene la finalidad de probar los comandos básicos y servir de entorno de desarrollo mientras que la segunda pretende ser un demostrador de las capacidades del dron y de la librería.     


### Aplicación de prueba
Se trata de una aplicación que presenta al usuario una interfaz basada en botones que permiten realizar las operaciones básicas de control del dron (conectar, despegar, navegar en diferentes direcciones, aterrizar, etc.). La aplicación usa la clase Dron para comunicarse con él mediante la radio Crazyradio PA.  
   
### Aplicación de demostración
La APP de demostración ofrece una interfaz con un mapa interactivo, pensada para planificar y supervisar vuelos del dron de manera cómoda e intuitiva. Para iniciar esta segunda aplicación, deberemos abrir la estación de tierra y hacer clic en el botón de Abrir mapa, lo que generará una nueva ventana. En esta ventana, lo que veremos al inicio es un canva gris cuadriculado representando una superficie de 10 metros por 10 metros, con marcas cada 0,5 metros. El dron aparece inicialmente en el centro (posición X=o e Y=0) para empezar a actualizar su posición en cuanto despegue.

En la parte superior hay una barra de controles con los siguientes elementos: un botón de Misión, que al hacer clic nos indicará los pasos necesarios para generar una misión, un segundo botón llamado “Limpiar misión” que nos permite borrar los waypoints y salir del modo planificación; también disponemos de un slider de velocidad que nos permitirá regular a cómo de rápido queremos hacer los movimientos, por último, tenemos dos botones que nos permiten activar y desactivar el modo joystick, para poder controlar el dron desde el mando.

El siguiente vídeo ilustra el funcionamiento de ambas aplicaciones.


[![](https://img.youtube.com/vi/jpzkRK8Avdk/0.jpg)](https://www.youtube.com/watch?v=jpzkRK8Avdk)


