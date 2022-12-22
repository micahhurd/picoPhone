from ili9341 import Display
from machine import Pin, SPI

font_pack = {
    "arcade": ("ArcadePix9x11.c", 9, 11),
    "bally": ("Bally5x8.c", 5, 8),
    "bally2": ("Bally7x9.c", 7, 9),
    "broadway": ("Broadway17x15.c", 17, 15),
    "espresso": ("EspressoDolce18x24.c", 18, 24),
    "fixed": ("FixedFont5x8.c", 5, 8),
    "ibm": ("IBMPlexMono12x25.c", 12, 24),
    "neato": ("Neato5x7.c", 5, 7),
    "neato2": ("NeatoReduced5x7.c", 5, 7),
    "robotron": ("Robotron13x21.c", 13, 21),
    "robotron2": ("Robotron7x11.c", 7, 11),
    "ubuntu": ("UbuntuMono12x24.c", 12, 24),
    "unispace": ("Unispace12x24.c", 12, 24),
    "unispace2": ("UnispaceExt12x24.c", 12, 24),
    "wendy": ("Wendy7x8.c", 7, 8)
    }


TFT_CLK_PIN = const(6)
TFT_MOSI_PIN = const(7)
TFT_MISO_PIN = const(4)

TFT_CS_PIN = const(13)
TFT_RST_PIN = const(14)
TFT_DC_PIN = const(15)

def createMyDisplay():
    #spi = SPI(0, baudrate=40000000, sck=Pin(TFT_CLK_PIN), mosi=Pin(TFT_MOSI_PIN))
    spiTFT = SPI(0, baudrate=51200000,
                 sck=Pin(TFT_CLK_PIN), mosi=Pin(TFT_MOSI_PIN))
    display = Display(spiTFT,
                      dc=Pin(TFT_DC_PIN), cs=Pin(TFT_CS_PIN), rst=Pin(TFT_RST_PIN))
    return display
        