# -*- coding: utf-8 -*-
import numpy as np

def values_extend(values, unique=False, toString=False):
    """ Extend targets/sources e.g. if target is '1-3, 5', it converts into '1,2,3,5'. """
    
    value_list = values.split(',')
    extended_list = []
    for value in value_list:
        if '-' in value:
            start, end = value.split('-')
            
            assert int(start) < int(end)
            value = [i for i in range(int(start), int(end)+1)]
            extended_list.extend(value)
        else:
            extended_list.append(int(value))
            
    # Make each target/source value unique and sorted
    if unique:
        extended_list = list(set(extended_list))
        
    # Convert each value into string
    if toString:
        extended_list = map(lambda x: str(x), extended_list)
        
    return extended_list

def id_escape(id_filterbank, tid=None):
    """ Return user visible id from true id. """
    tids = np.array(id_filterbank[:,0], dtype=float)
    vids = np.array(id_filterbank[:,1], dtype=int)

    if float(tid) in tids: 
        return vids[tids.tolist().index(float(tid))]
        
    return np.array([], dtype=int)
    
def id_identify(id_filterbank, vid=None):
    """ Return true id from user visible id. """
    tids = np.array(id_filterbank[:,0], dtype=int)
    vids = np.array(id_filterbank[:,1], dtype=float)
    
    if vid == -1:
        return tids[vids == -1]
    
    if float(vid) in vids: 
        return tids[vids.tolist().index(float(vid))]
        
    return np.array([], dtype=int)