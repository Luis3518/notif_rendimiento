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

Ejecutar el sistema:

```bash
python main.py
```

El sistema automáticamente:
1. Cargará tu archivo `tenencias.json`
2. Consultará la cotización del dólar MEP
3. Obtendrá precios actuales de acciones y CEDEARs
4. Calculará rendimientos y conversiones
5. Mostrará un reporte detallado en consola

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

- `API_ACCIONES`: URL de la API de acciones
- `API_CEDEARS`: URL de la API de CEDEARs
- `API_DOLAR`: URL de la API del dólar
- `TENENCIAS_FILE`: Nombre del archivo JSON de tenencias
- `MAX_RETRIES`: Número máximo de reintentos en peticiones (default: 3)
- `TIMEOUT`: Timeout en segundos para peticiones HTTP (default: 10)
- `DOLAR_CASA`: Casa de cambio para dólar MEP (default: bolsa)


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

## 🐛 Resolución de Problemas

**Error: No se encuentra tenencias.json**
- Verifica que el archivo existe en el mismo directorio que main.py

**Error: No se puede conectar a las APIs**
- Verifica tu conexión a Internet
- Las APIs pueden estar temporalmente no disponibles
- Considera aumentar `TIMEOUT` en `.env`

**Error: Ticker no encontrado**
- Verifica que el símbolo del ticker sea correcto
- Algunos activos pueden no estar disponibles en las APIs

**Error: ModuleNotFoundError**
```bash
pip install -r requirements.txt
```

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

