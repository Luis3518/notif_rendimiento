# Sistema de Gestión de Tenencias de Inversión

Sistema Python que monitorea y calcula rendimientos de una cartera de inversiones diversificada, incluyendo acciones argentinas, CEDEARs y criptomonedas.

## 🚀 Características

- ✅ Obtención automática de cotizaciones desde APIs en tiempo real
- ✅ Conversión de ARS a USD usando dólar MEP (casa bolsa)
- ✅ Cálculo de rendimientos por activo y categoría
- ✅ Reporte consolidado con colores en consola
- ✅ Manejo robusto de errores con reintentos automáticos
- ✅ Logging detallado de todas las operaciones
- ✅ Configuración mediante variables de entorno
- ✅ Notificaciones automáticas via Telegram
- 🚧 Soporte para criptomonedas (en desarrollo)

## 📋 Requisitos

- Python 3.7 o superior
- Conexión a Internet (para consultar APIs)

## 🔧 Instalación

1. Clonar o descargar el repositorio

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. (Opcional) Configurar variables de entorno:
```bash
# Copiar el archivo de ejemplo
copy .env.example .env

# Editar .env con tus valores personalizados (opcional)
```

## 📊 Estructura del Proyecto

```
C:\Proyectos\
├── shared-data/
│   └── tenencias.json   # Archivo compartido con tu cartera
│
└── notif_rendimiento/
    ├── .env                 # Variables de entorno (opcional)
    ├── .env.example         # Plantilla de configuración
    ├── .gitignore          # Protege .env
    ├── main.py             # Script principal
    ├── api_client.py       # Cliente de APIs
    ├── calculator.py       # Cálculos de rendimiento
    ├── report.py           # Generador de reportes
    └── requirements.txt    # Dependencias Python
```

**Nota**: El archivo `tenencias.json` está en una carpeta compartida `shared-data` al mismo nivel que el proyecto, permitiendo que múltiples proyectos accedan al mismo archivo de cartera.

## 📝 Configuración

### Personalizar tu Cartera

El archivo `tenencias.json` se encuentra en `C:\Proyectos\shared-data\` (configurado en `.env`).

Si deseas usar una ubicación diferente, edita el archivo `.env`:

```env
# Ruta relativa desde el proyecto
TENENCIAS_FILE=../shared-data/tenencias.json

# O ruta absoluta
TENENCIAS_FILE=C:/Proyectos/shared-data/tenencias.json

# O en el mismo directorio del proyecto
TENENCIAS_FILE=tenencias.json
```

Estructura del archivo `tenencias.json`:

```json
{
  "acciones": [
    {
      "ticker": "YPFD",
      "cantidad": 100,
      "preciototalcompra": 3500.00
    }
  ],
  "cedears": [
    {
      "ticker": "AAPL",
      "cantidad": 50,
      "preciototalcompra": 8500.00
    }
  ],
  "crypto": [
    {
      "ticker": "BTC",
      "cantidad": 0.05,
      "preciototalcompra": 2800.00
    }
  ]
}
```

**Importante**: 
- `preciototalcompra` debe estar en USD para todas las categorías
- Los tickers deben coincidir con los símbolos de las APIs
- Los valores en `tenencias.json` son de ejemplo. Ajústalos según tu cartera real
- Tanto acciones como CEDEARs cotizan en ARS y se convierten automáticamente a USD

## ▶️ Uso

### Ejecución Normal

```bash
python main.py
```

El sistema automáticamente:
1. Cargará tu archivo `tenencias.json`
2. Consultará la cotización del dólar MEP
3. Obtendrá precios actuales de acciones y CEDEARs
4. Calculará rendimientos y conversiones
5. Mostrará un reporte detallado en consola

### 📱 Comportamiento de Notificaciones

Por defecto, las notificaciones de Telegram **NO se envían automáticamente**. Solo se envían cuando:

1. **Se fuerza el envío con un argumento:**
   ```bash
   python main.py --notify
   # O usando la versión corta:
   python main.py -n
   ```

2. **Se fuerza el envío con un mensaje personalizado:**
   ```bash
   python main.py --notify "Reporte Semanal"
   # O usando la versión corta:
   python main.py -n "Cierre del Mes"
   ```
   El mensaje personalizado reemplazará el título "Resumen de Cartera" en la notificación.

3. **Algún activo supera el 40% de rendimiento positivo:**
   - El sistema detecta automáticamente si algún activo tiene más del 40% de ganancia
   - En ese caso, se enviará la notificación sin necesidad de usar `--notify`
   - Verás en los logs: *"Notificación activada: al menos un activo supera el 40% de rendimiento"*

**Ejemplos:**
```bash
# Ejecución normal - Solo notifica si hay activo > 40%
python main.py

