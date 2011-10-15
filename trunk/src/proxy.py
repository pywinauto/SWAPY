
import pywinauto
'''
proxy module for pywinauto 
'''

def test():
    return '1'

def _get_windows():
    '''
    returns [(window_text, window_obj),...]
    '''
    windows = []
    app = pywinauto.application.Application()
    handles = pywinauto.findwindows.find_windows(title_re='.*')
    for w_handle in handles:
        wind = app.window_(handle=w_handle)
        title = wind.Texts()[0]
        if not title:
            title = 'Unknow title!'
        windows.append((title, wind))
    return windows

def _get_properties(pywin_obj):
    '''
    returns {p_name: p_value,..}
    '''
    properties = pywin_obj.GetProperties()
    return properties

def _get_subitems(pywin_obj):
    '''
    returns [(control_text, control_obj),...]
    '''
    subitems = []
    controls = pywin_obj.Children()
    for control in controls:
        c_name = control.Texts()[0]
        if not c_name:
            c_name = 'Unknow control name!'
        subitems.append((c_name, control))
    return subitems