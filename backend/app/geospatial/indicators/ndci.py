import ee
from .base import SpectralIndicator

class NDCI(SpectralIndicator):
    @property
    def name(self) -> str:
        return "ndci"
        
    @property
    def type(self) -> str:
        return "Chlorophyll-Related Indicator"
        
    @property
    def formula(self) -> str:
        return "(B5 - B4) / (B5 + B4)"
        
    @property
    def bands_used(self) -> list[str]:
        return ["B4", "B5"]
        
    @property
    def units(self) -> str:
        return "relative / dimensionless proxy"
        
    def calculate(self, image: ee.Image) -> ee.Image:
        """
        NDCI = (Red Edge - Red) / (Red Edge + Red) -> (B5 - B4) / (B5 + B4)
        """
        return image.normalizedDifference(['B5', 'B4']).rename('ndci')
