from typing import Dict, Protocol


class EmailServiceInterface(Protocol):
    def send_email_with_template(self, email: str, template_id: str, params: Dict[str, str | int]) -> None:
        """In background"""
        raise NotImplementedError
