# -*- coding: utf-8 -*-
"""
Compatibility wrapper for Adafruit NeoPixel SPI library.
Provides the same API as rpi_ws281x.PixelStrip for Pi 5 compatibility.
"""
from __future__ import absolute_import, division, unicode_literals

__author__ = "Charlie Powell, Austin (Pi 5 compatibility)"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"

# Lazy imports - only load Adafruit libraries when actually needed
# This allows the plugin to load even if dependencies are missing
board = None
neopixel = None


def _load_adafruit_libs():
    """Lazy load Adafruit libraries when needed."""
    global board, neopixel
    if board is None:
        import board as _board
        import neopixel_spi as _neopixel
        board = _board
        neopixel = _neopixel


def _get_color_order(strip_type):
    """Get the color order for a strip type, loading libraries if needed."""
    _load_adafruit_libs()
    color_orders = {
        "WS2811_STRIP_GRB": neopixel.GRB,
        "WS2812_STRIP": neopixel.GRB,  # WS2812 is typically GRB
        "WS2811_STRIP_RGB": neopixel.RGB,
        "WS2811_STRIP_RBG": neopixel.RBG,
        "WS2811_STRIP_GBR": neopixel.GBR,
        "WS2811_STRIP_BGR": neopixel.BGR,
        "WS2811_STRIP_BRG": neopixel.BRG,
        "SK6812_STRIP": neopixel.GRB,
        "SK6812W_STRIP": neopixel.GRBW,
        "SK6812_STRIP_RGBW": neopixel.RGBW,
        "SK6812_STRIP_RBGW": neopixel.RBGW,
        "SK6812_STRIP_GRBW": neopixel.GRBW,
        "SK6812_STRIP_GBRW": neopixel.GBRW,
        "SK6812_STRIP_BRGW": neopixel.BRGW,
        "SK6812_STRIP_BGRW": neopixel.BGRW,
    }
    return color_orders.get(strip_type, neopixel.GRB)


# Strip type names - these don't require loading the actual libraries
STRIP_TYPE_NAMES = [
    "WS2811_STRIP_GRB",
    "WS2812_STRIP",
    "WS2811_STRIP_RGB",
    "WS2811_STRIP_RBG",
    "WS2811_STRIP_GBR",
    "WS2811_STRIP_BGR",
    "WS2811_STRIP_BRG",
    "SK6812_STRIP",
    "SK6812W_STRIP",
    "SK6812_STRIP_RGBW",
    "SK6812_STRIP_RBGW",
    "SK6812_STRIP_GRBW",
    "SK6812_STRIP_GBRW",
    "SK6812_STRIP_BRGW",
    "SK6812_STRIP_BGRW",
]

# For backwards compatibility - these values mirror rpi_ws281x constants
# They're just used as keys to look up the actual color order
STRIP_TYPES = {name: name for name in STRIP_TYPE_NAMES}


