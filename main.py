import math
import argparse
from settleup import RawTransaction, Transaction, ExpenseSummaryMatrix
from bokeh.io import save
from bokeh.resources import CDN
from bokeh.layouts import gridplot
from bokeh.palettes import Category10, Category20
from bokeh.plotting import figure
from bokeh.transform import cumsum

def color_palette(number_of_elements: int):
    if number_of_elements <= 10:
        return Category10[number_of_elements]
    elif number_of_elements <= 20:
        return Category20[number_of_elements]
    else:
        raise ValueError('More than 20 colors are currently not supported')

def pie_chart_by_category(summary: ExpenseSummaryMatrix):
    totals = summary.totals_by_category()

    # The categories sorted from highest to lowest amount of expenses
    categories = sorted(totals.keys(), key=totals.get, reverse=True)
    
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
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', 
            legend_field='category', 
            source=data_source)
    p.title.text_font_size = '20pt'
    p.legend.label_text_font_size = '15pt'
    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None           
    
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
    
    grid = gridplot([pie_chart_by_category(summary)], ncols=2)
    save(grid, title='SettleUpGraphs', filename=arguments.output_file,
         resources=CDN)

    print('Done!')
