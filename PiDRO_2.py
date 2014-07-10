# PiDRO_2 - June 2014 Alan Campbell
# by Alan Campbell
# July 2014

# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 3 of the License, or
# * (at your option) any later version.

import time
import serial
from tkinter import *
from tkinter import ttk

def storesetup(*args):  # used with Setup Tab
    try:
        f = open('DROsetup.txt', 'w')
        f.write('PiDRO Setup information\n')        
        f.write(str(sfsz) + ' # setup tab font size\n')
        f.write(str(mfsz) + ' # mill tab font size\n')
        f.write(str(gfsz) + ' # lathe tab font size\n')
        f.write(str(tfsz) + ' # measure tab font size\n')
        f.write( units.get() +    ' # display units\n')
        f.write( str(avg.get()) +    ' # data average\n')
        #print( units.get() )        
        for c in range(1, 7):
            f.write( cscaletxt[c].get() + ' # ' + cname[c] + ' scaling factor and direction\n')        
        f.close()
    except ValueError:
        pass

def readsetup(*args): # used with Setup Tab
    try:
        f = open('DROsetup.txt', 'r')
        inbuf = f.read()
        #print( inbuf ) # debug prints to shell screen
        f.close()
        st = inbuf.find('inch')        
        if st > 1:
            units.set('Units-inch')            
        else:
            units.set('Units-mm')            
        #print( units.get() )
        st = inbuf.find('\n')
        sp = inbuf.find('#')
        sfsz = int(inbuf[st+1:sp])
        #print( str(st) + "  " + str(sp)+'  '+ str(sfsz) )
        st = inbuf.find('\n', st+1)
        sp = inbuf.find('#', st+1)
        mfsz = int(inbuf[st+1:sp])
        #print( str(st) + "  " + str(sp)+'  '+ str(mfsz) )
        st = inbuf.find('\n', st+1)
        sp = inbuf.find('#', st+1)
        gfsz = int(inbuf[st+1:sp])
        #print( str(st) + "  " + str(sp)+'  '+ str(gfsz) )
        st = inbuf.find('\n', st+1)
        sp = inbuf.find('#', st+1)
        tfsz = int(inbuf[st+1:sp])
        #print( str(st) + "  " + str(sp)+'  '+ str(tfsz) )
        st = inbuf.find('\n', st+1) # skip units
        sp = inbuf.find('#', st+1)
        st = inbuf.find('\n', st+1) # average
        sp = inbuf.find('#', st+1)
        a = int(inbuf[st+1:sp])
        avg.set( a )
        for c in range(1, 7):
            st = inbuf.find('\n', st+1)
            sp = inbuf.find('#', st+1)
            cscale[c] = float( inbuf[st+1:sp] )
            #print str(st) + '  ' + str(sp) + '  ' + str(cscale[c])            
    except ValueError:
        print( 'Read Setup Error')
        pass

def readscales( ):
    serin.flushInput()
    time.sleep(.001)
    inbuf = str(serin.readline() )
    inbuf = str(serin.readline() )   
    #print( inbuf )
    st = 0;
    av = avg.get()
    for c in range(1, 7): # read data
        st = inbuf.find(':', st+1) 
        sp = inbuf.find(';', st+1)
        cdata[c] = int( (int(inbuf[st+1:sp]) / av) + (cdata[c] * (av-1)/av) ) # rolling average data       
        x = int((cdata[c]*cscale[c]-offset[c]) * 1000 )
        #if c==1: print( c, cdata[c], cscale[c], offset[c], x)
        if x < 0 :
            sflag = '- '
            x = -1 * x
        else:
            sflag = "+"
        xs = '000000000000' + str( x )
        xlen = len( xs )        
        uni = units.get()        
        if uni.find('nch') > 0 :            
            outdata[c].set( sflag + xs[ xlen-5:xlen-3 ] + '.' + xs[ xlen-3:xlen] )  # inch format XX.XXX
        else:
            outdata[c].set( sflag + xs[ xlen-6:xlen-3 ] + '.' + xs[ xlen-3:xlen-1] )  # metric format XXX.XX        
        scaledata[c].set( str(round(cdata[c], 3))+'  ' )
    root.after( 100, readscales )

def zero( chan, off ):
    #print( chan, off )
    if off==8888: off = -cdata[6] + (offset[6]/cscale[6])  # set to caliper
    if off==9999: off = (-cdata[6] + (offset[6]/cscale[6]))/2  # set to half caliper
    offset[chan] = (cdata[chan] + off) * cscale[chan]    
    
