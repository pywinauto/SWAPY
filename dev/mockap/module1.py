import pywinauto

class Obj_browser():
    """
    Proxy between UI and pywinauto module
    """
    
    def __init__(self):
#        self.__application = pywinauto.application.Application()
        self.__processes = [] # {'handle':'', 'name':'', 'pid':''}
        self.__get_procs()
        self.__application = pywinauto.application.Application()
        
    def __del__(self):
        del self.__application
        
    
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
                    self.__processes.append({'name':name, 'pid':pid, 'handle':handle})
                
    def get_process(self):
        return self.__processes
    
    def get_children_list(self, handle):
        children_list = [] # {'wrap_name':'', 'texts':''}
        window = self.__application.window_(handle=handle)
        for child in window.Children():
            str_type = str(type(child)).split("'")[-2].split('.')[-1] #return wrapper name of control
            texts = child.Texts()
            children_list.append({'wrap_name':str_type, 'texts':texts}) 
        return children_list
            
        
    