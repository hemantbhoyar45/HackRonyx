import ee
from .base import SpectralIndicator

class SuspendedSedimentProxy(SpectralIndicator):
    @property
    def name(self) -> str:
        return "suspended_sediment"
        
    @property
    def type(self) -> str:
        return "Suspended Sediment Proxy"
        
    @property
    def formula(self) -> str:
        return "(B4 - B2) / (B4 + B2)"
        
    @property
    def bands_used(self) -> list[str]:
        return ["B2", "B4"]
        
    @property
    def units(self) -> str:
        return "relative / dimensionless proxy"
        
    def calculate(self, image: ee.Image) -> ee.Image:
        """
        Normalized Difference Suspended Sediment index proxy:
        (Red - Blue) / (Red + Blue) -> (B4 - B2) / (B4 + B2)
        """
        return image.normalizedDifference(['B4', 'B2']).rename('suspended_sediment')
