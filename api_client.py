"""
Módulo para interactuar con las APIs de cotizaciones
"""
import logging
import os
import requests
from typing import Optional, Dict, List

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración desde .env
API_ACCIONES = os.getenv("API_ACCIONES", "https://data912.com/live/arg_stocks")
API_CEDEARS = os.getenv("API_CEDEARS", "https://data912.com/live/arg_cedears")
API_DOLAR = os.getenv("API_DOLAR", "https://dolarapi.com/v1/dolares")
DOLAR_CASA = os.getenv("DOLAR_CASA", "bolsa")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
TIMEOUT = int(os.getenv("TIMEOUT", "10"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIClient:
    """Cliente para obtener datos de las APIs de mercado"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def _get_with_retry(self, url: str) -> Optional[Dict]:
        """Realiza petición GET con reintentos automáticos"""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"Intentando obtener datos de {url} (intento {attempt}/{MAX_RETRIES})")
                response = self.session.get(url, timeout=TIMEOUT)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout en intento {attempt} para {url}")
                if attempt == MAX_RETRIES:
                    logger.error(f"Timeout definitivo tras {MAX_RETRIES} intentos para {url}")
                    return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Error en petición a {url}: {e}")
                return None
        return None
    
    def get_dolar_mep(self) -> Optional[float]:
        """Obtiene la cotización del dólar MEP (casa bolsa, venta)"""
        data = self._get_with_retry(API_DOLAR)
        
        if not data:
            logger.error("No se pudo obtener cotización del dólar MEP")
            return None
        
        try:
            # Buscar la casa "bolsa"
            for item in data:
                if item.get("casa") == DOLAR_CASA:
                    venta = item.get("venta")
                    logger.info(f"Dólar MEP (bolsa/venta): ${venta}")
                    return float(venta)
            
            logger.error(f"No se encontró la casa '{DOLAR_CASA}' en la respuesta")
            return None
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error al parsear datos del dólar MEP: {e}")
            return None
    
    def get_acciones_prices(self, tickers: List[str]) -> Dict[str, float]:
        """
        Obtiene precios de acciones argentinas (en ARS)
        Retorna dict {ticker: px_ask}
        """
        data = self._get_with_retry(API_ACCIONES)
        
        if not data:
            logger.error("No se pudo obtener cotizaciones de acciones")
            return {}
        
        prices = {}
        try:
            for ticker in tickers:
                found = False
                for item in data:
                    if item.get("symbol") == ticker:
                        px_ask = item.get("px_ask")
                        if px_ask:
                            prices[ticker] = float(px_ask)
                            logger.info(f"Acción {ticker}: ${px_ask} ARS")
                            found = True
                            break
                
                if not found:
                    logger.warning(f"No se encontró cotización para acción: {ticker}")
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error al parsear datos de acciones: {e}")
        
        return prices
    
    def get_cedears_prices(self, tickers: List[str]) -> Dict[str, float]:
        """
        Obtiene precios de CEDEARs (en ARS, igual que las acciones)
        Retorna dict {ticker: px_ask}
        """
        data = self._get_with_retry(API_CEDEARS)
        
        if not data:
            logger.error("No se pudo obtener cotizaciones de CEDEARs")
            return {}
        
        prices = {}
        try:
            for ticker in tickers:
                found = False
                for item in data:
                    if item.get("symbol") == ticker:
                        px_ask = item.get("px_ask")
                        if px_ask:
                            prices[ticker] = float(px_ask)
                            logger.info(f"CEDEAR {ticker}: ${px_ask} USD")
                            found = True
                            break
                
                if not found:
                    logger.warning(f"No se encontró cotización para CEDEAR: {ticker}")
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error al parsear datos de CEDEARs: {e}")
        
        return prices
