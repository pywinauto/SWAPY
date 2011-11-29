
import pywinauto
import time
import wx
import thread
import exceptions
import platform

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
    
def _get_additional_properties(pywin_obj):
    '''
    returns {p_name: p_value,..}
    '''
    try:
      parent_obj = pywin_obj.Parent()
    except:
      return {}
    else:
      additional_properties = {}
      try:
        all_controls = parent_obj.Children()
      except:
        pass
      else:
        uniq_names = pywinauto.findbestmatch.build_unique_dict(all_controls)
        #print len(uniq_names)
        for uniq_name, obj in uniq_names.items():
          if obj == pywin_obj:
            access_name = uniq_name
            break
          else:
            access_name = 'Unknown'
        additional_properties = {'Access name' : access_name}
      return additional_properties

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
        try:
            c_name_str = str(c_name)
        except exceptions.UnicodeEncodeError:
            c_name_str = c_name.encode('unicode-escape', 'replace')
        subitems.append((c_name_str, control))
    subitems.sort(key=lambda name: name[0].lower())
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
    
def _get_pywinobj_type(pywin_obj):
    if type(pywin_obj) == pywinauto.application.WindowSpecification:
      return 'window'
    elif 1==0:
      return 'other'
    else:
      return 'unknown'
    
def exec_action(pywin_obj, action_id):
    action = ACTIONS[action_id]
    exec('pywin_obj.'+action+'()')
    return 0
    
def get_code(pywin_obj, action_id):
    action = ACTIONS[action_id]
    if _get_pywinobj_type(pywin_obj) == 'window':
      code = "\
w_handle = pywinauto.findwindows.find_windows(title_re=u'"+ pywin_obj.WindowText().encode('unicode-escape', 'replace') +"', class_name='"+ pywin_obj.Class() +"')[0]\n\
window = pwa_app.window_(handle=w_handle)\n\
window."+action+"()\n\
"
    else:
      code = "\
window['"+_get_additional_properties(pywin_obj)['Access name']+"']."+action+"()\n\
"
    #exec('pywin_obj.'+action+'()')
    return code

def highlight_control(control):
    def _highlight_control(control, repeat = 1):
            while repeat > 0:
                repeat -= 1
                control.DrawOutline(thickness=1)
                time.sleep(0.3)
                control.DrawOutline(colour=0xffffff, thickness=1)
                time.sleep(0.2)
    thread.start_new_thread(_highlight_control,(control,3))
        
class SysInfo(object):
    handle = 0
    
    def Children(self):
        return []
        
    def Rectangle(self):
        return 0
        
    def GetProperties(self):
        info = { 'Platform' : platform.platform(), \
                'Processor' : platform.processor(), \
                'PC name' : platform.node() }
        return info