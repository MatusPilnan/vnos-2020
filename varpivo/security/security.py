import logging
import random
import string

from varpivo.config import config
from varpivo.utils import Event
from varpivo.utils.librarian import load_security, save_security, discard_security


class Security:
    __instance = None

    @staticmethod
    def get_instance():
        if Security.__instance is None:
            Security.__instance = Security()

        return Security.__instance

    def __init__(self) -> None:
        self.logger = logging.getLogger('quart.app')
        self.brew_session_code, self.code_save_time = load_security()
        if self.brew_session_code is None:
            self.generate_code()
        else:
            self.logger.info(f'Loaded brew session security code: {self.brew_session_code}')

    def generate_code(self):
        self.brew_session_code = ''.join(random.choices(string.ascii_uppercase + string.digits,
                                                        k=config.BREW_SESSION_CODE_LENGTH))
        self.logger.info(f'New brew session security code: {self.brew_session_code}')
        self.save_code()

    @staticmethod
    async def security_observer(event: Event):
        if event.event_type[0] == event.BREW_SESSION_STARTED:
            Security.get_instance().save_code()
        elif event.event_type[0] == event.BREW_SESSION_FINISHED:
            Security.get_instance().discard_code()

    def save_code(self):
        save_security(self)

    @staticmethod
    def discard_code():
        discard_security()

    @staticmethod
    def check_code(code):
        return code == Security.get_instance().brew_session_code
