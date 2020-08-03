# SlackInteractivePM
## An Interactive Monitoring and Failsafe program to monitor Multicharts + ELD

Currently ran on NGROK Server locally, Deploying to Glitch for production

#### Commands (Writes):
SlackUI is primary IU / entrypoint, controlled via Slack Channel -- Must be given proper OAuth in Slack API dashboard.
Commands are executed, and written to txt / csv (to be read into ELD files, and parsed to then set Globals (via GlobalVariables.dll in MC64) to be read by individual Strategies.  EX: [1, 'P', 'ES', 5] would Pause ES Symbol for 5 Bars. 


#### Monitoring (Reads):
~50 Trade Metrics are processed and written from ELD file to txt file (Thanks to Ben Racze for his ELD Monitoring/Logging program!)
    (will post a very basic logging alternative eventually)
    
Txt File log is parsed by ELDParse.py, and things like Rogue Trades are flagged --> sent to Service Layer -> to SlackUI, where an action can be decided via Slack Command.  Eventually, these Alerts will have a default Command + log to handle the event.



##### Queries (Coming Soon):
Query the log from SlackUI, to pull metrics and reports on trade data -- Ex PNL + Slippage Report of ES, NQ, and CL for past 10 days.




## ELD Snippets:
Found in .ELD files or .TXT files
ELDMonitor needs to run in 1 location, on one chart for ex.

Then the Snippet at bottom -- for reading globals -- needs to be included in all strategies to be controlled by SlackInteractivePM
