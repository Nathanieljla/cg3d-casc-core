


def apple(var1, var2=None, *args, **kwargs):
    print(var1)
    print(var2)
    
    
    
    
apple(1, 3, 4, 6)
apple(1)
print("done")




class A_class(object):
    
    @property
    def custom(self):
        return 10
    
    
class B_class(A_class):
    
    @A_class.custom.getter
    def custom(self):
        print("ere")
        return super().custom
    
    
    
b = B_class()
print(b.custom)