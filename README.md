# Reto Applab

Esta aplicación sirve para demostrar un Pipeline básico:

- Se consume un [API](https://smn.conagua.gob.mx/es/web-service-api)
- Se extraen los datos obtenidos
- Se transforman y se manipulan ligeramete
- Se combinan con datos existentes.

todos estos procesos están automatizados con scripts de python y desarrollados de tal manera que puedan ser ejecutados por Docker _cada hora_.

A continuación la estructura general

```
├── history              # folder donde se almacenan los datos obtenidos del api
├── data_municipios      # folder donde se almacenan las tablas de datos trabajados
├── logs                 # folder donde se almacenan los logs
├── python
│   ├── api.py           # script que jala y guarda los datos del api
│   ├── join_tables.py   # script que transforma los datos y los junta con los anteriores
│   ├── util.py          # funciones de utilidad para los scripts
│   └── requirements.txt # librerias de dependencia
├── Dockerfile
└── docker_compose.yml
```

- Nótese que algunos de estos folders no se encuentran en git, y son generados automáticamente al comenzar a recolectar datos
- los folders `history`, `logs`, y `data_municipios` serán utilizados como Volúmenes de Docker para almacenar los datos recolectados

## instalación y uso

Existen dos ramas en este repositorio: `single_exec` y `persist` dependiendo del modo de uso deseado:

- `single_exec` levanta un contenedor de Docker cada que se quiere ejecutar el pipeline (una vez por hora), y en cuanto termina el proceso se destruye el contenedor.
- `persist` levanta un contenedor de Docker que se mantiene arriba permanentemente y ejecuta el pipeline una vez por hora

### single_exec

Esta opción es preferible si ya se cuenta con un servidor que corre otros procesos periódicamente, y se desea agregar este proceso a él.

#### setup

- clonar el repositorio

```bash
git clone -b single_exec https://github.com/Alex23rodriguez/Applab
cd Applab
```

- construir la imágen con `docker-compose`

```bash
docker-compose build
```

agregar a crontab para que se corra cada hora:

- si el crontab está vacío: (checar con `crontab -l`)

```bash
echo "30 * * * * docker-compose up" | crontab
```

- si no está vacío, correr `crontab -e` y agregar la línea `30 * * * * docker-compose up`

- para ejecutar una sóla vez (por ejemplo, si se quiere hacer debugging), corrase `docker-compose up`

- para detener el funcionamiento, eliminar el crontab (`crontab -r`) o la línea correspondiente

### persist (default)

Esta opción funciona como un servidor dedicado únicamente a ejecutar este proceso cada hora. Su configuración es un poco más fácil, por lo que también es la rama `main`

#### setup

- clonar el repositorio

```bash
git clone -b persist https://github.com/Alex23rodriguez/Applab
cd Applab
```

- construir la imágen con `docker-compose` y levantar un contenedor

```bash
docker-compose build
docker-compose up
```

- para ejecutar una sóla vez (por ejemplo, si se quiere hacer debugging), corrase el script "bootstrap" local: `sh script_local.sh`

- para detener el funcionamiento, ejecutar `docker-compose down`

---

## Decisiones

En esta sección se aclara algunas decisiones de diseño que se tomaron, y su razonamiento

1. El crontab corre cada hora al minuto 30
   Esto se debe a que el la especificación del API se indica que los datos son actualizados cada hora al minuto 15. Sin embargo, seguido pasa que el servicio se cae durante unos minutos antes y después de esta hora. El minuto 30 se un buen balance entre una hora que ya se encuentra disponible y agarrar los datos lo antes posible

2. los datos de `history` se reciben como `json` pero se almacenan como `csv`
   En el folder de `history` se almacenan los datos tal como son recibidos del API (sin filtrar los que no nos interesan). Los datos recibidos del API (usando `method=3` para que se actualicen cada hora) pueden ser bastante pesados: el archivo de `json` que se obtiene pesa alrededor de 100MB. Dada la estroctura de los datos, no se pierede nada de información al pasarlos a `csv`, y se reduce su tamaño en ~60%.

3. `.gitignore` los folders de `history`, `data_municipios` y `logs`
   En estos 3 folders se almacena la información que se va a persistir entre llamadas, y por lo tanto, se va acumulando. Esta información debe ser almacenada en un disco duro, y no in GitHub.

- La única excepción a esto es el archivo `data_municipios/data1.csv`. Este archivo se recibió como parte del reto y contiene la lista de municipios que nos interesan, por lo que se conserva para hacer "join" con cada nueva tanda de datos.
- A pesar de que las instrucciones indican que se vaya tomando cada vez los datos más recientes para combinar con los nuevos, opté por siempre combinar con este archivo ya si el API llegara a omitir municipios en ocaciones, el hacer "inner join" (indicaciones del equipo) eliminaría poco a poco las entradas. Por eso se combinan los datos siempre con este archivo: se toma como fuente de verdad sobre qué municipios nos interesan.
- Las instrucciones no dejan muy claro cómo combinar los datos, así que se optó por combinar dejar también las columnas de `data1.csv`. Corregir esto es fácil en caso de que sólo nos interese la temperatura y la precipitación.
- No supe qué propósito servía `data2.csv` (también en el correo original). Mandé un correo para verificar si estos eran los archivos de datos actualizados pero no recibí respuesta.

4. Las dos fases (jalar los datos y agregarlos a `history`, transformarlos y agregarlos a `data_municipios`) se corren secuencialmente, y la segunda fase sólo corre si la primera corre exitosamente
   Esto es porque no tiene caso crear un nuevo archivo de datos con información desactualizada. El link simbólico `current` sirve para siempre saber cuáles son los datos más recientes

## posibles mejoras

1. El API es muy inestable, y frecuentemente no otorga respuesta. En el código se maneja este caso para que no truene el programa, y se toman ciertas medidas para intentar que el API responda. Sin embargo, si tras varios intentos el programa no es exitoso y sale, no se vuelve intentar sino hasta la próxima hora. Esto podría mejorarse volviendo a intentarlo después de unos minutos

2. Los logs van todos a un mismo lugar, y para cambiar el nivel de especifidad (`DEBUG`, ..., `CRITICAL`) es necesario editar el código fuente
   Se propone, si así se deseara, agregar la opción de determinar el nivel de especifidad desde la línea de comandos:

```python
import logging
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument(
    "--log",
    "--logs",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    default="WARNING",
)
args = parser.parse_args()

logging.basicConfig(level=getattr(logging, args.log))
```

para correrse de la siguiente manera:

- `python api.py --log=DEBUG`

Además, todos los logs van únicamente a un archivo, por lo que no se pueden revizar a un vistazo (por ejemplo, con `docker logs`)
Se podrían agregar más `Handlers` para enviarlos a múltiples lugares, o usar distintos loggers según su función:

```python
L = logging.getLogger(__name__)
L.addHandler(logging.StreamHandler())
###
L = logging.getLogger(__name__)
fh = logging.FileHandler("path/to/log")
L.addHandler(fh)
```

3. Ya que el script está hecho para ser ejecutado al minuto 30, no se verifica si se corre _los primeros 15 minutos de la hora_, cuando el API aun no ha sido actualizado. Esto puede ser un problema ya que si se corre manualmente en este periodo, los archivos resultantes tendrían un nombre engañoso.
   Esto se puede solucionar fácilmente agregando `datetime.now() - timedelta(minutes=15)` cada que se calcula la hora

## Propuestas para colaboración

Si esta versión inicial fuera elegida para sequir siendo desarrollada por un equipo, hay ciertas consideraciones importantes:

1. Pruebas
   Se deben escribir "Unit Tests" para verificar el funcionamiento de los diferentes componentes, e "Integration Tests" para verificar que las distintas partes se comuniquen de manera correcta. Esto es particularmente importante si varias personas van a estar trabajando sobre la misma base de código

2. Revisitar la estructura del proyecto
   Dependiendo de los requisitos, debe planearse anticipadamente cuál será la estructura y alcance del proyecto, ya que intentar modificar el "esqueleto" más adelante se vuelve mucho más complicado.

3. Implementar mejoras.
   Las mejoras ya mencionadas permitirían que este proceso escale más eficientemente. En particular, debe planearse de antemano cómo será el formato y diseño de los logs para intentar agilizar la búsqueda de cuellos de botella y bugs. También debe investigarse el API para intentar averiguar cuándo / por qué falla y cómo se va lidiar con esas sitauciones.

4. Desempeño y costos
   Actualmente se trata de un proceso bastante ligero en términos de complejidad computacional. Sin embargo, si esto fuera a cambiar debe pensarse en dónde se va a correr (desde una Raspberry Pi a AWS) y los costos que implican los distintos servicios, así como el costo temporal relacionado a qué servicios se desarrollarán "in house" contra utilizar un SaaS, IaaS, etc.
