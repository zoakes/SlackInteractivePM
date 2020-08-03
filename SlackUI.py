#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 10:55:44 2020

@author: zoakes

Version 1.0.1:
    8.01.20 -- Initial Commit, Primary routes built, no handling for events.
    
    
"""


from flask import Flask, request

#Actual functions to go here -- but really should go to SVC LAYER !! / MessageBus?
from collections import deque

from command import Commands
c = Commands()




CID = 0
CMDS = deque()
#Ex [(1,Query, ES, PNL, 1, H), 
    #(2, Pause, NQ , 1)]
    #(3, Halt, RTY)

'''Make a DataClass of Command Object ? -- is there  ANY point of the CMDS deque?'''

def get_cid():
    global CID
    CID += 1
    return CID


#CONSIDER A DEQUE?
def halt_api_call(*args):
    # this is where you can do whatever you want. the call to your server, whatever
    cid = get_cid()
    cmd = (cid, 'halt', *args)
    CMDS.append(cmd)
    #NOW call the  COMMAND module -- to EXECUTE it!
    c.Halt(*args)  
    return cmd


def pause_api_call(*args):
    cid = get_cid()
    cmd = (cid,'pause', *args)
    CMDS.append(cmd)
    c.Pause(*args)
    return cmd
    
    #Make call to OUTSIDE -- Command module...

def go_flat_api_call(*args):
    cid = get_cid()
    cmd = (cid,'flatten', *args)
    CMDS.append(cmd)
    #CALL COMMAND MODULE
    c.GoFlat(*args)
    return cmd
    


def query_api_call(*args):
    cid = get_cid()
    cmd = (cid, 'query', *args)
    CMDS.append(cmd)
    #CALL COMMAND MODULE
    return cmd


#MAKE THIS ASPECT EVENT BASED + Decoupled.

#This maybe in different module..?  WHICH ONLY depends on ELD Parse ?
#This needs to communicate WHAT and HOW it was requested to ELD Parse (+ Back)
#Won't KNOW the function, so maybe should just be ARGS?! ***
'''
Requests process ...
UI -> cmds/evnts module -> svg layer / msg bus -> eld_parse_module -> data
then 
    <-                  <-                     <-                  <-
Data Process               (Get from PDs to Natives? (arrays, matrices, dicts))
data -> eld_parse -> msg_bus / svc layer -> commands module -> UI 
'''

HANDLERS_BUS = {
    'query':[], #Example:[ (Function), (sym, metric, ln, period) ] ? Kinda confusing...
    'pause':[], #Example : [Function, Arguments]
    }


#Maybe it JUST imports the HANDLERS dict ?!

'''Flask Functions'''
# flask server setup and routes
app = Flask(__name__)



@app.route('/')
def index():
    return 'hi there'



@app.route('/halt', methods=['POST'])
def halt_route():
    #halt_api_call()
    payload = request.form.to_dict()
    print(payload)

    args = payload['text']
    print(args)                                     #   THIS is where you do the ARGUMENTs -- like SYMBOL or TIME!
    halt_api_call(args)
    return "Ok, halted " + args

@app.route('/haltall', methods=['POST'])
def halt_all_route():
    
    #payload = request.form.to_dict()
    #args = payload['text']
    #print(args)                                     #   THIS is where you do the ARGUMENTs -- like SYMBOL or TIME!
    halt_api_call('ALL')
    return "Ok, halted All!"

@app.route('/pause', methods=['POST'])
def pause_route():                                                          #Need MULTIPLE args, so need to PARSE this 
    payload = request.form.to_dict()
    args = payload['text']
    #CALL the PAUSE function here too
    
    syms, time = args.split('--')
    pause_api_call(syms, time)
    print('Call Function to PAUSE ', args)
    return 'Ok, Paused ' + syms + 'for ' + time + 'hours'

@app.route('/goflat',methods=['POST'])
def go_flat_route():
    payload = request.form.to_dict()
    args = payload['text']
    #CALL the PAUSE function here too
    print('Call Function to GO FLAT in ', args)
    go_flat_api_call(args)
    return 'OK, Going Flat in ' + args
    

'''Returns DFs basically or SQL views'''
@app.route('/query',methods=['POST'])
def query_route():
    '''
    Ex:
    ES - PNL - N -  W
    Sym - Metric - # - Period
    '''
    payload = request.form.to_dict()
    args = payload['text']
    sym, metric, ln, period = args.replace(' ','').split('-')                   #May need .replace or .strip in others?
    if period.upper() not in ['W','D','H']:
        return 'Please enter W, D or H for weeks, days, hours'
    return 'Returning ' + ln + period + ' ' + metric  + ' for ' + sym  + '.'
    
    
    
    
    

if __name__ == "__main__":
    #TO SET UP NGROK  -- 
    app.run()
    
    
    '''
    TO SETUP NROK SERVER -- 
    In Terminal -- 
    ngrok http 5000
    REMEMEBER -- use the NGROK URL + <command> ex:
        https://..../halt
        
    '''