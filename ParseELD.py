#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 16:31:57 2020

@author: zoakes
"""

from io import StringIO
import pandas as pd

class ELDMonitor:
    default_path = '/Users/zoakes/Desktop/eld_output.txt'
    EXIT_DICT = { 
        'ES_PR30': [-300, 100, 3],
        'RTY_PR30': [-225, 70, 3]
    }
    
    def __init__(self, path=None, ts_idx = False):
        if path is None:
            self.path = self.default_path
        else:
            self.path = path
            
        try:
            self.file = open(self.path)
        except Exception as e:
            raise e
            
        self.df = self.parse_eld_file(ts_index = ts_idx)
        self.symbol_dfs = {} 
        self.strategy_dfs = {}
        
    '''  
    Uneeded complexity, just define instance var of opened file and Raise path error @ Init -- Fail Quick.
    @property
    def path(self):
        return self.path
    
    @path.setter
    def path(self, new_path):
        print(new_path[-4:])
        if new_path[-4:] != '.txt':
            raise f'Error -- Must be a txt file + path -- Ex: /Users/zoakes/Desktop/eld_output.txt'
    '''

    #Could make this a df @property... get would parse, set would change path?
    def parse_eld_file(self, path_and_file=None, ts_index = False):
        '''
        Referenced Parse Text File to Pandas in StackOverflow:
        https://stackoverflow.com/questions/44288169/parse-text-file-python-and-covert-to-pandas-dataframe
        '''
        if path_and_file is None:
            path_and_file = self.path
        try:
            file = open(path_and_file)
            
        except Exception as e:
            print('Path Incorrect -- Please check path_and_file input -- Ex: /Users/zoakes/Desktop/eld_output.txt')
            raise e

        parse = [line.split(',') for line in file.read().split('\n')]

        parsed = parse[0::2] #Remove Blank Lists... (What are these?)
        col, values = parsed[0], parsed[1:]
        assert len(values) + 1 == len(parsed), 'Warning -- Underflow'

        df = pd.DataFrame(values, columns = col)
        assert df.shape[0] + 1 == len(parsed), 'Warning -- DF Dropped a row...'

        if ts_index:
            df.set_index('TimeStamp',inplace=True)
        self.df = df
        return df
    
    def reindex_timestamp(self):
        self.df = self.df.set_index('TimeStamp',inplace=True)
        return self.df
    
    #Build out to sort by TimeStamp - TimeStamp...
    def get_trade(self, idx, TimeStamp=None, df = None):
        #if df is None:
        #    df = self.df
        if TimeStamp:
            df = self.reindex_timestamp()
            return df.loc[TimeStamp]
        else:
            return self.df.iloc[idx]
    
    def get_strategy_trades(self, StrategyName, df = None):
        if df is None:
            df = self.df
        return df.loc[df['StrategyName'] == StrategyName]
    
    def get_trades_by_symbol(self, Symbol, df = None):
        if df is None:
            df = self.df
        return df.loc[df.Symbol == Symbol]
    
    
    def get_date_range(self, beg_str, end_str, df = None):
        '''
        format for strings: '2019-10-01'
        Maybe should be >=  <= (cur: > and <= ) 
        '''
        if df is None: 
            df = self.df
        df.TimeStamp = pd.to_datetime(df.TimeStamp) #df.TimeStamp.to_datetime()
        df = df[(df['TimeStamp'] > beg_str) & (df['TimeStamp'] <= end_str)] #Maybe should be >= and <= ?
        return df 

    
    #Need to test further, but looks to be working correctly -- MAY need to do a temp df, like self.view_df ... which tracks queries and changes, 
    #then can return to self.df (by parse -- or save base df as class var?)
    #ORR -- a dict of df's like in modular py... by symbol ? 
    def multi_query(self, beg_str = None, end_str = None, Symbol = None, Strategy = None):
        if Strategy:
            df = self.get_strategy_trades(Strategy)
        if Symbol:
            df = self.get_trades_by_symbol(Symbol)
        if beg_str and end_str:
            df = self.get_date_range(beg_str, end_str)
        return df
    
    
    '''MAYBE just ADD ALL to symbol / strategy df dicts? -- whenever new one, just ADD to it.'''
    def make_df_dict(self,symbol_list=None,strategies=None):
        '''NOT consecutive - One or Other!! (currently)'''
        if symbol_list:
            if len(symbol_list) > 1:
                for sym in symbol_list:
                    self.symbol_dfs[sym] = self.get_trades_by_symbol(sym)
            else:
                self.symbol_dfs[symbol_list[0]] = self.get_trades_by_symbol(symbol_list[0]) 
            return self.symbol_dfs
        
        if strategies:
            if len(strategies) > 1:
                for sys in strategies:
                    self.strategy_dfs[sys] = self.get_strategy_trades(sys)
            else:
                self.strategy_dfs[strategies[0]] = self.get_strategy_trades(strategies[0])
            return self.strategy_dfs
        

                
            
        
    
    def rogue_search(self, symbols=None, strategies=None):
        flagged = []
        definite = []
                
        dct = {} 
        if strategies:
            strat_not_in = [symbol for symbol in symbols if symbol not in self.strategy_dfs]
            if strat_not_in:
                dct = self.make_df_dict(strat_not_in)
                #print(dct)
                
                #missing = [sys for sys in strategies if sys not in self.EXIT_DICT] SL + TGT in DF!!!
                #Block is NOT tested... not enough data to test yet.
                if symbols:
                    #PArse only keys where first few letters of strategy name == symbol ! ex ES , RT, NQ, 
                    match_symbols = {key:value for key, value in dct.items() if key[0:3] in symbols}
                    #print(match_symbols)
                    dct = match_symbols
                    
            dct = {key:value for key, value in dct.items() if key in strategies}
                    

        if symbols:
            not_in = [symbol for symbol in symbols if symbol not in self.symbol_dfs]
            if not_in:
                dct = self.make_df_dict(not_in) 
                #print(dct)
            #Filter down to only relevant dfs....
            dct = {key:value for key, value in dct.items() if key in symbols}

        #for sdf in get_trades_by_symbol()
        #for sdf in get_trades_by_strategy
        #if strategies:
        #    dfs = [self.get_strategy_trades(strat) for strat in strategies]
        
        #if symbols: ...
        #    dfs = [self.get_trades_by_symbol(symbol) for symbol in symbols]

        
        for k,v in dct.items(): #Might need another loop or query for each strategy?
            if v.shape[0] % 2 == 0:
                continue
                
            #Also can query entries v exits...
            #print(v.Action)
            exits = v.loc[v['Action'] == 'Exit']
            entries = v.loc[v['Action'] == 'Entry'] 
            if entries.shape[0] == exits.shape[0]:
                continue
                
            #Add More complex testing here... Stop + Target ...
            
            #If live PNL < Stop loss -- DEFINITE rogue.
            if v.LivePNL.iloc[0] <  -1 * v['SL$'].iloc[0]:
                print(k,v.LivePNL.iloc[0], ' < ', v['SL$'].iloc[0])
                definite.append(k)

            #if v.OpenPNL > v.TGT$:
            #if v.LivePNL > v['TGT$']: -- No TGT I see?
                #flagged.append(k)

                
            #if v.BSE > v.TmExMax:
            #    flagged.append(k)
            #    definite.append(k)
            
        return definite, flagged
                
        
        
'''
Ideas: (For self.DF)
Current: Include optional df argument, to CHAIN commands -- but I think this is dumb / unclear.

-Argument to PERSIST/Commit changes in methods (Permanent, or No)

-@property type methods for DF: 
    Getter (w Arg -- Fresh or Curr) -- Queries fresh one
    Setter (To Commit or Not?)
    View?
    
- 2 Seperate variables --  + Properties ! ** I Like this !  [self.DF, self.df]  OR self.df self.df0
self.DF and self.df ? DF is permanent, not changed -- df is changed, queried, viewed, filtered

Lets try them out, pick the best one? Play with it, try to implement them : )


'''    
    

