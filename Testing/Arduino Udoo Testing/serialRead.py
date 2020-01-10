  
'''
*  Copyright (C) 2014 Ekironji <ekironjisolutions@gmail.com>
*
*  This file is part of serial libraries examples for UDOO
*
*  Serial libraries examples for UDOO is free software: you can redistribute it and/or modify
*  it under the terms of the GNU General Public License as published by
*  the Free Software Foundation, either version 3 of the License, or
*  (at your option) any later version.
*
*  This libraries are distributed in the hope that it will be useful,
*  but WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*  GNU General Public License for more details.
*
*  You should have received a copy of the GNU General Public License
*  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*

Short todo:
-Create function to be called to read characters
'''

import serial
import time
import struct

def init():
    ser = serial.Serial('/dev/ttyACM0',9600,timeout=1)
    ser.flushOutput()

    print('Serial connected')
    '''Not sure if this fails to print in the case that Serial does not connect. Maybe change to "Listening on serial..."?'''

init()

while True:
    r = ser.read(1)

    print(r)

    time.sleep(0.1) 		# delay for 1 second
