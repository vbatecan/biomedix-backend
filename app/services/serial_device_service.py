import logging

from app.core import config

logger = logging.getLogger(__name__)

try:
    import serial
    from serial import SerialException
    from serial.tools import list_ports
except ImportError:  # pragma: no cover - handled at runtime when dependency is missing
    serial = None
    SerialException = Exception
    list_ports = None


class SerialDeviceService:
    @staticmethod
    def detect_serial_devices() -> list[str]:
        if list_ports is None:
            logger.warning("pyserial is not installed; skipping serial device detection.")
            return []

        devices = [port.device for port in list_ports.comports() if port.device]
        logger.info("Detected %d serial device(s): %s", len(devices), devices)
        return devices

    @staticmethod
    def send_to_all_devices(data: str = "open") -> int:
        if serial is None:
            logger.warning("pyserial is not installed; cannot send serial payload.")
            return 0

        devices = SerialDeviceService.detect_serial_devices()
        if not devices:
            logger.info("No serial devices available for payload '%s'.", data)
            return 0

        payload = data.encode("utf-8")
        sent_count = 0

        for device in devices:
            try:
                with serial.Serial(
                    port=device,
                    baudrate=config.SERIAL_BAUD_RATE,
                    timeout=config.SERIAL_TIMEOUT_SECONDS,
                    write_timeout=config.SERIAL_WRITE_TIMEOUT_SECONDS,
                ) as serial_conn:
                    serial_conn.write(payload)
                    serial_conn.flush()
                    sent_count += 1
                    logger.info("Sent payload '%s' to serial device %s", data, device)
            except (SerialException, OSError) as exc:
                logger.error(
                    "Failed to send payload '%s' to serial device %s: %s",
                    data,
                    device,
                    exc,
                )

        return sent_count
