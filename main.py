"""
Sistema de Gestión de Tenencias de Inversión
Monitorea y calcula rendimientos de cartera (acciones, CEDEARs, crypto)
"""
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple

from dotenv import load_dotenv

from api_client import APIClient
from calculator import PortfolioCalculator
from report import ReportGenerator
from telegram_notifier import TelegramNotifier

# Cargar variables de entorno
load_dotenv()
TENENCIAS_FILE = os.getenv("TENENCIAS_FILE", "tenencias.json")

# Crear carpeta de logs si no existe
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Configurar logging con archivos separados por timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_all = os.path.join(LOGS_DIR, f"execution_{timestamp}.log")
log_file_errors = os.path.join(LOGS_DIR, f"errors_{timestamp}.log")

# Configurar el formato de logging
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Handler para todos los logs (INFO y superior)
file_handler_all = logging.FileHandler(log_file_all, encoding='utf-8')
file_handler_all.setLevel(logging.INFO)
file_handler_all.setFormatter(log_format)

# Handler para solo errores (ERROR y superior)
file_handler_errors = logging.FileHandler(log_file_errors, encoding='utf-8')
file_handler_errors.setLevel(logging.ERROR)
file_handler_errors.setFormatter(log_format)

# Handler para consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)

# Configurar el logger raíz
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler_all, file_handler_errors, console_handler]
)

logger = logging.getLogger(__name__)


