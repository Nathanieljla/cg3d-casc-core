from collections.abc import Collection 

class Test(object):
    def __init__(self):
        super(Test, self).__init__()
        
    
    def __getattr__(self, attr):
        def wrapper(*args, **kwargs):
            print('{}'.format(attr))
            print(args.__class__.__name__)
            print(kwargs)
            
        return wrapper #lambda *args, ** kwargs: wrapper(args, **kwargs)
    
    
    def bobby(self):
        result = "Name"
        raise AttributeError(result, result, result)
    
    
class Toot(Test):
    pass
        
        
        
        
        

apple = Test()
#shoe = Toot()

#print(isinstance(shoe, Test))

#name = 'name'

#print(isinstance(name, Collection))


apple.bobby() #1, bob=True)
print("done")
