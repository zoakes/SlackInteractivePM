#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 11:13:50 2020

@author: zoakes
"""

import csv 
import datetime as dt

DEBUG = False

class Commands:
    default_file = 'cmd_output.csv'
    
    def __init__(self, output_file=None):
        '''Currently Created New CSV EACH time its Initialized...'''
        if not output_file:
            self.filename = self.default_file
        else:
            if (output_file[-4:] != '.csv'):
                self.filename = self.default_file
            else:
                self.filename = output_file
            
        assert self.filename[-4:] == '.csv', 'MUST be CSV file'

        

    
    
    '''These may need *Args input, and a loop to flatten ALL?'''
    '''Need to add write to csv logic here too !!'''
    

    
    def goFlat(self, symbol):

        self.Write('F',symbol)
        #print(f'going flat in {symbol}')
        return f'going flat in {symbol}'
    
    
    def Pause(self, *args):
        '''Can only Take 1 thing!!! -- otherwise too confusing I think...'''
        #for s in symbols:
            #self.Write('P',s) #This isn't quite right... NEEDS TO LOOP IN SLACKUI, call once.
            
        #Writes 'p', symbol, time in HOURS
        self.Write('P',*args)
        print('Pausing',args[0])
        #return f'pausing {symbol}'
    
    
    
    def Halt(self, symbol):
        '''halts ALL or Multiple symbols depending on args'''
        
        #If All... Write -- Date, H, ALL
        if symbol == 'ALL': # in symbols: 
            self.Write('H','ALL')
            return 'Halting ALL.'
        
        #Else, Date, H, Symbol
        self.Write('H',symbol)
        return f'Halting {symbol}' 
    
    
    def Query(self, *args):
        '''
        SHOULD MAKE THIS SEPERATE, I THINK !! 
        SEPERATE READS AND WRITES!
        '''
        sym, query, n, units = args
        print(f'Returning {n} {units} {query} for {sym}')
        return f'Returning {n} {units} {query} for {sym}'
    
    
    def Write(self,*args):
        '''More detailed -- 
        https://www.geeksforgeeks.org/writing-csv-files-in-python/
        https://stackoverflow.com/questions/43733205/write-newline-to-csv-in-python
        
        WRITE ONE LINE, ONE SYMBOL, ONE COMMAND AT A TIME 
        (DATE, COMMAND, SYMBOL)
        '''
        
        #with open(self.filename,'a') as f:
        #    f.write("title; post")
        #    f.write("\n")
        date = dt.datetime.now()
        out = [date, *args]  #INCLUDE THE ACTION -- 'halt', 
        with open(self.filename, 'a') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(out)
        
        


if __name__ == '__main__':

    c = Commands('tst.csv')
    c.Pause('ES','1')    
    c.Halt('ES') #,'NQ')
    
    #c.Query('ES','PNL','1','H')
    
    c.goFlat('ES') #,'RTY')
    c.Halt('ALL')
    
    #print(c.filename)
    #print(c.filename[-4:])
    
    #c.Write('ES','NQ')
    
    





    '''Format for MULTIPLE AT ONCE -- just wont work for this, not YET.
    #def goFlat(self, *symbols):
        #for s in symbols:
        #    pass
        #self.Write('F',symbols)
        #print(f'going flat in {symbols}')
        #return f'going flat in {symbols}'
        
    def Halt(self, *symbols):
        
        #for s in symbols:                                                       #Logic to LOOP through MULTIPLE ARGS
            #print(s) Still loops as 'ALL', not 'A', 'L', 'L',
        #    self.Write('H',s)

        
        if 'ALL' in symbols: 
            print('Halting ALL')
            self.Write('H','ALL')
            return 'Halting ALL.'
        
        self.Write('H',symbol)
        
        #WIRTE TO CSV HERE
        return f'Halting {symbols}' 
    '''
    
    