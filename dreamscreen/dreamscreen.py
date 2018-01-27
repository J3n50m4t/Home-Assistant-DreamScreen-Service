"""DreamScreen controller. Send commands to/from your DreamScreen via Wifi."""

import socket
import logging

REQUIREMENTS = ["crc8==0.0.4"]

_LOGGER = logging.getLogger(__name__)


class DreamScreen:
    """Control mechanism for the DreamScreen Wifi."""

    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __init__(self, ip: str, group=0, port=8888) -> None:
        """Init method to gather IP, group, and port."""
        self._ip = ip
        self._port = port
        self._group = group
        _LOGGER.debug("DreamScreen initialized")

    @staticmethod
    def _crc8(data: bytearray) -> bytes:
        import crc8
        hash = crc8.crc8()
        hash.update(data)
        return hash.digest()

    def _build_packet(self, option: int, value: list) -> bytearray:
        if type(value) != list:
            raise TypeError("value type {} != list"
                            .format(type(value)))

        # Based on group address by looking at sample Android code
        # 0b00100001 -> 0x21 -> 33
        # 0b00010001 -> 0x11 -> 17
        flags = 17 if self._group == 0 else 33
        resp = [252, len(value) + 5, self._group, flags, 3, option]
        resp.extend(value)
        resp.extend(self._crc8(bytearray(resp)))
        return bytearray(resp)

    def _send_packet(self, packet: bytearray) -> None:
        if type(packet) != bytearray:
            raise TypeError("packet type {} != bytearray"
                            .format(type(packet)))
        self._socket.sendto(packet, (self._ip, self._port))

    def set_mode(self, mode: int) -> None:
        """Set DreamScreen mode.

        0: Off
        1: Video
        2: Music
        3: Ambient
        """
        mode = max(min(mode, 3), 0)
        packet = self._build_packet(1, [mode])
        self._send_packet(packet)
        _LOGGER.debug("set mode {}".format(mode))

    def set_hdmi_source(self, hdmi_source: int) -> None:
        """Set DreamScreen HDMI source.

        0: HDMI Source 1
        1: HDMI Source 2
        2: HDMI Source 3
        """
        hdmi_source = max(min(hdmi_source, 2), 0)
        packet = self._build_packet(32, [hdmi_source])
        self._send_packet(packet)
        _LOGGER.debug("set hdmi_source {}".format(hdmi_source))

    def set_brightness(self, brightness: int) -> None:
        """Set DreamScreen brightness.

        Brightness values between 0 and 100
        """
        brightness = max(min(brightness, 100), 0)
        packet = self._build_packet(2, [brightness])
        self._send_packet(packet)
        _LOGGER.debug("set brightness {}".format(brightness))

    def set_ambiance_mode(self, mode: int) -> None:
        """Set DreamScreen ambiance mode.

        Not sure on clamping/all values
        0: RGB Color
        1: Scenes (Required for setting scene below)
        """
        mode = max(min(mode, 1), 0)
        packet = self._build_packet(8, [mode])
        self._send_packet(packet)
        _LOGGER.debug("set ambiance mode {}".format(mode))

    def set_ambiance_scene(self, scene: int) -> None:
        """Set DreamScreen ambient scene.

        Scenes from the app:
        0: Random Colors
        1: Fireside
        2: Twinkle
        3: Ocean
        4: Pride
        5: July 4th
        6: Holiday
        7: Pop
        8: Enchanted Forrest
        """
        scene = max(min(scene, 8), 0)
        packet = self._build_packet(13, [scene])
        self._send_packet(packet)
        _LOGGER.debug("set scene {}".format(scene))

    def set_ambiance_color(self,
                           red: int=0,
                           green: int=0,
                           blue: int=0) -> None:
        """Set DreamScreen ambient color."""
        red = max(min(red, 255), 0)
        green = max(min(green, 255), 0)
        blue = max(min(blue, 255), 0)
        packet = self._build_packet(5, [red, green, blue])
        self._send_packet(packet)
        _LOGGER.debug("set ambiance_color R{} G{} B{}".
                      format(red, green, blue))

if __name__ == '__main__':
    ds = DreamScreen(ip="172.16.16.76", group=0)
    ds.set_mode(1)
