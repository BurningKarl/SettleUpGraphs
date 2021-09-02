import i18n
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pgf import PdfPages
from matplotlib.figure import Figure

from settleup import ExpenseSummaryMatrix


# Taken from https://stackoverflow.com/questions/28931224/adding-value-labels-on-a-matplotlib-bar-chart
def add_value_labels(ax, spacing=5, last=None):
    """Add labels to the end of each bar in a bar chart.

    Arguments:
        ax (matplotlib.axes.Axes): The matplotlib object containing the axes
            of the plot to annotate.
        spacing (int): The distance between the labels and the bars.
    """

    # For each bar: Place a label
    patches = ax.patches if last is None else ax.patches[-last:]
    for rect in patches:
        # Get X and Y placement of label from rect.
        y_value = rect.get_y() + rect.get_height()
        x_value = rect.get_x() + rect.get_width() / 2

        # Use Y value as label and format number with one decimal place
        label = "{:.2f}".format(y_value)

        # Create annotation
        ax.annotate(
            label,  # Use `label` as label
            (x_value, y_value),  # Place label at end of the bar
            xytext=(0, spacing),  # Vertically shift label by `spacing`
            textcoords="offset points",  # Interpret `xytext` as offset in points
            ha="center",  # Horizontally center label
            va="bottom",
        )  # Vertically align label at the bottom

    # Slightly hacky solution
    ax.set_ylim(top=ax.get_ylim()[1] + spacing * 5)


def pie_chart_by_category(summary: ExpenseSummaryMatrix) -> Figure:
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    totals = summary.totals_by_category()
    categories = list(totals.keys())
    amounts = [totals[category] for category in categories]

    fig, ax = plt.subplots()
    patches, *_ = ax.pie(amounts, autopct="%1.1f%%")

    ax.set_title(i18n.t("title.by_category"))
    ax.legend(patches, categories)
    ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

    return fig


def bar_chart_by_category(summary: ExpenseSummaryMatrix) -> Figure:
    totals = summary.totals_by_category()
    categories = list(totals.keys())
    amounts = [totals[category] for category in categories]

    fig, ax = plt.subplots()
    ax.bar(categories, amounts)
    ax.set_title(i18n.t("title.by_category"))
    add_value_labels(ax)

    return fig


def stacked_bar_chart_by_name(summary: ExpenseSummaryMatrix) -> Figure:
    categories = list(summary.expenses)
    names = sorted(summary.names())

    amounts = np.array(
        [[0 for name in names]]
        + [
            [summary.expenses[category][name] for name in names]
            for category in categories
        ]
    )
    # Build the cumulative sums over the columns
    bar_heights = np.cumsum(amounts, axis=0)

    fig, ax = plt.subplots()
    for i, category in enumerate(categories):
        ax.bar(names, amounts[i + 1], bottom=bar_heights[i], label=category)
    ax.set_title(i18n.t("title.by_name_by_category"))
    add_value_labels(ax, last=len(names))
    ax.legend()

    return fig


def output_graphs(filename: str, summary: ExpenseSummaryMatrix) -> None:
    plt.rcParams["figure.figsize"] = (11.69, 8.27)  # A4 size

    # Sort the categories from highest to lowest amount of expenses
    totals = summary.totals_by_category()
    summary.expenses = dict(
        sorted(summary.expenses.items(), key=lambda item: totals[item[0]], reverse=True)
    )

    with PdfPages(filename, metadata={"Title": "SettleUpGraphs"}) as pdf:
        pdf.savefig(pie_chart_by_category(summary))
        pdf.savefig(bar_chart_by_category(summary))
        pdf.savefig(stacked_bar_chart_by_name(summary))
