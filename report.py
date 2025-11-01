"""
Módulo para generar reportes de rendimiento
"""
from typing import List, Dict
from colorama import Fore, Style, init

# Inicializar colorama para Windows
init(autoreset=True)


class ReportGenerator:
    """Generador de reportes formateados para consola"""
    
    def __init__(self):
        pass
    
    def _format_currency(self, amount: float) -> str:
        """Formatea un número como moneda USD"""
        return f"${amount:,.2f}"
    
    def _format_percentage(self, percentage: float) -> str:
        """Formatea un porcentaje con color según sea positivo o negativo"""
        color = Fore.GREEN if percentage >= 0 else Fore.RED
        sign = "+" if percentage >= 0 else ""
        return f"{color}{sign}{percentage:.2f}%{Style.RESET_ALL}"
    
    def _format_amount(self, amount: float) -> str:
        """Formatea un monto con color según sea positivo o negativo"""
        color = Fore.GREEN if amount >= 0 else Fore.RED
        sign = "+" if amount >= 0 else ""
        return f"{color}{sign}{self._format_currency(amount)}{Style.RESET_ALL}"
    
    def print_header(self, title: str):
        """Imprime un encabezado formateado"""
        print("\n" + "=" * 100)
        print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(100)}{Style.RESET_ALL}")
        print("=" * 100 + "\n")
    
    def print_asset_details(self, asset: Dict):
        """Imprime detalles de un activo individual"""
        ticker = asset["ticker"]
        categoria = asset["categoria"].upper()
        cantidad = asset["cantidad"]
        precio_compra_unit = asset["precio_compra_unitario_usd"]
        precio_actual_unit = asset["precio_actual_unitario_usd"]
        valor_actual = asset["valor_actual_total_usd"]
        ganancia = asset["ganancia_perdida_usd"]
        rendimiento = asset["rendimiento_porcentaje"]
        
        print(f"{Fore.YELLOW}{Style.BRIGHT}{ticker}{Style.RESET_ALL} ({categoria})")
        print(f"  Cantidad:              {cantidad}")
        print(f"  Precio compra (unit):  {self._format_currency(precio_compra_unit)}")
        print(f"  Precio actual (unit):  {self._format_currency(precio_actual_unit)}")
        print(f"  Valor actual (total):  {self._format_currency(valor_actual)}")
        print(f"  Ganancia/Pérdida:      {self._format_amount(ganancia)}")
        print(f"  Rendimiento:           {self._format_percentage(rendimiento)}")
        
        # Si es una acción (tiene precio MEP), mostrar conversión
        if "precio_mep_usado" in asset:
            print(f"  Precio ARS:            ${asset['precio_actual_ars']:.2f} (MEP: ${asset['precio_mep_usado']:.2f})")
        
        print()
    
    def print_category_summary(self, category_name: str, totals: Dict):
        """Imprime resumen de una categoría"""
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}{'─' * 50}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}RESUMEN {category_name.upper()}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}{'─' * 50}{Style.RESET_ALL}")
        print(f"  Total Invertido:       {self._format_currency(totals['total_invertido_usd'])}")
        print(f"  Valor Actual:          {self._format_currency(totals['total_actual_usd'])}")
        print(f"  Ganancia/Pérdida:      {self._format_amount(totals['ganancia_perdida_usd'])}")
        print(f"  Rendimiento:           {self._format_percentage(totals['rendimiento_porcentaje'])}")
        print()
    
    def print_portfolio_summary(self, totals: Dict):
        """Imprime resumen consolidado de toda la cartera"""
        self.print_header("RESUMEN CONSOLIDADO DE CARTERA")
        print(f"{Fore.CYAN}  Total Invertido:       {Style.BRIGHT}{self._format_currency(totals['total_invertido_usd'])}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  Valor Actual:          {Style.BRIGHT}{self._format_currency(totals['total_actual_usd'])}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  Ganancia/Pérdida:      {Style.BRIGHT}{self._format_amount(totals['ganancia_perdida_usd'])}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  Rendimiento Total:     {Style.BRIGHT}{self._format_percentage(totals['rendimiento_porcentaje'])}{Style.RESET_ALL}")
        print("\n" + "=" * 100 + "\n")
    
    def generate_full_report(
        self,
        acciones: List[Dict],
        cedears: List[Dict],
        crypto: List[Dict],
        totals_acciones: Dict,
        totals_cedears: Dict,
        totals_crypto: Dict,
        totals_portfolio: Dict,
        dolar_mep: float,
        dolar_mep_fecha: str
    ):
        """
        Genera el reporte completo de la cartera
        
        Args:
            acciones: Lista de activos de acciones
            cedears: Lista de activos de CEDEARs
            crypto: Lista de activos de crypto
            totals_acciones: Totales de acciones
            totals_cedears: Totales de CEDEARs
            totals_crypto: Totales de crypto
            totals_portfolio: Totales consolidados
            dolar_mep: Cotización del dólar MEP utilizada
            dolar_mep_fecha: Fecha de actualización del dólar MEP
        """
        from datetime import datetime
        
        self.print_header("REPORTE DE RENDIMIENTO DE CARTERA")
        
        # Formatear la fecha y ajustar a hora de Argentina (UTC-3)
        try:
            from datetime import timedelta
            fecha_dt = datetime.fromisoformat(dolar_mep_fecha.replace('Z', '+00:00'))
            # Restar 3 horas para convertir de UTC a hora de Argentina
            fecha_dt_argentina = fecha_dt - timedelta(hours=3)
            fecha_formateada = fecha_dt_argentina.strftime("%d/%m/%Y %H:%M")
        except:
            fecha_formateada = dolar_mep_fecha
        
        print(f"{Fore.CYAN}Dólar MEP (Bolsa): {Style.BRIGHT}${dolar_mep:.2f}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Actualizado: {Style.BRIGHT}{fecha_formateada}{Style.RESET_ALL}\n")
        
        # ACCIONES
        if acciones:
            print(f"\n{Fore.BLUE}{Style.BRIGHT}{'═' * 100}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}{Style.BRIGHT}ACCIONES ARGENTINAS (ARS → USD){Style.RESET_ALL}")
            print(f"{Fore.BLUE}{Style.BRIGHT}{'═' * 100}{Style.RESET_ALL}\n")
            for asset in acciones:
                self.print_asset_details(asset)
            self.print_category_summary("Acciones", totals_acciones)
        
        # CEDEARS
        if cedears:
            print(f"\n{Fore.BLUE}{Style.BRIGHT}{'═' * 100}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}{Style.BRIGHT}CEDEARS (ARS → USD){Style.RESET_ALL}")
            print(f"{Fore.BLUE}{Style.BRIGHT}{'═' * 100}{Style.RESET_ALL}\n")
            for asset in cedears:
                self.print_asset_details(asset)
            self.print_category_summary("CEDEARs", totals_cedears)
        
        # CRYPTO
        if crypto:
            print(f"\n{Fore.BLUE}{Style.BRIGHT}{'═' * 100}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}{Style.BRIGHT}CRIPTOMONEDAS (USD){Style.RESET_ALL}")
            print(f"{Fore.BLUE}{Style.BRIGHT}{'═' * 100}{Style.RESET_ALL}\n")
            for asset in crypto:
                self.print_asset_details(asset)
            self.print_category_summary("Crypto", totals_crypto)
        
        # TOTALES CONSOLIDADOS
        self.print_portfolio_summary(totals_portfolio)
