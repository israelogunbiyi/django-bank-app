
from django.core.management.base import BaseCommand
from monitoring.monitoring import monitor_transactions

class Command(BaseCommand):
    help = "Monitor bank transactions"

    def handle(self, *args, **kwargs):
        flagged = monitor_transactions()

        if flagged:
            for reference, amount, reason in flagged:
                self.stdout.write(
                    f"Reference: {reference} | "
                    f"Amount: ₦{amount} | "
                    f"Reason: {reason}"
                )
        else:
            self.stdout.write("No transactions flagged.")

        self.stdout.write(
            self.style.SUCCESS(
                "Transaction monitoring completed."
            )
        )