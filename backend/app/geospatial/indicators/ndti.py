import ee
from .base import SpectralIndicator

class NDTI(SpectralIndicator):
    @property
    def name(self) -> str:
        return "ndti"
        
    @property
    def type(self) -> str:
        return "Turbidity-Related Indicator"
        
    @property
    def formula(self) -> str:
        return "(B4 - B3) / (B4 + B3)"
        
    @property
    def bands_used(self) -> list[str]:
        return ["B3", "B4"]
        
    @property
    def units(self) -> str:
        return "relative / dimensionless proxy"
        
    def calculate(self, image: ee.Image) -> ee.Image:
        """
        NDTI = (Red - Green) / (Red + Green) -> (B4 - B3) / (B4 + B3)
        """
        return image.normalizedDifference(['B4', 'B3']).rename('ndti')
