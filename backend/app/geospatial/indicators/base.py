import ee
from abc import ABC, abstractmethod

class SpectralIndicator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def type(self) -> str:
        pass
        
    @property
    @abstractmethod
    def formula(self) -> str:
        pass
        
    @property
    @abstractmethod
    def bands_used(self) -> list[str]:
        pass
        
    @property
    @abstractmethod
    def units(self) -> str:
        pass
        
    @property
    def calibration_status(self) -> str:
        return "not_calibrated"
        
    @abstractmethod
    def calculate(self, image: ee.Image) -> ee.Image:
        """
        Calculates the indicator from the provided Sentinel-2 image.
        The input image is assumed to be preprocessed (scaled to reflectance).
        Returns an ee.Image with a single band named after the indicator.
        """
        pass
