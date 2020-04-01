import math
import argparse
from settleup import RawTransaction, Transaction, ExpenseSummaryMatrix

# Backends
import bokeh_graphs
import pgf_graphs

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create beautiful graphs of your expenses in SettleUp')

    parser.add_argument('-b', action='store', metavar='BACKEND',
                        dest='backend', default='bokeh',
                        choices=['bokeh', 'pgf'],
                        help='The backend: bokeh (html output) '
                             'or pgf (pdf output)')
    parser.add_argument('-i', action='store', metavar='INPUT_FILE', 
                        dest='input_file', default='transactions.csv', 
                        help='The input file (default: "transactions.csv")')
    parser.add_argument('-o', action='store', metavar='OUTPUT_FILE', 
                        dest='output_file', default=None,
                        help='The output file '
                             '(default: "SettleUpGraphs(.html|.pdf)")')
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
    
    if arguments.backend == 'bokeh':
        arguments.output_file = arguments.output_file or 'SettleUpGraphs.html'
        bokeh_graphs.output_graphs(arguments.output_file, summary)
    elif arguments.backend == 'pgf':
        arguments.output_file = arguments.output_file or 'SettleUpGraphs.pdf'
        pgf_graphs.output_graphs(arguments.output_file, summary)

    print('Done!')
