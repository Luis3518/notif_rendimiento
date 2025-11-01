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
    
    def _get_performance_emoji(self, rendimiento: float) -> str:
        """
        Determina el emoji según el rendimiento porcentual
        
        Args:
            rendimiento: Porcentaje de rendimiento
            
        Returns:
            Emoji correspondiente al rango de rendimiento
        """
        if rendimiento <= -80:
            return "☠"
        elif rendimiento <= -51:
            return "💀"
        elif rendimiento <= -16:
            return "🔴"
        elif rendimiento < 0:
            return "🟠"
        elif rendimiento <= 9:
            return "🟡"
        elif rendimiento <= 39:
            return "🟢"
        elif rendimiento <= 59:
            return "🤑"
        elif rendimiento <= 99:
            return "💰"
        else:  # >= 100%
            return "💎"
    
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
                emoji = self._get_performance_emoji(rend)
                sign = "+" if rend >= 0 else ""
                lines.append(f"{emoji} <b>{asset['ticker']}</b>: {sign}{rend:.2f}%")
        
        # Detalle de CEDEARs
        if cedears:
            lines.append("\n<b>🌎 CEDEARS</b>")
            for asset in cedears:
                rend = asset['rendimiento_porcentaje']
                emoji = self._get_performance_emoji(rend)
                sign = "+" if rend >= 0 else ""
                lines.append(f"{emoji} <b>{asset['ticker']}</b>: {sign}{rend:.2f}%")
        
        # Detalle de Crypto
        if crypto:
            lines.append("\n<b>₿ CRYPTO</b>")
            for asset in crypto:
                rend = asset['rendimiento_porcentaje']
                emoji = self._get_performance_emoji(rend)
                sign = "+" if rend >= 0 else ""
                lines.append(f"{emoji} <b>{asset['ticker']}</b>: {sign}{rend:.2f}%")
        
        lines.append("━━━━━━━━━━━━━━━━━━━")
        
        return "\n".join(lines)
    
    def format_high_performance_alert(
        self,
        high_performance_assets: List[Dict],
        dolar_mep: float,
        dolar_mep_fecha: str
    ) -> str:
        """
        Formatea un mensaje de alerta especial cuando activos superan el 40%
        
        Args:
            high_performance_assets: Lista de activos que superan el 40%
            dolar_mep: Cotización del dólar MEP
            dolar_mep_fecha: Fecha de actualización del MEP
            
        Returns:
            Mensaje formateado en HTML para Telegram
        """
        from datetime import datetime
        import math
        
        # Formatear la fecha
        try:
            fecha_dt = datetime.fromisoformat(dolar_mep_fecha.replace('Z', '+00:00'))
            fecha_formateada = fecha_dt.strftime("%d/%m/%Y %H:%M")
        except:
            fecha_formateada = dolar_mep_fecha
        
        lines = []
        
        # Header de alerta
        lines.append("🚨🔥 <b>¡ALERTA DE ALTO RENDIMIENTO!</b> 🔥🚨\n")
        
        # Información de los activos que superan el umbral
        if len(high_performance_assets) == 1:
            asset = high_performance_assets[0]
            lines.append(f"💎 <b>Activo {asset['ticker']}</b> superó el 40%")
            lines.append(f"📈 <b>Rendimiento actual:</b> +{asset['rendimiento_porcentaje']:.2f}%")
            lines.append(f"💰 <b>Ganancia:</b> ${asset['ganancia_perdida_usd']:.2f} USD")
            
            # Calcular cuántos activos vender para recuperar inversión
            precio_compra_total = asset['precio_compra_total_usd']
            precio_actual_unitario = asset['precio_actual_unitario_usd']
            cantidad_total = asset['cantidad']
            
            # Cantidad necesaria para recuperar inversión inicial
            cantidad_a_vender = math.ceil(precio_compra_total / precio_actual_unitario)
            
            # Asegurarse de no vender más de lo que se tiene
            if cantidad_a_vender <= cantidad_total:
                cantidad_restante = cantidad_total - cantidad_a_vender
                valor_vendido = cantidad_a_vender * precio_actual_unitario
                
                lines.append("")
                lines.append("━━━━━━━━━━━━━━━━━━━")
                lines.append("💡 <b>Estrategia de Recuperación:</b>")
                lines.append(f"📈 <b>Vende {cantidad_a_vender}</b> {asset['ticker']} → Recuperas ${valor_vendido:.2f} USD")
                lines.append(f"🎁 <b>Te quedan {cantidad_restante}</b> {asset['ticker']} <b>GRATIS</b>")
            else:
                lines.append("")
                lines.append("━━━━━━━━━━━━━━━━━━━")
                lines.append("💡 <b>Estrategia de Recuperación:</b>")
                lines.append(f"📤 <b>Vende todo</b> ({cantidad_total} {asset['ticker']}) para maximizar ganancia")
        else:
            lines.append(f"��� <b>{len(high_performance_assets)} activos</b> superaron el 40%\n")
            for asset in high_performance_assets:
                precio_compra_total = asset['precio_compra_total_usd']
                precio_actual_unitario = asset['precio_actual_unitario_usd']
                cantidad_total = asset['cantidad']
                
                cantidad_a_vender = math.ceil(precio_compra_total / precio_actual_unitario)
                
                if cantidad_a_vender <= cantidad_total:
                    cantidad_restante = cantidad_total - cantidad_a_vender
                    lines.append(f"🔸 <b>{asset['ticker']}:</b> +{asset['rendimiento_porcentaje']:.2f}% → Vende {cantidad_a_vender}, quedan {cantidad_restante} gratis")
                else:
                    lines.append(f"🔸 <b>{asset['ticker']}:</b> +{asset['rendimiento_porcentaje']:.2f}%")
        
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━")
        lines.append(f"💵 <b>Dólar MEP:</b> ${dolar_mep:.2f}")
        lines.append(f"📅 <b>Actualizado:</b> {fecha_formateada}")
        lines.append("━━━━━━━━━━━━━━━━━━━")        
        return "\n".join(lines)
