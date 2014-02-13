What is it?
-----------

Python module that checks the wind speed reported by a NOAA weather station on the hour, from 8am - 8pm.  This is a great tool for anyone who loves windsports, but hates having to constantly check the weather.  It can be configured to run once or continually.

If the station is reporting a wind speed greater than the configured minimum speed, an SMS alert is sent to a mobile phone
displaying the current wind speed, along with a graphical chart showing the wind speed over the past 4 hours.  

Prerequisites
-------------

Since timezones conversions are involved, pytz is a required module and can be found here: http://pytz.sourceforge.net/

Installation
------------

     o Modify the notifier.py module to use a valid gmail username/password.  In addition, modify the module
        to use a valid mobile carrier email address that supports SMPT to SMS.

     o Install notifier.py module into python by dropping into the appropriate third-party module directory
        or run directly from a terminal window

     
Additional Details
------------------

     o To run the script, call sample.py from a terminal window
    
        python sample.py

