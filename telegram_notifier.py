"""
Módulo para enviar notificaciones via Telegram
"""
import logging
import os
import requests
from typing import List, Dict

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Cliente para enviar notificaciones via Telegram Bot API"""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        """
        Inicializa el notificador de Telegram
        
        Args:
            bot_token: Token del bot de Telegram (o se lee de env)
            chat_id: ID del chat destino (o se lee de env)
        """
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram no configurado (falta BOT_TOKEN o CHAT_ID)")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("Telegram notifier inicializado correctamente")
    
    def send_message(self, message: str) -> bool:
        """
        Envía un mensaje a través de Telegram
        
        Args:
            message: Texto del mensaje a enviar
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        if not self.enabled:
            logger.warning("Telegram no está habilitado. No se enviará mensaje.")
            return False
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Mensaje de Telegram enviado exitosamente")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al enviar mensaje de Telegram: {e}")
            return False
    
    def format_portfolio_message(
        self,
        dolar_mep: float,
        dolar_mep_fecha: str,
        acciones: List[Dict],
        cedears: List[Dict],
        crypto: List[Dict],
        totals_portfolio: Dict,
        custom_title: str = None
    ) -> str:
        """
        Formatea el mensaje de resumen de cartera para Telegram
        
        Args:
            dolar_mep: Cotización del dólar MEP
            dolar_mep_fecha: Fecha de actualización del MEP
            acciones: Lista de activos de acciones
            cedears: Lista de activos de CEDEARs
            crypto: Lista de activos de crypto
            totals_portfolio: Totales consolidados
            custom_title: Título personalizado (opcional, reemplaza "Resumen de Cartera")
            
        Returns:
            Mensaje formateado en HTML para Telegram
        """
        from datetime import datetime
        
        # Formatear la fecha
        try:
            fecha_dt = datetime.fromisoformat(dolar_mep_fecha.replace('Z', '+00:00'))
            fecha_formateada = fecha_dt.strftime("%d/%m/%Y %H:%M")
        except:
            fecha_formateada = dolar_mep_fecha
        
        # Construir mensaje
        lines = []
        
        # Usar título personalizado si está disponible, sino usar el predeterminado
        if custom_title:
            lines.append(f"📊 <b>{custom_title}</b>\n")
        else:
            lines.append("📊 <b>Resumen de Cartera</b>\n")
        
        lines.append(f"💵 <b>Dólar MEP:</b> ${dolar_mep:.2f}")
        lines.append(f"📅 <b>Actualizado:</b> {fecha_formateada}\n")
        
        # Detalle de acciones
        if acciones:
            lines.append("━━━━━━━━━━━━━━━━━━━")
            lines.append("<b>🇦🇷 ACCIONES</b>")
            for asset in acciones:
                rend = asset['rendimiento_porcentaje']
                emoji = "🟢" if rend >= 0 else "🔴"
                sign = "+" if rend >= 0 else ""
                lines.append(f"{emoji} <b>{asset['ticker']}</b>: {sign}{rend:.2f}%")
        
        # Detalle de CEDEARs
        if cedears:
            lines.append("\n<b>🌎 CEDEARS</b>")
            for asset in cedears:
                rend = asset['rendimiento_porcentaje']
                emoji = "🟢" if rend >= 0 else "🔴"
                sign = "+" if rend >= 0 else ""
                lines.append(f"{emoji} <b>{asset['ticker']}</b>: {sign}{rend:.2f}%")
        
        # Detalle de Crypto
        if crypto:
            lines.append("\n<b>₿ CRYPTO</b>")
            for asset in crypto:
                rend = asset['rendimiento_porcentaje']
                emoji = "🟢" if rend >= 0 else "🔴"
                sign = "+" if rend >= 0 else ""
                lines.append(f"{emoji} <b>{asset['ticker']}</b>: {sign}{rend:.2f}%")
        
        lines.append("━━━━━━━━━━━━━━━━━━━")
        
        return "\n".join(lines)
