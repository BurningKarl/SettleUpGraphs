# -*- encoding: utf-8 -*-
import csv
from typing import List, Iterable, Set, Mapping
from dataclasses import dataclass
from collections import namedtuple, defaultdict
from functools import partial
from datetime import datetime

# Columns in the SettleUp export file
TRANSACTION_COLUMNS = ['who_paid', 'amount', 'currency', 'for_whom',
                       'split_amounts', 'purpose', 'category', 'date_time',
                       'exchange_rate', 'converted_amount', 'type', 'receipt']

TABLE_COLUMN_NAMES = ['Purpose', 'Date & time', 'Category']


class RawTransaction(namedtuple('Transaction', TRANSACTION_COLUMNS)):
    '''An unprocessed SettleUp transaction in the export format'''
    
    @staticmethod
    def from_file(filename: str): # -> Iterable[RawTransaction]
        with open(filename, 'r', encoding='utf8', newline='') as f:
            reader = csv.reader(f)
            next(reader) # skip the header
            for row in reader:
                yield RawTransaction(*row)

@dataclass
class Transaction:
    '''A SettleUp transaction'''
    purpose: str
    category: str
    date_time: datetime
    spent_amounts: dict
    paid_amounts: dict
    
    @staticmethod
    def from_raw_transaction(raw: RawTransaction): # -> Transaction
        spent_names = raw.for_whom.split(';')
        spent_amounts = map(float, raw.split_amounts.split(';'))
        paid_names = raw.who_paid.split(';')
        paid_amounts = map(float, raw.amount.split(';'))

        if raw.exchange_rate.strip():
            exchange_rate = float(raw.exchange_rate.split(':')[1])
            spent_amounts = [amount/exchange_rate for amount in spent_amounts]
            paid_amounts = [amount/exchange_rate for amount in paid_amounts]
            
        date_time = datetime.strptime(raw.date_time, '%Y-%m-%d %H:%M:%S')

        return Transaction(raw.purpose, raw.category, raw.date_time, 
                           dict(zip(spent_names, spent_amounts)),
                           dict(zip(paid_names, paid_amounts)))

@dataclass                           
class ExpenseSummaryMatrix:
    '''Matrix of the sum of expenses by category and name'''
    # expenses[category][name] is the sum of all the expenses of this person 
    # in this category
    expenses: Mapping[str, Mapping[str, float]]
    
    @staticmethod
    def from_transactions(transactions: Iterable[Transaction], 
                          paid=False): # -> ExpenseSummaryMatrix
        expenses = defaultdict(partial(defaultdict, float))
        if paid:
            for transaction in transactions:
                for name, amount in transaction.paid_amounts.items():
                    expenses[transaction.category][name] += amount
        else:
            for transaction in transactions:
                for name, amount in transaction.spent_amounts.items():
                    expenses[transaction.category][name] += amount
            
        return ExpenseSummaryMatrix(expenses)
        
    def names(self) -> Set[str]:
        names = set()
        for category in self.expenses:
            names |= self.expenses[category].keys()
        return names
        
    def totals_by_category(self) -> Mapping[str, float]:
        return {category:sum(self.expenses[category].values()) 
                for category in self.expenses.keys()}
        
        
            
