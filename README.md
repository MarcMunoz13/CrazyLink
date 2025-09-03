# La librería CrazyLink
CrazyLink es una librería que pretende facilitar el desarrollo de aplicaciones de control del dron. Ofrece una amplia variedad de funcionalidades y se está diseñando con la mente puesta en las posibles necesidades del Drone Engineering Ecosystem (DEE).    
En este repositorio puede encontrarse el código de la librería y varias aplicaciones que demuestran su uso, en una variedad de contextos. Es importante tener presente que CrazyLink está en desarrollo y, por tanto, no exenta de errores.
## 1. Alternativa a DronLink
En el DDE encontramos la librería DronLink, una adaptación de DroneKit creada específicamente en el ecosistema mencionado para trabajar con drones basados en ArduPilot. Sin embargo, DronLink está estrechamente ligada a esa plataforma de paquetes y no resulta compatible con el dron Crazylink, que cuenta con un sistema de posicionamiento relativo incompatible con GPS. Esta limitación ha sido la motivación que ha impulsado la creación de una librería alternativa, orientada a la integración del Crazyflie dentro del DDE para ofrecer una experiencia de usuario similar a la de los módulos que propone DronLink.
No obstante, DronLink sigue siendo plenamente operativa y dispone de abundante documentación y ejemplos. La filosofía de la nueva libreria, se basa en aprovechar los conceptos y estructuras que se han desarrollado en la librería original, sirviendo esta de inspiración y pauta que dicta la coherencia y el flujo de datos para adaptar el sistema al Crazyflie. De este modo, se facilita la transición y se asegura que tanto estudiantes como desarrolladores puedan trabajar de manera homogénea en futuros proyectos.
--------------------video?
## 2. Modelo de programación de CrazyLink
CrazyLink esta implementada en forma de clase **(la clase Dron)** con sus atributos y una
variedad de métodos para operar con el dron. La clase con los atributos está definida en el
fichero _Dron_1.py_ y los métodos están en los diferentes ficheros de la carpeta _modules_
(connect.py, takeOff.py, etc.).

Muchos de los métodos pueden activarse **de forma bloqueante o de forma no bloqueante**. En
el primer caso, **el control no se devuelve al programa que hace la llamada hasta que la
operación ordenada haya acabado**. Si la llamada es no bloqueante entonces **el control se
devuelve inmediatamente** para que el programa pueda hacer otras cosas mientras se realiza la
operación.
------------video de un takeoff en modo bloqueante vs no bloqueante?

## 3. Métodos de la clase Dron
En la tabla que se enlaza más abajo se describen los métodos de la clase Dron de la versión actual de CrazyLink.
-----?????????'

## 4. Instalación de CrazyLink
Para poder usar la librería CrazyLink en un proyecto Pycharm es necesario copiar la carpeta CrazyLink que hay en este repositorio en la carpeta del proyecto en el que se quiere usar. Para ello basta clonar este repositorio y luego copiar la carpeta dronLink (y posiblemente borrar después el repositorio clonado).     

## 5. Inicio de Crazyflie
Para empezar a usar el Crazyflie a traves de la radio Crazyradio PA es necesario el instalador de driver que me permitirá controlar el dongle. Para ello, deberemos instalar el ejecutable Zadig des de este enlace <a href="https://zadig.akeo.ie/" target="_blank">Zadig</a> y configurarlo para instalar el driver libsub. El siguiente paso es generar un proyecto con PyCharm e instalar la librería cfclient, con la librería instalada podremos ejecutar el comando cfclient des del termianl del proyecto, lo que nos abrirá una interfaz sencilla permitiendo controlar el dron.
-----captura de la interfaz

## 6. Demostradores
En este repositorio se proporcionan dos aplicaciones que demuestran el uso de la librería CrazyLink para diferentes funcionalidades, una de ellas tiene la finalidad de probar los comandos básicos y servir de entorno de desarrollo mientras que la segunda pretende ser un demostrador de las capacidades del dron y de la librería.     
### Aplicación de prueba
Se trata de una aplicación que presenta al usuario una interfaz basada en botones que permiten realizar las operaciones básicas de control del dron (conectar, despegar, navegar en diferentes direcciones, aterrizar, etc.). La aplicación usa la clase Dron para comunicarse con el mediante la radio Crazyradio PA.  
   
### Aplicación de demostración
La APP de demostración ofrece una interfaz con un mapa interactivo, pensada para planificar y supervisar vuelos del dron de manera cómoda e intuitiva. Para iniciar esta segunda aplicación, deberemos abrir la estación de tierra y clicar en el botón de Abrir mapa, lo que generará una nueva ventana. En esta ventana, lo que veremos al inicio es un canva gris cuadriculado representando una superficie de 10 metros por 10 metros, con marcas cada 0,5 metros. El dron aparece inicialmente en el centro (posición X=o e Y=0) para empezar a actualizar su posición en cuanto despegue.
En la parte superior hay una barra de controles con los siguientes elementos: un botón de Misión, que al clicarlo nos indicará los pasos necesarios para generar una misión, un segundo botón llamado “Limpiar misión” que nos permite borrar los waypoints y salir del modo planificación; también disponemos de un slider de velocidad que nos permitirá regular a cómo de rápido queremos hacer los movimientos, por último, tenemos dos botones que nos permiten activar y desactivar el modo joystick, para poder controlar el dron des del mando.

El siguiente vídeo ilustra el funcionamiento de ambas aplicaciones.


