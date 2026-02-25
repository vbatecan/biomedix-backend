import logging
import time

import serial
import serial.tools.list_ports

from app.core import config

logger = logging.getLogger(__name__)


class SerialService:
    @staticmethod
    def find_serial_port() -> str | None:
        """
        Auto-detects a serial port that might be the microcontroller.
        Prioritizes ports with 'Arduino', 'USB', or 'ACM' in their description/name.
        """
        ports = list(serial.tools.list_ports.comports())
        logger.info("Scanning %d serial ports...", len(ports))

        candidates: list[str] = []
        for port in ports:
            logger.debug(
                "Found port: %s - %s [%s]", port.device, port.description, port.hwid
            )
            # Heuristic detection for common USB-Serial chips (Arduino, FTDI, CH340, CP210x, etc.)
            description_lower = port.description.lower()
            if any(
                token in description_lower
                for token in ["arduino", "usb", "ch340", "ftdi", "cp210", "acm"]
            ):
                candidates.append(port.device)

        if candidates:
            logger.info("Auto-detected candidate ports: %s", candidates)
            return candidates[0]

        logger.warning("No likely candidate ports found via auto-detection.")
        return None

    @staticmethod
    def send_command(command: str) -> None:
        if not config.ENABLE_SERIAL_UNLOCK:
            logger.info("Serial unlock is disabled.")
            return

        target_port = config.SERIAL_PORT
        available_ports = [port.device for port in serial.tools.list_ports.comports()]

        if target_port not in available_ports:
            logger.info(
                "Configured port %s not found in available ports. Attempting auto-detection.",
                target_port,
            )
            detected = SerialService.find_serial_port()
            if detected:
                target_port = detected

        if not target_port:
            logger.error("No serial port available.")
            return

        try:
            logger.info(
                "Attempting to send '%s' to serial port %s...", command, target_port
            )
            with serial.Serial(target_port, config.SERIAL_BAUDRATE, timeout=1) as ser:
                # Wait for microcontroller reset if DTR toggles on serial open.
                time.sleep(2)
                ser.write(f"{command}\n".encode())
                logger.info("Sent '%s' to %s", command, target_port)
        except serial.SerialException as exc:
            logger.error("Serial communication error on %s: %s", target_port, exc)
        except Exception as exc:  # pragma: no cover - defensive fallback
            logger.error("Unexpected error in serial communication: %s", exc)