# Forzar notificación siempre
python main.py --notify

# Forzar notificación con título personalizado
python main.py --notify "Resumen Mensual de Octubre"

# También funciona con -n
python main.py -n "Alerta de Rendimiento"
```

> **Nota**: Si las variables `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` no están configuradas, el sistema funcionará normalmente pero no intentará enviar notificaciones.

## 📈 Ejemplo de Salida

```
====================================================================
                  REPORTE DE RENDIMIENTO DE CARTERA                                  
====================================================================

Dólar MEP (Bolsa): $1,495.20

════════════════════════════════════════════════════════════════════
ACCIONES ARGENTINAS (ARS → USD)
════════════════════════════════════════════════════════════════════

YPFD (ACCIONES)
  Cantidad:              4
  Precio compra (unit):  $28.58
  Precio actual (unit):  $36.85
  Valor actual (total):  $147.41
  Ganancia/Pérdida:      +$33.09
  Rendimiento:           +28.94%
  Precio ARS:            $55100.00 (MEP: $1495.20)


## 🔌 APIs Utilizadas

- **Acciones argentinas**: https://data912.com/live/arg_stocks (cotizaciones en ARS)
- **CEDEARs**: https://data912.com/live/arg_cedears (cotizaciones en ARS)
- **Dólar MEP**: https://dolarapi.com/v1/dolares (conversión ARS → USD)
- **Criptomonedas**: 🚧 En desarrollo - Próximamente se agregará integración con APIs de crypto

> **Nota sobre conversión**: Tanto las acciones como los CEDEARs cotizan en pesos argentinos (ARS). El sistema convierte automáticamente todos los valores a dólares (USD) usando la cotización del dólar MEP (casa bolsa) para facilitar la comparación y análisis.

> **Nota sobre crypto**: La funcionalidad de criptomonedas está actualmente en desarrollo. Puedes incluir crypto en tu archivo `tenencias.json`, pero los precios no se obtendrán automáticamente hasta que se integre una API de cotizaciones.

## ⚙️ Configuración Avanzada

### Variables de Entorno (.env)

Puedes personalizar el comportamiento del sistema creando un archivo `.env`:

**APIs y Configuración:**
- `API_ACCIONES`: URL de la API de acciones
- `API_CEDEARS`: URL de la API de CEDEARs
- `API_DOLAR`: URL de la API del dólar
- `TENENCIAS_FILE`: Nombre del archivo JSON de tenencias
- `MAX_RETRIES`: Número máximo de reintentos en peticiones (default: 3)
- `TIMEOUT`: Timeout en segundos para peticiones HTTP (default: 10)
- `DOLAR_CASA`: Casa de cambio para dólar MEP (default: bolsa)

**Notificaciones de Telegram (opcional):**
- `TELEGRAM_BOT_TOKEN`: Token del bot de Telegram (obtener de @BotFather)
- `TELEGRAM_CHAT_ID`: ID del chat/usuario donde enviar notificaciones

#### 📱 Configurar Notificaciones de Telegram

Para recibir notificaciones automáticas del rendimiento de tu cartera:

