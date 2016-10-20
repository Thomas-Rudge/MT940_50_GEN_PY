#! python3
#-------------------------------------------------------------------------------
# Name:        Swift MT940/950 Generator
# Purpose:     Takes a specific csv file and converts it to
#              either an MT940 or MT950 swift message.
# Version:     1.1.0
# Author:      Thomas Edward Rudge
# Created:     25-10-2015
# Copyright:   (c) Thomas Edward Rudge 2015
# Licence:     GPL
#-------------------------------------------------------------------------------
# Written for Python 3

import tkinter, sys, ctypes, pickle, webbrowser, os, mt940_50
import tkinter.filedialog as tkfd

bgclr, actvclr, btnclr, btnclr2 = 'white', '#00CDFA', '#F0F0F0', '#99FFFF'
conf_size = 235, 160
winrlf = 'raised'
cwd = os.getcwd()
icon = cwd + '\\mt9_ico.ico'


def get_screensize(event=None):
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def okwindow(txt, wdth, hght, title, screensizet):
    '''
    Generates a window that displays text. Single 'OK' button.
    '''
    def gogo(event=None):
        okwin.destroy()

    wlxym = '+%s+%s' % (str(screensizet[0] // 2 - wdth // 2), 
                        str(screensizet[1] // 2 - hght // 2))

    okwin = tkinter.Tk()

    lblfrm = tkinter.LabelFrame(okwin, width=wdth, height=hght, bg=bgclr)
    lblfrm.grid(row=0, column=0, sticky='nesw')
    lblfrm.grid_propagate(False)

    lbl = tkinter.Label(lblfrm, text=txt, bg=bgclr, justify='center', wraplength=wdth - 20)
    lbl.grid(row=0, column=0, pady=10)

    okbut = tkinter.Button(lblfrm, text='Ok', command=gogo, activebackground='#00CDFA', 
                           relief=winrlf, width=6, bg='#f0f0f0')
    okbut.grid(row=1, column=0, sticky='s', pady=4)

    lblfrm.grid_columnconfigure(0, weight=1)
    lblfrm.grid_rowconfigure(0, weight=1)
    lblfrm.grid_rowconfigure(1, weight=1)

    okwin.geometry('%sx%s%s' % (str(wdth), str(hght), wlxym))
    okwin.config(bg=bgclr)
    okwin.title(title)
    okwin.bind('<Return>', gogo)
    okwin.protocol("WM_DELETE_WINDOW", gogo)
    okwin.iconbitmap(icon)

    okwin.wait_window()


def confirmwin(txt, b1, b2, b3, title, screensizet):
    '''
    Generates a window that displays text with two button options. The value
    of the button pressed is returned. Delete window protocol also returns False.
    '''
    confwin = tkinter.Tk()

    trig = tkinter.StringVar()
    trig.set('')

    def gogo1(event=None):
        trig.set(b1)
        confwin.destroy()

    def gogo2(event=None):
        trig.set(b2)
        confwin.destroy()

    def gogo3(event=None):
        trig.set(b3)
        confwin.destroy()

    def nogo(event=None):
        confwin.destroy()

    wlxym = '+%s+%s' % (str(screensizet[0] // 2 - conf_size[0] // 2), 
                        str(screensizet[1] // 2 - conf_size[1] // 2))

    lblfrm = tkinter.LabelFrame(confwin, width=conf_size[0], height=conf_size[1], bg=bgclr)
    lblfrm.grid(row=0, column=0, sticky='nesw')
    lblfrm.grid_propagate(False)

    lbl = tkinter.Label(lblfrm, text=txt, bg=bgclr, justify='center', wraplength=conf_size[0] - 20)
    lbl.grid(row=0, column=0, sticky='nesw', columnspan=3, padx=10, pady=10)

    btn1 = tkinter.Button(lblfrm, text=b1, command=gogo1, activebackground=actvclr, 
                          relief=winrlf, width=len(b1) + 2, bg=btnclr2)
    btn1.grid(row=1, column=0, sticky='s', pady=15)

    btn2 = tkinter.Button(lblfrm, text=b2, command=gogo2, activebackground=actvclr, 
                          relief=winrlf, width=len(b2) + 2, bg=btnclr2)
    btn2.grid(row=1, column=1, sticky='s', pady=15)

    btn3 = tkinter.Button(lblfrm, text=b3, command=gogo3, activebackground=actvclr, 
                          relief=winrlf, width=len(b3) + 2, bg=btnclr)
    btn3.grid(row=1, column=2, sticky='s', pady=15)

    lblfrm.grid_columnconfigure(0, weight=1)
    lblfrm.grid_columnconfigure(1, weight=1)
    lblfrm.grid_columnconfigure(2, weight=1)
    lblfrm.grid_rowconfigure(1, weight=1)

    confwin.geometry('%sx%s%s' % (str(conf_size[0]), str(conf_size[1]), wlxym))
    confwin.config(bg=bgclr)
    confwin.title(title)
    confwin.protocol("WM_DELETE_WINDOW", nogo)
    confwin.iconbitmap(icon)

    confwin.wait_window()

    return trig.get()

def settings_window(screensizes):
    '''
    Calls the settings window.
    '''
    settings = get_settings(return_error=True)
    if type(settings) == tuple and settings[0] is False:
        raise Exception('Failed to get settings! Error:%s' % settings[1])

    setwin = tkinter.Tk()

    # Setting variables
    aplid, servid, ssno,  sqno  = tkinter.StringVar(), tkinter.StringVar(), tkinter.StringVar(), tkinter.StringVar()
    drctn, prty,   dmf,   obp   = tkinter.StringVar(), tkinter.StringVar(), tkinter.StringVar(), tkinter.StringVar()
    itime, odate,  otime, miref = tkinter.StringVar(), tkinter.StringVar(), tkinter.StringVar(), tkinter.StringVar()
    bpc,   muref,  chckv, dtfm  = tkinter.StringVar(), tkinter.StringVar(), tkinter.StringVar(), tkinter.StringVar()

    def set_variables(event=None):
        '''
        Sets tkinter variables using setting dictionary, and refreshes screen.
        '''
        # Replace short form with long form, for clarity
        decode = {
            'A':   'A - General',
            'F':   'F - Financial',
            'L':   'L - Logins',
            '01':  '01 - FIN/GPA',
            '21':  '21 - ACK/NAK',
            'I':   'I - Inward',
            'O':   'O - Outward',
            'S':   'S - System',
            'N':   'N - Normal',
            'U':   'U - Urgent',
            '1':   '1 - Non Delivery Warning',
            '2':   '2 - Delivery Notification',
            '3':   '3 - Both (1 & 2)',
            '003': '003 - 15 Minutes',
            '020': '020 - 100 Minutes',
            '':    'None'
            }

        aplid.set(decode[settings['appid']])
        dtfm.set(settings['dtf'])
        servid.set(decode[settings['servid']])
        ssno.set(settings['session_no'])
        sqno.set(settings['seqno'])
        drctn.set(decode[settings['drctn']])
        prty.set(decode[settings['msg_prty']])
        dmf.set(decode[settings['dlvt_mnty']])
        obp.set(decode[settings['obs']])
        itime.set(settings['inp_time'])
        odate.set(settings['out_date'])
        otime.set(settings['out_time'])
        muref.set(settings['mur'])

        if settings['mir'] is True:
            miref.set('')
        else:
            miref.set(settings['mir'])

        if settings['f113'] is False:
            bpc.set('')
        else:
            bpc.set(settings['f113'])

        if settings['chk'] is False:
            chckv.set('')
        else:
            chckv.set(settings['chk'])

        for child in bhb.winfo_children():
            try: child.update_idletasks()
            except: pass

        for child in ahb.winfo_children():
            try: child.update_idletasks()
            except: pass

        for child in uhb.winfo_children():
            try: child.update_idletasks()
            except: pass

        for child in tbk.winfo_children():
            try: child.update_idletasks()
            except: pass

        for child in dtb.winfo_children():
            try: child.update_idletasks()
            except: pass

    setlblfrm = tkinter.LabelFrame(setwin,bg=bgclr, width=630, height=560)
    setlblfrm.grid(row=0, column=0, sticky='nesw')
    setlblfrm.grid_propagate(False)

    ttl = tkinter.Label(setlblfrm, text='Message Header Settings', bg=bgclr)
    ttl.grid(row=0, column=0, sticky='n', pady=10)

    # Basic Header Block
    bhb = tkinter.LabelFrame(setlblfrm, bg=bgclr, text='{1: Basic Header Block')
    bhb.grid(row=1, column=0, sticky='nesw', padx=5, pady=5)

    aidl = tkinter.Label(bhb, bg=bgclr, text='Application ID:')
    aidl.grid(row=0, column=0, sticky='e', padx=5, pady=5)
    aide = tkinter.OptionMenu(bhb, aplid, 'A - General', 'F - Financial', 'L - Logins')
    aide.grid(row=0, column=1, sticky='w', padx=5, pady=5)
    aide.config(width=14, relief='groove', bg=btnclr, bd=1, highlightthickness=0)

    snol = tkinter.Label(bhb, bg=bgclr, text='  Session Number:')
    snol.grid(row=0, column=2, sticky='e', padx=5, pady=5)
    snoe = tkinter.Entry(bhb, textvariable=ssno, bd=2, relief='groove', width=7)
    snoe.grid(row=0, column=3, sticky='w', padx=5, pady=5)

    sidl = tkinter.Label(bhb, bg=bgclr, text='Service ID:')
    sidl.grid(row=1, column=0, sticky='e', padx=5, pady=5)
    side = tkinter.OptionMenu(bhb, servid, '01 - FIN/GPA', '21 - ACK/NAK')
    side.grid(row=1, column=1, sticky='w', padx=5, pady=5)
    side.config(width=14, relief='groove', bg=btnclr, bd=1, highlightthickness=0)

    sqnol = tkinter.Label(bhb, bg=bgclr, text='  Sequence Number:')
    sqnol.grid(row=1, column=2, sticky='e', padx=5, pady=5)
    sqnoe = tkinter.Entry(bhb, textvariable=sqno, bd=2, relief='groove', width=7)
    sqnoe.grid(row=1, column=3, sticky='w', padx=5, pady=5)

    # Application Header Block
    ahb = tkinter.LabelFrame(setlblfrm, bg=bgclr, text='{2: Application Header Block')
    ahb.grid(row=2, column=0, sticky='nesw', padx=5, pady=5)

    drl = tkinter.Label(ahb, bg=bgclr, text='Direction:')
    drl.grid(row=0, column=0, sticky='e', padx=5, pady=5)
    dre = tkinter.OptionMenu(ahb, drctn, 'I - Inward', 'O - Outward')
    dre.grid(row=0, column=1, sticky='w', padx=5, pady=5)
    dre.config(width=18, relief='groove', bg=btnclr, bd=1, highlightthickness=0)

    odtl = tkinter.Label(ahb, bg=bgclr, text='  Output Date:')
    odtl.grid(row=0, column=2, sticky='e', padx=5, pady=5)
    odte = tkinter.Entry(ahb, textvariable=odate, bd=2, relief='groove', width=8)
    odte.grid(row=0, column=3, sticky='w', padx=5, pady=5)

    ptl = tkinter.Label(ahb, bg=bgclr, text='Priority:')
    ptl.grid(row=1, column=0, sticky='e', padx=5, pady=5)
    pte = tkinter.OptionMenu(ahb, prty, 'S - System', 'N - Normal', 'U - Urgent')
    pte.grid(row=1, column=1, sticky='w', padx=5, pady=5)
    pte.config(width=18, relief='groove', bg=btnclr, bd=1, highlightthickness=0)

    otml = tkinter.Label(ahb, bg=bgclr, text='  Output Time:')
    otml.grid(row=1, column=2, sticky='e', padx=5, pady=5)
    otme = tkinter.Entry(ahb, textvariable=otime, bd=2, relief='groove', width=8)
    otme.grid(row=1, column=3, sticky='w', padx=5, pady=5)

    itml = tkinter.Label(ahb, bg=bgclr, text='Input Time:')
    itml.grid(row=2, column=0, sticky='e', padx=5, pady=5)
    itme = tkinter.Entry(ahb, textvariable=itime, bd=2, relief='groove', width=8)
    itme.grid(row=2, column=1, sticky='w', padx=5, pady=5)

    dmfl = tkinter.Label(ahb, bg=bgclr, text='  Delivery Monitoring:')
    dmfl.grid(row=2, column=2, sticky='e', padx=5, pady=5)
    dmfe = tkinter.OptionMenu(ahb, dmf, 'None', '1 - Non Delivery Warning',
                              '2 - Delivery Notification', '3 - Both (1 & 2)')
    dmfe.grid(row=2, column=3, sticky='w', padx=5, pady=5)
    dmfe.config(width=26, relief='groove', bg=btnclr, bd=1, highlightthickness=0)

    obsl = tkinter.Label(ahb, bg=bgclr, text='Obsolenscence:')
    obsl.grid(row=3, column=0, sticky='e', padx=5, pady=5)
    obse = tkinter.OptionMenu(ahb, obp, 'None', '003 - 15 Minutes', '020 - 100 Minutes')
    obse.grid(row=3, column=1, sticky='w', padx=5, pady=5)
    obse.config(width=18, relief='groove', bg=btnclr, bd=1, highlightthickness=0)

    mirl = tkinter.Label(ahb, bg=bgclr, text='  Message Input Ref:')
    mirl.grid(row=3, column=2, sticky='e', padx=5, pady=5)
    mire = tkinter.Entry(ahb, textvariable=miref, bd=2, relief='groove', width=30)
    mire.grid(row=3, column=3, sticky='w', padx=5, pady=5)

    # User Header Block
    uhb = tkinter.LabelFrame(setlblfrm, bg=bgclr, text='{3: User Header Block')
    uhb.grid(row=3, column=0, sticky='nesw', padx=5, pady=5)

    bpcl = tkinter.Label(uhb, bg=bgclr, text='Bank Priority Code:')
    bpcl.grid(row=0, column=0, sticky='e', padx=5, pady=5)
    bpce = tkinter.Entry(uhb, textvariable=bpc, bd=2, relief='groove', width=8)
    bpce.grid(row=0, column=1, sticky='w', padx=5, pady=5)

    murl = tkinter.Label(uhb, bg=bgclr, text='  Message User Ref:')
    murl.grid(row=0, column=2, sticky='e', padx=5, pady=5)
    mure = tkinter.Entry(uhb, textvariable=muref, bd=2, relief='groove', width=20)
    mure.grid(row=0, column=3, sticky='w', padx=5, pady=5)

    # Trailer Header Block
    tbk = tkinter.LabelFrame(setlblfrm, bg=bgclr, text='{5: Trailer Block')
    tbk.grid(row=4, column=0, sticky='nesw', padx=5, pady=5)

    chkl = tkinter.Label(tbk, bg=bgclr, text='Checksum Value:')
    chkl.grid(row=0, column=0, sticky='e', padx=5, pady=5)
    chke = tkinter.Entry(tbk, textvariable=chckv, bd=2, relief='groove', width=15)
    chke.grid(row=0, column=1, sticky='w', padx=5, pady=5)

    # Date Time Format
    dtb = tkinter.Frame(setlblfrm, bg=bgclr)
    dtb.grid(row=5, column=0, sticky='nesw', padx=5, pady=5)

    dtbl = tkinter.Label(dtb, bg=bgclr, text='CSV Date Format:')
    dtbl.grid(row=3, column=0, sticky='e', padx=5, pady=5)
    dtbe = tkinter.OptionMenu(dtb, dtfm, 'DDMMYYYY', 'MMDDYYYY', 'YYYYMMDD')
    dtbe.grid(row=3, column=1, sticky='w', padx=5, pady=5)
    dtbe.config(width=10, relief='groove', bg=btnclr, bd=1, highlightthickness=0)

    set_variables()

    def save_settings(event=None):
        ttl.config(text='')
        ttl.update_idletasks()

        db = {}

        db['dtf']        = dtfm.get()
        db['appid']      = aplid.get()[:1]
        db['servid']     = servid.get()[:2]
        db['session_no'] = ssno.get().rjust(4, '0')
        db['seqno']      = sqno.get().rjust(6, '0')
        db['drctn']      = drctn.get()[:1]
        db['msg_prty']   = prty.get()[:1]
        db['inp_time']   = itime.get().rjust(4, '0')
        db['out_date']   = odate.get().rjust(6, '0')
        db['out_time']   = otime.get().rjust(4, '0')

        if muref.get().strip() == '':
            db['mur'] = 'MT940950GEN'
        else:
            db['mur'] = muref.get()

        if chckv.get().strip() == '':
            db['chk'] = False
        else:
            db['chk'] = chckv.get()

        if bpc.get().strip() == '':
            db['f113'] = False
        else:
            db['f113'] = bpc.get().rjust(4, '0')

        if miref.get().strip() == '':
            db['mir'] = True
        else:
            db['mir'] = miref.get()

        if obp.get() == 'None':
            db['obs'] = ''
        else:
            db['obs'] = obp.get()[:3]

        if dmf.get() == 'None':
            db['dlvt_mnty'] = ''
        else:
            db['dlvt_mnty'] = dmf.get()[:1]

        pickle.dump(db, open("Settings.p", "wb"))

        ttl.config(text='Changes Saved')
        ttl.update_idletasks()

    def exit_settings(event=None):
        setwin.destroy()

    def help_me(event=None):
        try: webbrowser.open(r'http://www.ibm.com/support/knowledgecenter/SSBTEG_4.3.0/com.ibm.wbia_adapters.doc/doc/swift/swift72.htm%23HDRI1023624')
        except: pass

    # Button Frame
    btn = tkinter.Frame(setlblfrm, bg=bgclr)
    btn.grid(row=6, column=0, sticky='n', padx=5, pady=10)

    btn1 = tkinter.Frame(btn, bg=bgclr)
    btn1.grid(row=0, column=0, sticky='nw', padx=5)

    bsv = tkinter.Button(btn1, text='Save', width=8, command=save_settings, bg=btnclr2,
                         relief=winrlf, activebackground=actvclr)
    bsv.grid(row=0, column=0, padx=20, pady=5, sticky='w')

    clc = tkinter.Button(btn1, text='Close', width=8, command=exit_settings, bg=btnclr2,
                         relief=winrlf, activebackground=actvclr)
    clc.grid(row=0, column=1, padx=20, pady=5, sticky='w')

    btn2 = tkinter.Frame(btn, bg=bgclr)
    btn2.grid(row=0, column=1, sticky='ne', padx=5)

    hlp = tkinter.Button(btn2, text='help', width=5, command=help_me, bg=btnclr,
                         relief=winrlf, activebackground=actvclr)
    hlp.grid(row=0, column=0, padx=20, pady=5, sticky='e')

    setlblfrm.grid_columnconfigure(0, weight = 1)

    setwin.config(bg=bgclr)
    setwin.title('Settings Window')
    setwin.protocol("WM_DELETE_WINDOW", exit_settings)
    setwin.iconbitmap(icon)
    
    wlxym = '+%s+%s' % (str(screensizes[0] // 2 - 315), str(screensizes[1] // 2 - 280))
    
    setwin.geometry('630x560%s' % wlxym)

    setwin.mainloop()


def get_settings(return_error=False):
    '''
    Shelve File --> Dictionary
    Retrieve all settings from the pickled file and return them as a dictionary.
    If "return_error" is set to True, and exception during data retrieval will
    be returned.
    '''
    err = None
    try:
        xdb = pickle.load(open("Settings.p", "rb"))
    except Exception as e:
        xdb = False
        err = str(e)

    if err and return_error:
        return(xdb,err)

    return(xdb)

def make_settings(event=None):
    '''
    Create default settings.
    '''
    db = {}

    db['dtf']        = 'DDMMYYYY'
    db['appid']      = 'A'
    db['servid']     = '21'
    db['session_no'] = '0000'
    db['seqno']      = '000000'
    db['drctn']      = 'O'
    db['msg_prty']   = 'N'
    db['dlvt_mnty']  = ''
    db['obs']        = '003'
    db['inp_time']   = '0000'
    db['out_date']   = '010101'
    db['out_time']   = '1200'
    db['mir']        = True
    db['f113']       = False
    db['mur']        = 'MT940950GEN'
    db['chk']        = False

    pickle.dump(db, open("Settings.p", "wb"))

def main(event=None):
    screensize = get_screensize()

    if not os.path.isfile('Settings.p'):
        make_settings()

    tc_msg = '''The responsibility for ensuring the completeness of any output file and its
    compatibility with any system lies with you. The author(s) of this program,
    its owners, hosts, and affiliates, are not liable for any damages or loss
    (physical, material, financial, or otherwise), corruption of or loss of
    data, caused by the use of this program or its outputs. You use the output
    of this program at your own risk.'''

    okwindow(tc_msg, 490, 230, 'Notice', screensize)

    mt = 'Settings'
    while mt == 'Settings':
        mt = confirmwin('\nPlease select desired output format.', 
                        'MT940', 'MT950', 'Settings', 'Confirm', screensize)
        if mt == 'Settings':
            settings_window(screensize)

    if not mt:
        okwindow('The process was aborted.', 270, 100, 'Error!', screensize)
        sys.exit()

    root = tkinter.Tk()
    active_f = tkfd.askopenfilename(title='Select source file.')
    root.destroy()

    if not active_f:
        okwindow('The process was aborted.', 270, 100, 'Error!', screensize)
        sys.exit()
    elif not active_f.endswith(".csv"):
        okwindow('The input file is not a csv.', 270, 100, 'Error!', screensize)
        sys.exit()

    root = tkinter.Tk()
    target_f = tkfd.asksaveasfilename(title='Set destination file.')
    root.destroy()

    if not target_f:
        okwindow('The process was aborted.', 270, 100, 'Error!', screensize)
        sys.exit()
    elif not target_f.upper().endswith('.TXT'):
        target_f += '.txt'

    stgs = get_settings()

    if stgs:
        mt940_50.gen_mt9(active_f, mt, target_f, dtf=stgs['dtf'], appid=stgs['appid'], 
                         servid=stgs['servid'], session_no=stgs['session_no'], seqno=stgs['seqno'],
                         drctn=stgs['drctn'], msg_prty=stgs['msg_prty'], dlvt_mnty=stgs['dlvt_mnty'], 
                         obs=stgs['obs'], inp_time=stgs['inp_time'], out_date=stgs['out_date'],
                         out_time=stgs['out_time'], mir=stgs['mir'], f113=stgs['f113'],
                         mur=stgs['mur'], chk=stgs['chk'])
    else:
        mt940_50.gen_mt9(active_f, mt, target_f)

    okwindow('Process Completed.', 270, 100, 'Info', screensize)
    sys.exit()

if __name__ == '__main__':
    main()