def iftab( tabname ):
    note.tab(note.select(), "text")

def set_inch():      
    cscale[0]= float( 0.0003937 ) # not used
    cscale[1]= float( -0.0003937 )
    cscale[2]= float( 0.0003937 )
    cscale[3]= float( 0.0003937 )
    cscale[4]= float( 0.0003937 )
    cscale[5]= float( 0.0007874 )
    cscale[6]= float( 0.0003937 )    
    units.set('Units:inch')
    for c in range(1, 7) :
        cscaletxt[c].set( cscale[c] )
        offset[c] = offset[c]/25.4
    storesetup()
    
def set_mm():
    cscale[0]= float( 0.01 ) # not used
    cscale[1]= float( -0.01 )
    cscale[2]= float( 0.01 )
    cscale[3]= float( 0.01 )
    cscale[4]= float( 0.01 )
    cscale[5]= float( 0.02 )
    cscale[6]= float( 0.01 )    
    units.set('Units:mm')
    for c in range(1, 7) :
        cscaletxt[c].set( cscale[c] )
        offset[c] = offset[c]*25.4
    storesetup()

def avg_up():
    a = avg.get() + 1
    if a < 11: avg.set( a )

def avg_down():
    a = avg.get() - 1
    if a > 1: avg.set( a ) 

# End of function defs/////////////////////////////////////////////////////////////////////

root=Tk()
root.title('PiDRO Digital Read Out  V2.0') # Change version number//////////////////////////

# Main Tabs
note = ttk.Notebook(root)
stab = ttk.Frame(note)  # Setup tab
mtab = ttk.Frame(note)  # Mill tab
gtab = ttk.Frame(note)  # Lathe tab

# Font sizes for each tab
sfsz = 24
mfsz = 26
gfsz = 28
tfsz = 30
# Default axis scaling factors
units = StringVar()
units.set('Units:inch')
clabel = ['N', 'X', 'Y', 'Z', 'L', 'D', 'C']
cname =  ['None', 'Mill', 'Mill', 'Mill', 'Lathe Length', 'Lathe Diameter', 'Caliper']
cscale = [0.1, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6]
cscaletxt = ['0.1', '1.1', '2.2', '3.3', '4.4', '5.5', '6.6']
ent = [0, 1, 2, 3, 4, 5, 6]
cdata = [0.11, 1.11, 2.22, 3.33, 4.44, 5.55, 6.66]
offset = [0.11, 1.11, 2.22, 3.33, 4.44, 5.55, 6.66]
outdata = ['0.1', '1.1', '2.2', '3.3', '4.4', '5.5', '6.6']
scaledata = ['0.1', '1.1', '2.2', '3.3', '4.4', '5.5', '6.6']
for c in range(1, 7) :
    outdata[c] = StringVar()
    cscale[c] = DoubleVar()
avg = IntVar()
avg.set( 3 )

readsetup()
# Note tab titles
note.add(mtab, text='Mill')
note.add(gtab, text='Lathe')
note.add(stab, text='Setup')

# Setup Tab //////////////////////////////////////////////////////////////////////////////////
ttk.Label(stab, text="Counts", font=('Sans', sfsz)).grid(column=2, row=0, sticky=W)
ttk.Label(stab, text="Scale by", font=('Sans', sfsz)).grid(column=3, row=0, sticky=W)
ttk.Label(stab, textvariable=units, font=('Sans', sfsz)).grid(column=5, row=0, sticky=E)
# Channel Info
for c in range(1, 7) :
    outdata[c] = StringVar()
    scaledata[c] = StringVar() 
    ttk.Label(stab, text=clabel[c], font=('Sans', sfsz)).grid(column=1, row=c, sticky=W)
    ttk.Label(stab, textvariable=scaledata[c], font=('Sans', sfsz)).grid(column=2, row=c, sticky=W)
    ttk.Label(stab, text=cname[c], font=('Sans', sfsz)).grid(column=4, row=c, sticky=W)
    cscaletxt[c] = StringVar()
    cscaletxt[c].set( cscale[c] )
    ent[c] = ttk.Entry(stab, font=('Sans', sfsz), width=10, textvariable=cscaletxt[c])
    ent[c].grid(column=3, row=c, sticky=W)