1. **Crear un bot de Telegram:**
   - Abre Telegram y busca [@BotFather](https://t.me/botfather)
   - Envía `/newbot` y sigue las instrucciones
   - Copia el token que te proporciona (ej: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Obtener tu Chat ID:**
   - Envía un mensaje a tu bot
   - Abre en tu navegador: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
   - Busca el campo `"chat":{"id":` y copia ese número (ej: `987654321`)

3. **Configurar variables de entorno:**
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=987654321
   ```

4. **Probar el sistema:**
   ```bash
   python main.py
   ```
   
Si las variables no están configuradas, el sistema funcionará normalmente pero sin enviar notificaciones.

**Ejemplo de mensaje de Telegram:**
```
📊 Resumen de Cartera

💵 Dólar MEP: $1,495.20
📅 Actualizado: 01/11/2025 18:00

━━━━━━━━━━━━━━━━━━━
🇦🇷 ACCIONES
🟢 YPFD: +28.94%

🌎 CEDEARS
🟢 AAPL: +15.23%
🔴 TSLA: -5.42%
━━━━━━━━━━━━━━━━━━━
```

**Con título personalizado:**
```
📊 Reporte Semanal

💵 Dólar MEP: $1,495.20
📅 Actualizado: 01/11/2025 18:00

━━━━━━━━━━━━━━━━━━━
🇦🇷 ACCIONES
🟢 YPFD: +28.94%

🌎 CEDEARS
🟢 AAPL: +15.23%
🔴 TSLA: -5.42%
━━━━━━━━━━━━━━━━━━━
```


### Arquitectura del Sistema

El sistema está dividido en módulos especializados:

- **main.py**: Orquestador principal, coordina el flujo de ejecución y carga configuración desde `.env`
- **api_client.py**: Cliente HTTP con reintentos automáticos para las APIs, carga su configuración desde `.env`
- **calculator.py**: Motor de cálculos de rendimiento y conversiones ARS/USD
- **report.py**: Generador de reportes visuales con colores

### Fórmulas de Cálculo

**Conversión ARS → USD:**
```
valor_usd = valor_ars / cotizacion_dolar_mep
```

**Rendimiento Porcentual:**
```
rendimiento = ((valor_actual - precio_compra) / precio_compra) × 100
```

## � Sistema de Logs

El sistema genera automáticamente archivos de log detallados en la carpeta `logs/` para cada ejecución:

### Archivos Generados

Cada ejecución crea dos archivos con timestamp único en formato `YYYYMMDD_HHMMSS`:

1. **`execution_YYYYMMDD_HHMMSS.log`**
   - Contiene todos los logs (INFO, WARNING, ERROR)
   - Útil para auditar el flujo completo de ejecución
   - Incluye: consultas a APIs, cálculos realizados, warnings, etc.

2. **`errors_YYYYMMDD_HHMMSS.log`**
   - Contiene únicamente logs de ERROR y CRITICAL
   - Permite identificar problemas rápidamente
   - Estará vacío en ejecuciones exitosas sin errores

### Ejemplo de Nombres

```
logs/
├── execution_20251101_175958.log  # Ejecución del 1/nov/2025 a las 17:59:58
├── errors_20251101_175958.log     # Errores de esa misma ejecución
├── execution_20251101_180430.log  # Segunda ejecución
└── errors_20251101_180430.log     # (vacío si no hubo errores)
```

### Características

- ✅ Los logs también se muestran en consola en tiempo real
- ✅ Formato: `timestamp - módulo - nivel - mensaje`
- ✅ Encoding UTF-8 para caracteres especiales
- ✅ La carpeta `logs/` está en `.gitignore` (no se versiona)
- ✅ Creación automática de la carpeta si no existe

### Ejemplo de Contenido

```log
2025-11-01 17:59:58,768 - __main__ - INFO - Cargando archivo ../shared-data/tenencias.json
2025-11-01 17:59:58,769 - __main__ - INFO - Cargadas: 1 acciones, 4 CEDEARs, 0 crypto
2025-11-01 17:59:59,757 - api_client - INFO - Dólar MEP (bolsa/venta): $1495.2
2025-11-01 18:00:01,079 - api_client - WARNING - No se encontró cotización para CEDEAR: EMM
2025-11-01 18:00:01,089 - __main__ - INFO - Proceso completado exitosamente
```

## �🐛 Resolución de Problemas

**Error: No se encuentra tenencias.json**
- Verifica que el archivo existe en el mismo directorio que main.py
- Revisa los logs en `logs/errors_*.log` para más detalles

**Error: No se puede conectar a las APIs**
- Verifica tu conexión a Internet
- Las APIs pueden estar temporalmente no disponibles
- Considera aumentar `TIMEOUT` en `.env`
- Consulta `logs/errors_*.log` para ver el error específico

**Error: Ticker no encontrado**
- Verifica que el símbolo del ticker sea correcto
- Algunos activos pueden no estar disponibles en las APIs
- El sistema registra un WARNING en los logs

**Error: ModuleNotFoundError**
```bash
pip install -r requirements.txt
```

**Revisar logs de ejecuciones anteriores**
```bash
# Ver último archivo de ejecución
type logs\execution_*.log | Select-Object -Last 1

# Ver últimos errores
type logs\errors_*.log | Select-Object -Last 1
```

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

