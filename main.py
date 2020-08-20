import math
import i18n
import locale
import argparse
from settleup import RawTransaction, Transaction, ExpenseSummaryMatrix

# Backends
import bokeh_graphs
import pgf_graphs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create beautiful graphs of your expenses in SettleUp"
    )

    parser.add_argument(
        "-b",
        action="store",
        dest="backend",
        default="bokeh",
        choices=["bokeh", "pgf"],
        help="The backend: bokeh (html output) or pgf (pdf output)",
    )
    parser.add_argument(
        "-e",
        "--emojis",
        action="store_false",
        dest="translate_emojis",
        help="Disables translation from emojis to text",
    )
    parser.add_argument(
        "-l",
        action="store",
        metavar="LANG",
        dest="language",
        default=None,
        help="The language (e.g. en, de), fallback is English",
    )
    parser.add_argument(
        "-i",
        action="store",
        metavar="INPUT_FILE",
        dest="input_file",
        default="transactions.csv",
        help='The input file (default: "transactions.csv")',
    )
    parser.add_argument(
        "-o",
        action="store",
        metavar="OUTPUT_FILE",
        dest="output_file",
        default=None,
        help='The output file (default: "SettleUpGraphs(.html|.pdf)")',
    )
    arguments = parser.parse_args()

    raw_transactions = RawTransaction.from_file(arguments.input_file)
    transactions = (
        Transaction.from_raw_transaction(raw)
        for raw in raw_transactions
        if raw.type != "transfer"
    )
    summary = ExpenseSummaryMatrix.from_transactions(transactions)

    i18n.load_path.append("translations")
    preferred_locale = locale.setlocale(locale.LC_MESSAGES, "")
    i18n.set("locale", arguments.language or preferred_locale[:2])
    # 'en' is automatically set as a fallback

    if arguments.translate_emojis:
        # Translate the emojis to text
        summary.expenses = {
            i18n.t("emoji." + (category or "none")): amounts
            for category, amounts in summary.expenses.items()
        }

    if arguments.backend == "bokeh":
        arguments.output_file = arguments.output_file or "SettleUpGraphs.html"
        bokeh_graphs.output_graphs(arguments.output_file, summary)
    elif arguments.backend == "pgf":
        arguments.output_file = arguments.output_file or "SettleUpGraphs.pdf"
        pgf_graphs.output_graphs(arguments.output_file, summary)

    print("Done!")
