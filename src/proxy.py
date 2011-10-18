
import pywinauto
'''
proxy module for pywinauto 
'''

ACTIONS =  {101 : 'Close',
            102 : 'Click'
            }


pywinauto.timings.Timings.window_find_timeout = 1            

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
        texts = wind.Texts()
        while texts.count(''):
          texts.remove('')
        title = ', '.join(texts)
        if not title:
            title = 'Unknow title!'
        windows.append((title, wind))
    windows.sort(key=lambda name: name[0].lower())
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
        texts = control.Texts()
        while texts.count(''):
          texts.remove('')
        c_name = ', '.join(texts)
        if not c_name:
            c_name = 'Unknow control name!'
        subitems.append((c_name, control))
    return subitems

def _get_actions(pywin_obj):
    '''
    return allowed actions for this object. [(id,action_name),...]
    '''
    allowed_actions = []
    try:
        obj_actions = dir(pywin_obj.WrapperObject())
    except:
        obj_actions = dir(pywin_obj)
    #print obj_actions
    for id, action in ACTIONS.items():
        if action in obj_actions:
            allowed_actions.append((id,action))
    allowed_actions.sort(key=lambda name: name[1].lower())
    return allowed_actions
            
def exec_action(pywin_obj, action_id):
    action = ACTIONS[action_id]
    exec('pywin_obj.'+action+'()')
    return 0