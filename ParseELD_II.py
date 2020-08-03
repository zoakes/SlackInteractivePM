#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 15:37:39 2020

@author: zoakes
"""

'''With PROPERTIES for DF'''
import datetime as dt
from datetime import datetime
import pandas as pd
from io import StringIO

class ELDMonitor:
    default_path = '/Users/zoakes/Desktop/eld_output.txt'
    EXIT_DICT = { 
        'ES_PR30': [-300, 100, 3],
        'RTY_PR30': [-225, 70, 3]
    }
    
    def __init__(self, path=None, ts_idx = False):
        if path is None:
            self._path = self.default_path
        else:
            self._path = path
            
        try:
            self.file = open(self.path)
        except Exception as e:
            raise e
            
        self.df = self.parse_eld_file(ts_index = ts_idx)
        self.df_init = self.df #Save initial
        self.symbol_dfs = {} 
        self.strategy_dfs = {}
              
     
    @property
    def path(self):
        return self._path
    
    @path.setter
    def path(self, new_path):
        #print(new_path[-4:])
        ext = new_path[-4:]
        if ext != '.txt' and ext != '.csv':
            print(f'Error -- Must be a txt file + path -- Ex: /Users/zoakes/Desktop/eld_output.txt')
            raise Exception
        self._path = new_path
        
        return self._path

    def update_dfs(self,ts_idx=True, update_init=True):
        self.df = self.parse_eld_file(ts_index = ts_idx)
        if update_init:
            self.df_init = self.df
        return self.df
        
        

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
            df.TimeStamp = pd.to_datetime(df.TimeStamp)
            df.set_index('TimeStamp',inplace=True)
        self.df = df
        return df
    
    
    def get_date_range(self,beg_str, end_str, df = None):
        '''
        format for strings: '2019-10-01'
        Maybe should be >=  <= (cur: > and <= ) 
        df opt arg to CHAIN THINGS TOGETHER
        '''
        
        assert beg_str <= end_str, 'Please make beg_str earlier than end_str,'
        if df is None: 
            df = self.df
            
        
        #Dont think this is needed... str works ? More Flexible too...?
        #try:
        #    beg_dt = datetime.strptime(beg_str, '%Y-%m-%d')
        #    end_dt = datetime.strptime(end_str, '%Y-%m-%d')
        #except Exception as e:
        #    print('MUST format strings as YYYY-MM-DD,( or YYYY, YYYY-MM )-- please try again')
        #    raise e
    
        try:
            df.TimeStamp
        except:
            df.reset_index(inplace=True)
        
        df = df[(df['TimeStamp'] > beg_str) & (df['TimeStamp'] <= end_str)] #Maybe should be >= and <= ?
        df.set_index('TimeStamp',inplace=True)

        return df 
    

    def get_idx_trades(self, idx, TimeStamp=None, df = None):
        '''Really to find single trade -- for more, use get_date_range'''
        if df is None:
            df = self.df
        if TimeStamp:
            df = self.reindex_timestamp()
            return df.loc[TimeStamp]
        else:
            return df.iloc[idx]
        
    
    def get_strategy_trades(self, StrategyName, df = None):
        if df is None:
            df = self.df
        return df.loc[df['StrategyName'] == StrategyName]
    
    def get_symbol_trades(self, Symbol, df = None):
        if df is None:
            df = self.df
        return df.loc[df.Symbol == Symbol]
    
    

    def multi_query(self, beg_str = None, end_str = None, Symbol = None, Strategy = None, df = None):
        '''Must take LISTS -- even if single object lists'''
        if df is None:
            df = self.df

        if Strategy and Symbol:
            return df.loc[df['StrategyName'].isin(Strategy) & df['Symbol'].isin(Symbol)]
            
        
        if Strategy:
            return df[df['StrategyName'].isin(Strategy)]
        
        if Symbol:
            return df[df['Symbol'].isin(Symbol)]
    
    
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
        
    
    
    def rogue_search_II(self, strategies, symbols=None):
        '''Redid this -- trying to make it a bit more logical'''
        assert isinstance(strategies,list), 'strategies must be list, even if single item'
        assert isinstance(symbols, list) or symbols is None, 'symbols must be list, even if single item'
        
        
        DF = self.df
        alert = [print('Alert -- ',strategy,'not present in log.') for strategy in strategies if strategy not in DF.StrategyName.unique()]

        #Filter down to final dataframe here...
        if strategies:
            if symbols: #Might not need this block... bc continuing out of vvvv these ? 
                DF = DF.loc[DF['StrategyName'].isin(strategies) & DF['Symbol'].isin(symbols)]
            DF = DF.loc[DF['StrategyName'].isin(strategies)]
        elif symbols:
            DF = DF.loc[DF['Symbol'].isin(symbols)]
        else:
            print('ERROR -- Need strategies,symbols, or both specified.')
            
            
        flagged = []
        definite = []
        for i in strategies:
            print('running check on ',i)
            #Check to make SURE ITS IN symbols we're querying (if any)
            #if symbols and i[0:3] not in symbols: #This is only when using my labelling method ES_PRIII for ex.
            #    continue 
            
            #Get Local df -- (single system dataframe)
            df = DF[DF.StrategyName == i]
            #Maybe do DF[DF.Symbol is in symbols] here too !? (instead of up there ^^)
                    
            #################### ALL local (df) queries now...
            #print(df.shape[0])
            if df.shape[0] % 2 == 0:
                continue

            exits = df.loc[df['Action'] == 'Exit']
            entries = df.loc[df['Action'] == 'Entry']
            #print(f'Entries: {entries.shape[0]}; Exits: {exits.shape[0]}')
            if entries.shape[0] == exits.shape[0]:
                continue
               
            #if entries.shape[0] > exits.shape[0] + 2:
            #    flagged.append(i)
                
            #More robust rogue checks.....

            if df.LivePNL.iloc[0] < -1 * df['SL$'].iloc[0]:
                print(df.LivePNL.iloc[0],'<',df['SL$'].iloc[0])
                #Maybe append (strategy, symbol) -- INCLUDE SYMBOL NAME in STRATEGy -- ex: ES_PRIIII
                definite.append(i)
                
            #Check TIME Exits 
            #Check TGTS (for flagged...)
            
        return flagged, definite


    
    def rogue_search_III(self, strategies, symbols=None):
        '''Must take lists as strategies and symbols (if any)'''
        assert isinstance(strategies,list), 'strategies must be list, even if single item'
        #assert isinstance(symbols, list) or symbols is None, 'symbols must be list, even if single item'
        #should modify multi-query to take lists  / multiples...
        
        #CAN REPLACE W Multi-Query NOW!!
        DF = self.multi_query(Symbol=symbols,Strategy=strategies)
        alert = [print('Alert -- ',strategy,'not present in log.') for strategy in strategies if strategy not in DF.StrategyName.unique()]

        flagged = []
        definite = []
        for i in strategies:
            print('running check on ',i)
            #Get Local df -- (single system dataframe)
            df = DF[DF.StrategyName == i]
                    
            #################### ALL local (df) queries now...
            #print(df.shape[0])
            if df.shape[0] % 2 == 0:
                continue

            exits = df.loc[df['Action'] == 'Exit']
            entries = df.loc[df['Action'] == 'Entry']
            print(f'Entries: {entries.shape[0]}; Exits: {exits.shape[0]}')
            if entries.shape[0] == exits.shape[0]:
                continue
               
            if entries.shape[0] > exits.shape[0] + 2:
                flagged.append(i)
                
            #More robust rogue checks.....
            if df.LivePNL.iloc[0] < -1 * df['SL$'].iloc[0]:
                print(df.LivePNL.iloc[0],'<',df['SL$'].iloc[0])
                #Maybe append (strategy, symbol) -- INCLUDE SYMBOL NAME in STRATEGy -- ex: ES_PRIIII
                definite.append(i)
                
            #Check TIME Exits 
            #Check TGTS (for flagged...)
            
        return flagged, definite


    
    
if __name__ == '__main__':    
    
    elm = ELDMonitor(ts_idx=True)
    elm.df.head(1)
    #elm.df_init -- Saved ! Can Reference Original without Parse again...
    b = '2019-10-25'
    elm.get_date_range('2019','2019-10-25')
    
    '''MultiQueries...'''
    elm.multi_query('2019','2020',['USD/JPY'],['2017_11_12 USDJPY S r3']).head(5) #Temp
    elm.multi_query('2019','2020',Strategy=['2017_11_12 USDJPY S r3']).head(5) #Temp
    #IF JUST dt,sys etc -- NEED to specify ^^^^^ !
    
    elm.rogue_search_II(['2017_11_12 USDJPY S r3']) 
    elm.rogue_search_II(['2017_11_12 USDJPY S r3','ESPRIII']) 