def load_tenencias() -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Carga el archivo tenencias.json
    
    Returns:
        Tupla con (lista_acciones, lista_cedears, lista_crypto)
    
    Raises:
        FileNotFoundError: Si no encuentra el archivo
        json.JSONDecodeError: Si el JSON es inválido
        KeyError: Si falta alguna estructura esperada
    """
    try:
        logger.info(f"Cargando archivo {TENENCIAS_FILE}")
        with open(TENENCIAS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        acciones = data.get("acciones", [])
        cedears = data.get("cedears", [])
        crypto = data.get("crypto", [])
        
        logger.info(f"Cargadas: {len(acciones)} acciones, {len(cedears)} CEDEARs, {len(crypto)} crypto")
        
        # Validar estructura básica
        for asset in acciones + cedears + crypto:
            if not all(k in asset for k in ["ticker", "cantidad", "preciototalcompra"]):
                raise ValueError(f"Activo inválido: {asset}")
        
        return acciones, cedears, crypto
    
    except FileNotFoundError:
        logger.error(f"Archivo {TENENCIAS_FILE} no encontrado")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear JSON: {e}")
        raise
    except Exception as e:
        logger.error(f"Error al cargar tenencias: {e}")
        raise


def check_high_performance(todos_activos: List[Dict], threshold: float = 40.0) -> bool:
    """
    Verifica si algún activo supera el umbral de rendimiento
    
    Args:
        todos_activos: Lista con todos los activos procesados
        threshold: Umbral de rendimiento en porcentaje (default: 40%)
    
    Returns:
        True si algún activo supera el umbral, False en caso contrario
    """
    for activo in todos_activos:
        if activo['rendimiento_porcentaje'] > threshold:
            logger.info(f"Activo {activo['ticker']} supera el umbral: {activo['rendimiento_porcentaje']:.2f}% > {threshold}%")
            return True
    return False


def process_portfolio(force_notification: bool = False, custom_title: str = None):
    """
    Función principal que procesa toda la cartera
    
    Args:
        force_notification: Si es True, fuerza el envío de notificación
        custom_title: Título personalizado para la notificación de Telegram
    """
    
    try:
        # 1. Cargar tenencias
        acciones_data, cedears_data, crypto_data = load_tenencias()
        
        # 2. Inicializar cliente de API
        api_client = APIClient()
        
        # 3. Obtener cotización del dólar MEP
        logger.info("Obteniendo cotización del dólar MEP...")
        dolar_mep_data = api_client.get_dolar_mep()
        
        if not dolar_mep_data:
            logger.error("No se pudo obtener cotización del dólar MEP. Abortando.")
            return False
        
        dolar_mep = dolar_mep_data["venta"]
        dolar_mep_fecha = dolar_mep_data["fechaActualizacion"]
        
        # 4. Obtener cotizaciones de acciones
        acciones_prices = {}
        if acciones_data:
            logger.info("Obteniendo cotizaciones de acciones...")
            tickers_acciones = [a["ticker"] for a in acciones_data]
            acciones_prices = api_client.get_acciones_prices(tickers_acciones)
        
        # 5. Obtener cotizaciones de CEDEARs
        cedears_prices = {}
        if cedears_data:
            logger.info("Obteniendo cotizaciones de CEDEARs...")
            tickers_cedears = [c["ticker"] for c in cedears_data]
            cedears_prices = api_client.get_cedears_prices(tickers_cedears)
        
        # 6. Inicializar calculadora
        calculator = PortfolioCalculator(dolar_mep)
        
        # 7. Procesar acciones
        acciones_procesadas = []
        for accion in acciones_data:
            ticker = accion["ticker"]
            if ticker in acciones_prices:
                resultado = calculator.calculate_asset_performance(
                    ticker=ticker,
                    categoria="acciones",
                    cantidad=accion["cantidad"],
                    precio_compra_total_usd=accion["preciototalcompra"],
                    precio_actual_unitario=acciones_prices[ticker],
                    is_ars=True  # Las acciones están en ARS
                )
                acciones_procesadas.append(resultado)
            else:
                logger.warning(f"No se pudo obtener precio para acción: {ticker}")
        
        # 8. Procesar CEDEARs
        cedears_procesados = []
        for cedear in cedears_data:
            ticker = cedear["ticker"]
            if ticker in cedears_prices:
                resultado = calculator.calculate_asset_performance(
                    ticker=ticker,
                    categoria="cedears",
                    cantidad=cedear["cantidad"],
                    precio_compra_total_usd=cedear["preciototalcompra"],
                    precio_actual_unitario=cedears_prices[ticker],
                    is_ars=True  # Los CEDEARs también cotizan en ARS
                )
                cedears_procesados.append(resultado)
            else:
                logger.warning(f"No se pudo obtener precio para CEDEAR: {ticker}")
        
        # 9. Procesar crypto (sin cotizaciones por ahora, placeholder)
        crypto_procesados = []
        for cripto in crypto_data:
            logger.info(f"Crypto {cripto['ticker']}: No implementado aún (sin API)")
        
        # 10. Calcular totales por categoría
        totals_acciones = calculator.calculate_category_totals(acciones_procesadas)
        totals_cedears = calculator.calculate_category_totals(cedears_procesados)
        totals_crypto = calculator.calculate_category_totals(crypto_procesados)
        
        # 11. Calcular totales consolidados
        todos_activos = acciones_procesadas + cedears_procesados + crypto_procesados
        totals_portfolio = calculator.calculate_portfolio_totals(todos_activos)
        
        # 12. Generar reporte
        report = ReportGenerator()
        report.generate_full_report(
            acciones=acciones_procesadas,
            cedears=cedears_procesados,
            crypto=crypto_procesados,
            totals_acciones=totals_acciones,
            totals_cedears=totals_cedears,
            totals_crypto=totals_crypto,
            totals_portfolio=totals_portfolio,
            dolar_mep=dolar_mep,
            dolar_mep_fecha=dolar_mep_fecha
        )
        
        # 13. Determinar si se debe enviar notificación
        should_notify = False
        
        if force_notification:
            logger.info("Notificación forzada por argumento de línea de comandos")
            should_notify = True
        elif check_high_performance(todos_activos, threshold=40.0):
            logger.info("Notificación activada: al menos un activo supera el 40% de rendimiento")
            should_notify = True
        else:
            logger.info("No se envía notificación: ningún activo supera el 40% y no se forzó el envío")
        
        # 14. Enviar notificación de Telegram solo si corresponde
        if should_notify:
            logger.info("Enviando notificación de Telegram...")
            telegram = TelegramNotifier()
            if telegram.enabled:
                message = telegram.format_portfolio_message(
                    dolar_mep=dolar_mep,
                    dolar_mep_fecha=dolar_mep_fecha,
                    acciones=acciones_procesadas,
                    cedears=cedears_procesados,
                    crypto=crypto_procesados,
                    totals_portfolio=totals_portfolio,
                    custom_title=custom_title
                )
                telegram.send_message(message)
            else:
                logger.info("Notificación de Telegram deshabilitada (configurar TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID)")
        
        return True
    
    except FileNotFoundError:
        logger.error(f"Error: No se encontró el archivo {TENENCIAS_FILE}")
        return False
    except json.JSONDecodeError:
        logger.error("Error: El archivo JSON tiene formato inválido")
        return False
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        return False


def main():
    """Punto de entrada del programa"""
    logger.info("=" * 60)
    logger.info("Sistema de Gestión de Tenencias de Inversión")
    logger.info("=" * 60)
    
    # Verificar si se pasó el argumento --notify o -n
    force_notification = False
    custom_title = None
    
    # Buscar --notify o -n en los argumentos
    for i, arg in enumerate(sys.argv):
        if arg in ["--notify", "-n"]:
            force_notification = True
            # Si hay un argumento siguiente y no empieza con -, es el mensaje
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("-"):
                custom_title = sys.argv[i + 1]
                logger.info(f"Título personalizado detectado: '{custom_title}'")
            break
    
    if force_notification:
        logger.info("Argumento de notificación detectado: se enviará notificación de Telegram")
    
    success = process_portfolio(force_notification=force_notification, custom_title=custom_title)
    
    if success:
        logger.info("Proceso completado exitosamente")
        sys.exit(0)
    else:
        logger.error("El proceso finalizó con errores")
        sys.exit(1)


if __name__ == "__main__":
    main()
