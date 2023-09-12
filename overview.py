import csv
from locale import LC_ALL, setlocale, str as locale_str
from settleup import RawTransaction, Transaction
from zoneinfo import ZoneInfo

setlocale(LC_ALL, "de_DE.UTF-8")

raw_transactions = RawTransaction.from_file("transactions.csv")
transactions = list(
    (Transaction.from_raw_transaction(raw), raw.receipt)
    for raw in raw_transactions
    if raw.type != "transfer"
)

names = ["Alice", "Bob"]

with open("overview.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(
        ["Purpose", "Amount", "Date & Time"]
        + ["Spent"] * len(names)
        + ["Paid"] * len(names)
        + ["Receipt"]
    )
    writer.writerow(["", "", ""] + names + names + [""])
    for transaction, receipt in transactions:
        writer.writerow(
            [
                transaction.purpose,
                locale_str(sum(transaction.spent_amounts.values())),
                transaction.date_time.astimezone()
                .astimezone(ZoneInfo("Europe/Berlin"))
                .replace(tzinfo=None),
            ]
            + [locale_str(transaction.spent_amounts.get(name, 0)) for name in names]
            + [locale_str(transaction.paid_amounts.get(name, 0)) for name in names]
            + [receipt]
        )
