"""
Módulo para cálculos de rendimiento de cartera
"""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class PortfolioCalculator:
    """Calculadora de rendimientos de cartera"""
    
    def __init__(self, dolar_mep: float):
        """
        Inicializa el calculador con la cotización del dólar MEP
        
        Args:
            dolar_mep: Cotización del dólar MEP para conversiones
        """
        self.dolar_mep = dolar_mep
    
    def convert_ars_to_usd(self, amount_ars: float) -> float:
        """Convierte ARS a USD usando dólar MEP"""
        return amount_ars / self.dolar_mep
    
    def calculate_asset_performance(
        self,
        ticker: str,
        categoria: str,
        cantidad: float,
        precio_compra_total_usd: float,
        precio_actual_unitario: float,
        is_ars: bool = False
    ) -> Dict:
        """
        Calcula el rendimiento de un activo individual
        
        Args:
            ticker: Símbolo del activo
            categoria: "acciones", "cedears" o "crypto"
            cantidad: Cantidad de unidades
            precio_compra_total_usd: Total invertido en USD
            precio_actual_unitario: Precio actual unitario (en ARS si is_ars=True, sino USD)
            is_ars: Si el precio actual está en ARS (requiere conversión)
        
        Returns:
            Dict con todos los cálculos del activo
        """
        # Convertir precio actual a USD si es necesario
        if is_ars:
            precio_actual_unitario_usd = self.convert_ars_to_usd(precio_actual_unitario)
        else:
            precio_actual_unitario_usd = precio_actual_unitario
        
        # Cálculos
        precio_compra_unitario_usd = precio_compra_total_usd / cantidad
        valor_actual_total_usd = cantidad * precio_actual_unitario_usd
        ganancia_perdida_usd = valor_actual_total_usd - precio_compra_total_usd
        rendimiento_porcentaje = (ganancia_perdida_usd / precio_compra_total_usd) * 100
        
        resultado = {
            "ticker": ticker,
            "categoria": categoria,
            "cantidad": cantidad,
            "precio_compra_total_usd": precio_compra_total_usd,
            "precio_compra_unitario_usd": precio_compra_unitario_usd,
            "precio_actual_unitario_usd": precio_actual_unitario_usd,
            "valor_actual_total_usd": valor_actual_total_usd,
            "ganancia_perdida_usd": ganancia_perdida_usd,
            "rendimiento_porcentaje": rendimiento_porcentaje,
        }
        
        if is_ars:
            resultado["precio_actual_ars"] = precio_actual_unitario
            resultado["precio_mep_usado"] = self.dolar_mep
        
        logger.info(f"Calculado rendimiento para {ticker}: {rendimiento_porcentaje:.2f}%")
        
        return resultado
    
    def calculate_category_totals(self, assets: List[Dict]) -> Dict:
        """
        Calcula totales para una categoría de activos
        
        Args:
            assets: Lista de activos procesados
        
        Returns:
            Dict con totales de la categoría
        """
        if not assets:
            return {
                "total_invertido_usd": 0,
                "total_actual_usd": 0,
                "ganancia_perdida_usd": 0,
                "rendimiento_porcentaje": 0
            }
        
        total_invertido = sum(a["precio_compra_total_usd"] for a in assets)
        total_actual = sum(a["valor_actual_total_usd"] for a in assets)
        ganancia_perdida = total_actual - total_invertido
        rendimiento = (ganancia_perdida / total_invertido * 100) if total_invertido > 0 else 0
        
        return {
            "total_invertido_usd": total_invertido,
            "total_actual_usd": total_actual,
            "ganancia_perdida_usd": ganancia_perdida,
            "rendimiento_porcentaje": rendimiento
        }
    
    def calculate_portfolio_totals(self, all_assets: List[Dict]) -> Dict:
        """
        Calcula totales consolidados de toda la cartera
        
        Args:
            all_assets: Lista con todos los activos procesados
        
        Returns:
            Dict con totales consolidados
        """
        return self.calculate_category_totals(all_assets)