class PixelStrip:
    """
    Compatibility wrapper that provides rpi_ws281x.PixelStrip API
    using Adafruit's neopixel_spi library underneath.

    This enables WS281x LED support on Raspberry Pi 5.
    """

    def __init__(
        self,
        num,
        pin,
        freq_hz=800000,
        dma=10,
        invert=False,
        brightness=255,
        channel=0,
        strip_type=None,
    ):
        """
        Initialize the LED strip.

        Args:
            num: Number of LEDs
            pin: GPIO pin (ignored for SPI - uses SPI0 MOSI/GPIO10)
            freq_hz: LED signal frequency (ignored, handled by SPI)
            dma: DMA channel (ignored for SPI)
            invert: Invert signal (not supported via SPI)
            brightness: Initial brightness (0-255)
            channel: PWM channel (ignored for SPI)
            strip_type: Strip type string (e.g., "WS2811_STRIP_GRB")
        """
        self._num = num
        self._brightness = brightness
        self._brightness_float = brightness / 255.0
        self._strip_type = strip_type
        self._strip = None
        self._pixel_order = None
        self._is_rgbw = False

    def begin(self):
        """Initialize the strip hardware."""
        # Lazy load Adafruit libraries
        _load_adafruit_libs()

        # Determine color order from strip type
        self._pixel_order = _get_color_order(self._strip_type)

        # Determine if RGBW strip
        self._is_rgbw = self._pixel_order in (
            neopixel.RGBW, neopixel.RBGW, neopixel.GRBW,
            neopixel.GBRW, neopixel.BRGW, neopixel.BGRW
        )

        self._strip = neopixel.NeoPixel_SPI(
            board.SPI(),
            self._num,
            brightness=self._brightness_float,
            auto_write=False,
            pixel_order=self._pixel_order,
        )

    def show(self):
        """Push pixel data to the strip."""
        if self._strip:
            self._strip.show()

    def numPixels(self):
        """Return the number of pixels."""
        return self._num

    def setPixelColor(self, n, color):
        """
        Set pixel color using a 24/32-bit color value.

        Args:
            n: Pixel index
            color: 24-bit RGB or 32-bit WRGB color value
        """
        if self._strip and 0 <= n < self._num:
            if self._is_rgbw:
                w = (color >> 24) & 0xFF
                r = (color >> 16) & 0xFF
                g = (color >> 8) & 0xFF
                b = color & 0xFF
                self._strip[n] = (r, g, b, w)
            else:
                r = (color >> 16) & 0xFF
                g = (color >> 8) & 0xFF
                b = color & 0xFF
                self._strip[n] = (r, g, b)

    def setPixelColorRGB(self, n, r, g, b, w=0):
        """
        Set pixel color using individual RGB(W) values.

        Args:
            n: Pixel index
            r: Red (0-255)
            g: Green (0-255)
            b: Blue (0-255)
            w: White (0-255, for RGBW strips)
        """
        if self._strip and 0 <= n < self._num:
            if self._is_rgbw:
                self._strip[n] = (int(r), int(g), int(b), int(w))
            else:
                self._strip[n] = (int(r), int(g), int(b))

    def setBrightness(self, brightness):
        """
        Set strip brightness.

        Args:
            brightness: Brightness value (0-255)
        """
        self._brightness = brightness
        self._brightness_float = brightness / 255.0
        if self._strip:
            self._strip.brightness = self._brightness_float

    def getBrightness(self):
        """Return current brightness (0-255)."""
        return self._brightness

    def getPixelColor(self, n):
        """
        Get pixel color as 24/32-bit value.

        Args:
            n: Pixel index

        Returns:
            24-bit RGB or 32-bit WRGB color value
        """
        if self._strip and 0 <= n < self._num:
            pixel = self._strip[n]
            if self._is_rgbw and len(pixel) >= 4:
                r, g, b, w = pixel[:4]
                return (w << 24) | (r << 16) | (g << 8) | b
            else:
                r, g, b = pixel[:3]
                return (r << 16) | (g << 8) | b
        return 0

    def getPixelColorRGB(self, n):
        """
        Get pixel color as RGB tuple.

        Args:
            n: Pixel index

        Returns:
            Tuple of (r, g, b)
        """
        if self._strip and 0 <= n < self._num:
            pixel = self._strip[n]
            return (pixel[0], pixel[1], pixel[2])
        return (0, 0, 0)

    def getPixelColorRGBW(self, n):
        """
        Get pixel color as RGBW tuple.

        Args:
            n: Pixel index

        Returns:
            Tuple of (r, g, b, w)
        """
        if self._strip and 0 <= n < self._num:
            pixel = self._strip[n]
            if self._is_rgbw and len(pixel) >= 4:
                return (pixel[0], pixel[1], pixel[2], pixel[3])
            return (pixel[0], pixel[1], pixel[2], 0)
        return (0, 0, 0, 0)

    def getPixels(self):
        """Return the pixel buffer."""
        if self._strip:
            return list(self._strip)
        return []
