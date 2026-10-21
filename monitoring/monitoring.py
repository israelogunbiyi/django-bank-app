from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Q

from .models import Transaction

HIGH_VALUE_THRESHOLD = Decimal("10000000")


def monitor_transactions() -> list[tuple[str, Decimal, str]]:
    flagged_transactions = []

    transactions = Transaction.objects.filter(
        Q(processed=False) | Q(amount__gte=HIGH_VALUE_THRESHOLD),
        flagged=False,
    ).order_by("created_at")[:500]

    for txn in transactions:
        with transaction.atomic():
            txn = Transaction.objects.select_for_update().get(id=txn.id)

            if txn.flagged or (
                txn.processed and txn.amount < HIGH_VALUE_THRESHOLD
            ):
                continue

            recent_transactions = Transaction.objects.filter(
                customer=txn.customer,
                created_at__gte=txn.created_at - timedelta(minutes=10),
                created_at__lte=txn.created_at,
            )
            recent_count = recent_transactions.count()

            if txn.amount >= HIGH_VALUE_THRESHOLD:
                txn.flagged = True
                txn.save(update_fields=["flagged"])
                flagged_transactions.append(
                    (
                        txn.reference,
                        txn.amount,
                        f"Amount meets or exceeds ₦{HIGH_VALUE_THRESHOLD}",
                    )
                )
            elif recent_count > 5:
                newly_flagged = list(
                    recent_transactions.filter(flagged=False).values_list(
                        "reference",
                        "amount",
                    )
                )
                recent_transactions.filter(flagged=False).update(flagged=True)
                flagged_transactions.extend(
                    (
                        reference,
                        amount,
                        "More than five transactions within ten minutes",
                    )
                    for reference, amount in newly_flagged
                )
            else:
                txn.processed = True
                txn.save(update_fields=["processed"])

    return flagged_transactions