# Store setup information
ttk.Button(stab, text='Save Units', command=storesetup).grid(column=5, row=1, sticky=E)
ttk.Button(stab, text='Set: INCH', command=set_inch).grid(column=5, row=2, sticky=E)
ttk.Button(stab, text='Set: MM', command=set_mm).grid(column=5, row=3, sticky=E)
# set averaging
ttk.Label(stab, textvariable=avg, font=('Sans', sfsz)).grid(column=5, row=5, sticky=E)
ttk.Button(stab, text='Average+', command=avg_up).grid(column=5, row=4, sticky=E)
ttk.Button(stab, text='Average-', command=avg_down).grid(column=5, row=6, sticky=E)
for child in stab.winfo_children():
    child.grid_configure(padx=5, pady=5)

# Mill Tab //////////////////////////////////////////////////////////////////////////////////
mtab.btn = [0, 1, 2, 3, 4, 5, 6]
ttk.Label(mtab, text="DRO: MILL", font=('Sans', mfsz)).grid(column=2, row=0, sticky=W)
ttk.Label(mtab, textvariable=units, font=('Sans', mfsz)).grid(column=4, row=0, sticky=E)
ttk.Label(mtab, text="ZERO", font=('Sans', mfsz)).grid(column=5, row=0, sticky=W)
# Channel Info
for c in 1, 2, 3, 6 :
    ttk.Label(mtab, text=clabel[c]+':', font=('Sans', mfsz)).grid(column=1, row=c, sticky=W)
    ttk.Label(mtab, textvariable=outdata[c], font=('Sans', mfsz)).grid(column=2, row=c, sticky=W)
    ttk.Label(mtab, text=cname[c], font=('Sans', mfsz)).grid(column=4, row=c, sticky=W)
    mtab.btn[c] = Button(mtab, text='0', command= lambda row=c, ooff=0 : zero(row, ooff)).grid(column=5, row=c)
    mtab.btn[c] = Button(mtab, text='<', command= lambda row=c, ooff=254 : zero(row, ooff)).grid(column=6, row=c)
    mtab.btn[c] = Button(mtab, text='>', command= lambda row=c, ooff=-254 : zero(row, ooff)).grid(column=7, row=c)
    mtab.btn[c] = Button(mtab, text='C', command= lambda row=c, ooff=8888 : zero(row, ooff)).grid(column=8, row=c)
for child in mtab.winfo_children():
    child.grid_configure(padx=5, pady=5)

# Lathe Tab //////////////////////////////////////////////////////////////////////////////////
gtab.btn = [0, 1, 2, 3, 4, 5, 6]
ttk.Label(gtab, text="DRO: LATHE", font=('Sans', mfsz)).grid(column=2, row=0, sticky=W)
ttk.Label(gtab, textvariable=units, font=('Sans', mfsz)).grid(column=4, row=0, sticky=E)
ttk.Label(gtab, text="ZERO", font=('Sans', mfsz)).grid(column=5, row=0, sticky=W)
# Channel Info
for c in 4, 5, 6 :
    ttk.Label(gtab, text=clabel[c]+':', font=('Sans', mfsz)).grid(column=1, row=c, sticky=W)
    ttk.Label(gtab, textvariable=outdata[c], font=('Sans', mfsz)).grid(column=2, row=c, sticky=W)
    ttk.Label(gtab, text=cname[c], font=('Sans', mfsz)).grid(column=4, row=c, sticky=W)
    gtab.btn[c] = Button(gtab, text='0', command= lambda row=c, ooff=0 : zero(row, ooff)).grid(column=5, row=c)
    gtab.btn[c] = Button(gtab, text='<', command= lambda row=c, ooff=254 : zero(row, ooff)).grid(column=6, row=c)
    gtab.btn[c] = Button(gtab, text='>', command= lambda row=c, ooff=-254 : zero(row, ooff)).grid(column=7, row=c)
    if c==5:
        gtab.btn[c] = Button(gtab, text='C', command= lambda row=c, ooff=9999 : zero(row, ooff)).grid(column=8, row=c)
    else:
        gtab.btn[c] = Button(gtab, text='C', command= lambda row=c, ooff=8888 : zero(row, ooff)).grid(column=8, row=c)

for child in gtab.winfo_children():
    child.grid_configure(padx=5, pady=5)
# Lathe Tab end ////////////////////////////////////////////////////////////////////////////////////

note.pack()
serin = serial.Serial( '/dev/ttyUSB0', 9600 )
root.after_idle( readscales ) # serial port input
root.mainloop()
