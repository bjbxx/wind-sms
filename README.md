                          Wind SMS Module

What is it?
-----------

Python script that continually checks a NOAA weather station on the hour, between "normal" daylight hours 8am - 8pm.  
If the station is reporting a wind speed greater than the configured minimum speed, an SMS alert is sent to a mobile phone
displaying the current wind speed, along with a graphical chart showing the wind speed over the past 4 hours.  

Prerequisites
-------------

Since timezones conversions are involved, pytz is a required module and can be installed from here: http://pytz.sourceforge.net/

Installation
------------

     o Modify the notifier.py module to use a valid gmail username/password.  In addition, modify the module to use 
        a valid mobile carrier email address that supports SMPT to SMS.

     o Install notifier.py module into python by dropping into the appropriate third-party module directory or installing via the setup script
    
        python setup.py install

     
Additional Details
------------------

     o To run the script, call sample.py from a terminal window
    
        python sample.py

