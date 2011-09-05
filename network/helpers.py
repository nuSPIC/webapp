# -*- coding: utf-8 -*-

def values_extend(values, unique=False, toString=False):
    """
    Extend targets/sources e.g. if target is '1-3, 5', it converts into '1,2,3,5'.
    """
    
    value_list = values.split(',')
    extended_list = []
    for value in value_list:
        if '-' in value:
            start, end = value.split('-')
            value = [i for i in range(int(start), int(end)+1)]
            extended_list.extend(value)
        else:
            extended_list.append(int(value))
            
    # Make each target value unique and sorted
    if unique:
        extended_list = list(set(extended_list))
        extended_list.sort()
        
    # Convert each value into string
    if toString:
        extended_list = map(lambda x: str(x), extended_list)
        
    return extended_list
