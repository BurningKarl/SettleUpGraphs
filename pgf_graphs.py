import i18n
from settleup import ExpenseSummaryMatrix
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pgf import PdfPages
from matplotlib.figure import Figure
from matplotlib.ticker import StrMethodFormatter

def pie_chart_by_category(summary: ExpenseSummaryMatrix) -> Figure:
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    totals = summary.totals_by_category()
    categories = list(totals.keys())
    amounts = [totals[category] for category in categories]

    fig, ax = plt.subplots()
    patches, *_ = ax.pie(amounts)
    #optional arguments: labels=categories, autopct='%1.1f%%',
    
    ax.set_title(i18n.t('title.by_category'))
    ax.legend(patches, categories)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    return fig

def bar_chart_by_category(summary: ExpenseSummaryMatrix) -> Figure:
    totals = summary.totals_by_category()
    categories = list(totals.keys())
    amounts = [totals[category] for category in categories]

    fig, ax = plt.subplots()
    bars = ax.bar(categories, amounts)
    ax.set_title(i18n.t('title.by_category'))
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.0f}€'))
    
    return fig

def stacked_bar_chart_by_name(summary: ExpenseSummaryMatrix) -> Figure:
    categories = list(summary.expenses)
    names = sorted(summary.names())
    
    amounts = np.array([[0 for name in names]]
                       + [[summary.expenses[category][name] for name in names]
                          for category in categories])
    # Build the cumulative sums over the columns
    bar_heights = np.cumsum(amounts, axis=0) 
    
    fig, ax = plt.subplots()
    for i, category in enumerate(categories):
        ax.bar(names, amounts[i+1], bottom=bar_heights[i], label=category)
    ax.set_title(i18n.t('title.by_name_by_category'))
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.0f}€'))
    ax.legend()
    
    return fig


def output_graphs(filename: str, summary: ExpenseSummaryMatrix) -> None:
    plt.rcParams["figure.figsize"] = (11.69,8.27) # A4 size

    # Sort the categories from highest to lowest amount of expenses
    totals = summary.totals_by_category()
    summary.expenses = dict(
        sorted(summary.expenses.items(), key=lambda item: totals[item[0]], 
               reverse=True)
    )

    with PdfPages(filename, metadata={'title': 'SettleUpGraphs'}) as pdf:
        pdf.savefig(pie_chart_by_category(summary))
        pdf.savefig(bar_chart_by_category(summary))
        pdf.savefig(stacked_bar_chart_by_name(summary))

