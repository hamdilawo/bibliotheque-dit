from time import sleep
from typing import Dict

from loans.app.ports.email_service import EmailServiceInterface


class BrevoEmailService(EmailServiceInterface):
    def __init__(self):
        self.__api_key: str = ""
        self.__api_base_url: str = ""

    def send_email_with_template(self, email: str,  template_id: str, params: Dict[str, str | int]):
        sleep(5)
        print(
            f"====\nEmail envoyé à {email}. 'template_id' {template_id}\nWith params: {params}\n===")
        # TODO: A Implementer
        return
