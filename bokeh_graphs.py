import math

import i18n
from bokeh.io import save
from bokeh.layouts import gridplot
from bokeh.palettes import Category10, Category20
from bokeh.plotting import figure
from bokeh.plotting.figure import Figure
from bokeh.resources import INLINE
from bokeh.transform import cumsum

from settleup import ExpenseSummaryMatrix

TITLE_FONT_SIZE = "20pt"
LEGEND_FONT_SIZE = "15pt"


def color_palette(number_of_elements: int):
    if number_of_elements <= 10:
        return Category10[number_of_elements]
    if number_of_elements <= 20:
        return Category20[number_of_elements]
    raise ValueError("More than 20 colors are currently not supported")


def pie_chart_by_category(summary: ExpenseSummaryMatrix) -> Figure:
    totals = summary.totals_by_category()
    categories = list(totals.keys())

    data_source = {
        "category": categories,
        "amount": [totals[category] for category in categories],
        "angle": [
            totals[category] / sum(totals.values()) * 2 * math.pi
            for category in categories
        ],
    }
    data_source["color"] = color_palette(len(categories))

    chart = figure(
        title=i18n.t("title.by_category"),
        toolbar_location=None,
        tools="hover",
        tooltips="@category: @amount{0,0.00}",
        x_range=(-1.7, 2.2),
        width=1000,
        height=600,
    )

    chart.wedge(
        x=0,
        y=0,
        radius=0.9,
        start_angle=cumsum("angle", include_zero=True),
        end_angle=cumsum("angle"),
        line_color="white",
        fill_color="color",
        legend_field="category",
        source=data_source,
    )

    # Increase the font size
    chart.title.text_font_size = TITLE_FONT_SIZE
    chart.legend.label_text_font_size = LEGEND_FONT_SIZE

    # Make the graph more beautiful
    chart.axis.axis_label = None  # Hide the axis labels
    chart.axis.visible = False  # Hide the axes
    chart.grid.grid_line_color = None  # Hide the grid
    chart.outline_line_color = None  # Hide the outline

    return chart


def bar_chart_by_category(summary: ExpenseSummaryMatrix) -> Figure:
    totals = summary.totals_by_category()
    categories = list(totals.keys())

    data_source = {
        "category": categories,
        "amount": [totals[category] for category in categories],
    }
    data_source["color"] = color_palette(len(categories))

    chart = figure(
        title=i18n.t("title.by_category"),
        toolbar_location=None,
        tools="hover",
        tooltips="@amount{0,0.00}",
        x_range=categories,
        width=1000,
        height=600,
    )

    chart.vbar(x="category", top="amount", width=0.8, color="color", source=data_source)

    # Increase the font size
    chart.title.text_font_size = TITLE_FONT_SIZE
    chart.axis.major_label_text_font_size = LEGEND_FONT_SIZE

    # Make the graph more beautiful
    chart.y_range.start = 0  # Let the bars start at the bottom
    chart.x_range.range_padding = 0.1  # Add horizontal padding
    chart.xgrid.grid_line_color = None  # Hide the vertical grid lines
    chart.axis.minor_tick_line_color = None  # Hide all minor ticks
    chart.outline_line_color = None  # Hide the outline

    return chart


def stacked_bar_chart_by_name(summary: ExpenseSummaryMatrix) -> Figure:
    categories = list(summary.expenses)
    names = sorted(summary.names())

    data_source = {"names": names}
    data_source.update(
        {
            category: [summary.expenses[category][name] for name in names]
            for category in categories
        }
    )

    chart = figure(
        title=i18n.t("title.by_name_by_category"),
        toolbar_location=None,
        tools="hover",
        tooltips="$name: @$name{0,0.00}",
        x_range=names,
        width=1000,
        height=600,
    )

    chart.vbar_stack(
        categories,
        x="names",
        width=0.8,
        color=color_palette(len(categories)),
        source=data_source,
    )

    # Increase the font size
    chart.title.text_font_size = TITLE_FONT_SIZE
    chart.axis.major_label_text_font_size = LEGEND_FONT_SIZE

    # Make the graph more beautiful
    chart.y_range.start = 0  # Let the bars start at the bottom
    chart.x_range.range_padding = 0.1  # Add horizontal padding
    chart.xgrid.grid_line_color = None  # Hide the vertical grid lines
    chart.axis.minor_tick_line_color = None  # Hide all minor ticks
    chart.outline_line_color = None  # Hide the outline

    return chart


def output_graphs(filename: str, summary: ExpenseSummaryMatrix) -> None:
    # Sort the categories from highest to lowest amount of expenses
    totals = summary.totals_by_category()
    summary.expenses = dict(
        sorted(summary.expenses.items(), key=lambda item: totals[item[0]], reverse=True)
    )

    grid = gridplot(
        [
            [pie_chart_by_category(summary)],
            [bar_chart_by_category(summary)],
            [stacked_bar_chart_by_name(summary)],
        ]
    )
    save(grid, title="SettleUpGraphs", filename=filename, resources=INLINE)
