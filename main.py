import math
import argparse
from settleup import RawTransaction, Transaction, ExpenseSummaryMatrix
from bokeh.io import save
from bokeh.resources import CDN, INLINE
from bokeh.layouts import gridplot
from bokeh.palettes import Category10, Category20
from bokeh.plotting import figure
from bokeh.plotting.figure import Figure
from bokeh.transform import cumsum

TITLE_FONT_SIZE = '20pt'
LEGEND_FONT_SIZE = '15pt'

def color_palette(number_of_elements: int):
    if number_of_elements <= 10:
        return Category10[number_of_elements]
    elif number_of_elements <= 20:
        return Category20[number_of_elements]
    else:
        raise ValueError('More than 20 colors are currently not supported')

def pie_chart_by_category(summary: ExpenseSummaryMatrix) -> Figure:
    totals = summary.totals_by_category()
    categories = list(totals.keys())
    
    data_source = {
        'category': categories,
        'amount': [totals[category] for category in categories],
        'angle': [totals[category] / sum(totals.values()) * 2*math.pi
                  for category in categories]
    }
    data_source['color'] = color_palette(len(categories))
                                  
    p = figure(title='Expenses by category', toolbar_location=None,
               tools='hover', tooltips='@category: @amount{0,0.00}',
               x_range=(-1, 1.3), width=600, height=600)
                 
    p.wedge(x=0, y=0, radius=0.9,
            start_angle=cumsum('angle', include_zero=True), 
            end_angle=cumsum('angle'),
            line_color="white", fill_color='color', 
            legend_field='category', source=data_source)
            
    # Increase the font size
    p.title.text_font_size = TITLE_FONT_SIZE
    p.legend.label_text_font_size = LEGEND_FONT_SIZE
    
    # Make the graph more beautiful
    p.axis.axis_label=None # Hide the axis labels
    p.axis.visible=False # Hide the axes
    p.grid.grid_line_color = None # Hide the grid
    p.outline_line_color = None # Hide the outline

    return p 

def bar_chart_by_name(summary: ExpenseSummaryMatrix) -> Figure:
    totals = summary.totals_by_category()
    categories = list(totals.keys())
    
    data_source = {
        'category': categories,
        'amount': [totals[category] for category in categories],
    }
    data_source['color'] = color_palette(len(categories))
    
    p = figure(title='Expenses by category', toolbar_location=None, 
               tools='hover', tooltips='@amount{0,0.00}',
               x_range=categories, width=600, height=600)
    
    p.vbar(x='category', top='amount', width=0.8,
           color='color', source=data_source)
    
    # Increase the font size
    p.title.text_font_size = TITLE_FONT_SIZE
    p.axis.major_label_text_font_size = LEGEND_FONT_SIZE
    
    # Make the graph more beautiful
    p.y_range.start = 0 # Let the bars start at the bottom
    p.x_range.range_padding = 0.1 # Add horizontal padding
    p.xgrid.grid_line_color = None # Hide the vertical grid lines
    p.axis.minor_tick_line_color = None # Hide all minor ticks
    p.outline_line_color = None # Hide the outline
    
    return p

def stacked_bar_chart_by_name(summary: ExpenseSummaryMatrix) -> Figure:
    categories = list(summary.expenses)
    names = sorted(summary.names(), reverse=True)
    
    data_source = {'names': names}
    data_source.update({
        category:[summary.expenses[category][name] for name in names]
        for category in categories
    })
    data_source['color'] = color_palette(len(categories))
    
    p = figure(title='Expenses by person and category',
               toolbar_location=None,
               tools='hover', tooltips='$name: @$name{0,0.00}',
               y_range=names, width=1000, height=600)
    
    p.hbar_stack(categories, y='names', height=0.8,
                 color=color_palette(len(categories)),
                 source=data_source)
                 
    # Increase the font size
    p.title.text_font_size = TITLE_FONT_SIZE
    p.axis.major_label_text_font_size = LEGEND_FONT_SIZE
    
    # Make the graph more beautiful    
    p.x_range.start = 0 # Let the bars start at the left
    p.y_range.range_padding = 0.1 # Add vertical padding
    p.ygrid.grid_line_color = None # Hide the horizontal grid lines
    p.axis.minor_tick_line_color = None # Hide all minor ticks
    p.outline_line_color = None # Hide the outline
    
    return p


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create beautiful graphs of your expenses in SettleUp')

    parser.add_argument('-i', action='store', metavar='INPUT_FILE', 
                        dest='input_file', default='transactions.csv', 
                        help='The input file (default: "transactions.csv")')
    parser.add_argument('-o', action='store', metavar='OUTPUT_FILE', 
                        dest='output_file', default='SettleUpGraphs.html',
                        help='The output file '
                             '(default: "SettleUpGraphs.html")')
    #parser.add_argument('-g', action='store', nargs='+', metavar='GRAPH', 
    #                    dest='graphs', default=[],
    #                    help='The graphs included in the output ' 
    #                         '(default: my favorite ones)')
    arguments = parser.parse_args()
    
    raw_transactions = RawTransaction.from_file(arguments.input_file)
    transactions = (Transaction.from_raw_transaction(raw) 
                    for raw in raw_transactions
                    if raw.type != 'transfer')
    summary = ExpenseSummaryMatrix.from_transactions(transactions)
    
    # Sort the categories from highest to lowest amount of expenses
    totals = summary.totals_by_category()
    summary.expenses = {
        k:v for k, v in sorted(summary.expenses.items(), 
                               key=lambda item: totals[item[0]],
                               reverse=True)
    }

    grid = gridplot([[pie_chart_by_category(summary),
                      bar_chart_by_name(summary),
                      stacked_bar_chart_by_name(summary)]])
    save(grid, title='SettleUpGraphs', filename=arguments.output_file,
         resources=INLINE)

    print('Done!')
