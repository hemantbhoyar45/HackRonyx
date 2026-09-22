import ee
from .base import SpectralIndicator

class FAI(SpectralIndicator):
    @property
    def name(self) -> str:
        return "fai"
        
    @property
    def type(self) -> str:
        return "Algal Activity-Related Indicator"
        
    @property
    def formula(self) -> str:
        return "B8 - (B4 + (B11 - B4) * ((842 - 665) / (1610 - 665)))"
        
    @property
    def bands_used(self) -> list[str]:
        return ["B4", "B8", "B11"]
        
    @property
    def units(self) -> str:
        return "relative / dimensionless proxy"
        
    def calculate(self, image: ee.Image) -> ee.Image:
        """
        FAI = R_NIR - R_NIR'
        R_NIR' = R_RED + (R_SWIR - R_RED) * ((wl_NIR - wl_RED) / (wl_SWIR - wl_RED))
        
        Using Sentinel-2 central wavelengths:
        Red (B4) = 665 nm
        NIR (B8) = 842 nm
        SWIR (B11) = 1610 nm
        
        Interpolation factor: (842 - 665) / (1610 - 665) = 177 / 945 = 0.1873
        """
        wl_red = 665.0
        wl_nir = 842.0
        wl_swir = 1610.0
        
        factor = (wl_nir - wl_red) / (wl_swir - wl_red)
        
        b4 = image.select('B4')
        b8 = image.select('B8')
        b11 = image.select('B11')
        
        # R_NIR' = B4 + (B11 - B4) * factor
        baseline = b4.add(b11.subtract(b4).multiply(factor))
        
        # FAI = B8 - baseline
        fai = b8.subtract(baseline).rename('fai')
        
        return fai
