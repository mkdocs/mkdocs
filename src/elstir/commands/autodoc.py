"""
://medium.com/python-pandemonium/python-introspection-with-the-inspect-module-2c85d5aa5a48
"""
import inspect 


def getmarkdown(module):
    output = [ module_header ]
    output.extend(getfunctions(module))
    output.append("***\n")
    output.extend(getclasses(module))    
    return "".join(output)

def getclasses(item):
    output = list()
    for cl in inspect.getmembers(item, inspect.isclass):
        if cl[0] != "__class__" and not cl[0].startswith("_"):
            # Consider anything that starts with _ private
            # and don't document it            output.append( class_header )
            output.append(cl[0])               # Get the docstring
            output.append(inspect.getdoc(cl[1]))            # Get the functions
            output.extend(getfunctions(cl[1]))            # Recurse into any subclasses
            output.extend(getclasses(cl[1]))    
            return output

def getfunctions(item):
    output = list()
    for func in inspect.getmembers(item, inspect.isfunction):
        output.append( function_header )        
        output.append(func[0])        # Get the signature
        output.append("\n```python\n")
        output.append(func[0])
        output.append(str(inspect.signature(func[1])))        # Get the docstring
        output.append(inspect.getdoc(func[1])) 
        return output
