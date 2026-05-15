from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
import logging
from typing import Callable

from loans.app.ports.loan_repository import LoanRepository
from loans.app.ports.email_service import EmailServiceInterface

logger = logging.getLogger(__name__)

TEMPLATE_ID = "templateId651"


class NotifyUsers3DaysBeforeLoanDue():
    """
        Notifier les utilisateurs 3 jrs avant l'échéance de l'emprunt
    """

    def __init__(self, loan_repository: LoanRepository, email_service: EmailServiceInterface, max_workers: int = 2,):
        self.email_service = email_service
        self.loan_repository = loan_repository
        self.max_workers = max_workers

    def execute(self) -> None:
        emails = self.loan_repository.get_borrower_emails_with_loan_due_in_3_days(
            date.today())

        if not emails:
            return

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self.email_service.send_email_with_template,
                    str(email),
                    TEMPLATE_ID,
                    {"date": str(date.today())},
                ): email
                for email in emails
            }

            for future in as_completed(futures):
                email = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(
                        f"Failed to send notification to {email}: {e}")
                    pass
