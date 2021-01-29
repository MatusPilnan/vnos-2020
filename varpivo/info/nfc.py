import asyncio
import json
import logging

from varpivo.config import config
from varpivo.info.system_info import SystemInfo


class NFCTagEmulator:
    __instance = None

    @staticmethod
    def get_instance():
        if NFCTagEmulator.__instance is None:
            try:
                NFCTagEmulator.__instance = NFCTagEmulator()
            except ModuleNotFoundError:
                NFCTagEmulator.__instance = NFCPlaceholder()

        return NFCTagEmulator.__instance

    def __init__(self) -> None:
        self.libnfc_proc = None
        self.logger = logging.getLogger('quart.app')
        self.ndef_update = False
        self.update_ndef_record()

        SystemInfo.add_observer(self.request_ndef_update, SystemInfo.ADDRESSES)

    def update_ndef_record(self):
        # noinspection PyUnresolvedReferences
        import ndef
        record = ndef.UriRecord(f"{config.FRONTEND_URL}"
                                f"?connections={json.dumps(SystemInfo.get_instance().addresses, separators=(',', ':'))}"
                                f"&brewSessionCode={SystemInfo.get_instance().brew_session_code}")

        with open(config.NDEF_FILE, 'wb') as f:
            for _ in ndef.message_encoder([record], f):
                pass
        self.ndef_update = False

    async def request_ndef_update(self, **kwargs):
        self.ndef_update = True
        self.logger.info('NDEF record update requested')
        await self.stop()

    async def run_nfc_tag_emulator(self):
        serve_nfc = True
        stdout, stderr = None, None
        while serve_nfc:
            if self.ndef_update:
                self.update_ndef_record()
            try:
                self.libnfc_proc = await asyncio.create_subprocess_exec('nfc-emulate-forum-tag4', config.NDEF_FILE,
                                                                        stdout=asyncio.subprocess.PIPE,
                                                                        stderr=asyncio.subprocess.PIPE)
                stdout, stderr = await self.libnfc_proc.communicate()
                code = self.libnfc_proc.returncode

                serve_nfc = (code == 1 or self.ndef_update)
                if serve_nfc and len(stdout) > 0 and b'Target Released' in stderr:
                    self.logger.info('NFC tag has been read successfully')

            except FileNotFoundError:
                serve_nfc = False
                self.logger.info('Unable to emulate NFC tag. Is libnfc installed?')

        self.logger.info(f'Stopping NFC emulation: {stdout}\n{stderr}')

    async def stop(self):
        if self.libnfc_proc and self.libnfc_proc.returncode is None:
            self.logger.info('Terminating NFC emulator process')
            self.libnfc_proc.terminate()
            await self.libnfc_proc.wait()


class NFCPlaceholder(NFCTagEmulator):
    # noinspection PyMissingConstructor
    def __init__(self) -> None:
        SystemInfo.add_observer(self.request_ndef_update, SystemInfo.ADDRESSES)
        self.logger = logging.getLogger('quart.app')
        self.logger.info(
            f"NDEF URL: {config.FRONTEND_URL}"
            f"?connections={json.dumps(SystemInfo.get_instance().addresses, separators=(',', ':'))}"
            f"&brewSessionCode={SystemInfo.brew_session_code}")
        self.logger.info('No NDEF module installed, NFC disabled')

    def __del__(self):
        pass

    async def run_nfc_tag_emulator(self):
        pass

    async def request_ndef_update(self, **kwargs):
        self.logger.info(
            f"NDEF URL updated: {config.FRONTEND_URL}?connections={json.dumps(SystemInfo.get_instance().addresses)}")

    async def stop(self):
        pass
