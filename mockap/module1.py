import pywinauto

class Obj_browser():
    """
    Proxy between UI and pywinauto module
    """
    
    def __init__(self):
#        self.__application = pywinauto.application.Application()
        self.__processes = [{'name':'', 'pid':''}]
        self.__get_procs()
        
 #   def __del__(self):
        
        
    
    def __get_procs(self):
        self.__processes = []
        handles = pywinauto.findwindows.find_windows()
        for handle in handles:
            try:
                name = pywinauto.handleprops.text(handle)
                pid = pywinauto.handleprops.processid(handle)
            except:
                print('Seems process %s is not exist...' % name)
            else:
                if name and pid:   
                    self.__processes.append({'name':name, 'pid':pid})
                
    def get_process(self):
        return self.__processes
            
        
    