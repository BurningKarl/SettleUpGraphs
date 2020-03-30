import math
import argparse
from settleup import RawTransaction, Transaction, ExpenseSummaryMatrix
from bokeh.io import save
from bokeh.resources import CDN
from bokeh.layouts import gridplot
from bokeh.palettes import Category10, Category20
from bokeh.plotting import figure
from bokeh.plotting.figure import Figure
from bokeh.transform import cumsum

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
        'value': [totals[category] for category in categories],
        'angle': [totals[category] / sum(totals.values()) * 2*math.pi
                  for category in categories]
    }
    data_source['color'] = color_palette(len(categories))
                                  
    p = figure(title='Expenses by category', toolbar_location=None,
               tools='hover', tooltips='@category: @value{0,0.00}', 
               x_range=(-1, 1.3))
                 
    p.wedge(x=0, y=0, radius=0.9,
            start_angle=cumsum('angle', include_zero=True), 
            end_angle=cumsum('angle'),
            line_color="white", fill_color='color', 
            legend_field='category', source=data_source)
            
    p.title.text_font_size = '20pt'
    p.legend.label_text_font_size = '15pt'
    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None           
    
    return p 

def bar_chart_by_name(summary: ExpenseSummaryMatrix) -> Figure:
    totals = summary.totals_by_category()
    categories = list(totals.keys())
    
    data_source = {
        'category': categories,
        'value': [totals[category] for category in categories],
    }
    data_source['color'] = color_palette(len(categories))
    
    p = figure(x_range=categories, title='Expenses by category',
               toolbar_location=None, tools='hover',
               tooltips='@category: @value{0,0.00}')
    
    p.vbar(x='category', top='value', width=0.9,
           color='color', source=data_source)
    
    p.title.text_font_size = '20pt'
    #p.legend.label_text_font_size = '15pt'
    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    #p.legend.location = "top_left"
    #p.legend.orientation = "vertical"
    
    return p

def stacked_bar_chart_by_name(summary: ExpenseSummaryMatrix) -> Figure:
    categories = list(summary.expenses)
    names = sorted(summary.names())
    
    data_source = {'names': names}
    data_source.update({
        category:[summary.expenses[category][name] for name in names]
        for category in categories
    })
    data_source['color'] = color_palette(len(categories))
    
    p = figure(x_range=names, title='Expenses by person and category',
               toolbar_location=None, tools='hover', tooltips='@names')
    
    p.vbar_stack(categories, x='names', width=0.9,
                 color=color_palette(len(categories)),
                 source=data_source, legend_label=categories)
                 
    p.title.text_font_size = '20pt'
    p.legend.label_text_font_size = '15pt'
    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    #p.legend.location = "top_left"
    p.legend.orientation = "vertical"
    
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

    grid = gridplot([pie_chart_by_category(summary),
                     bar_chart_by_name(summary),
                     stacked_bar_chart_by_name(summary)], ncols=1)
    save(grid, title='SettleUpGraphs', filename=arguments.output_file,
         resources=CDN)

    print('Done!')
