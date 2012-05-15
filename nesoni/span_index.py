"""

Efficiently index a collection of intervals.

"""



class Span_entry(object):
    """
        start
        end
        strand
        feature    
    """
    
    def __repr__(self):
        return '%d:%d %d %s' % (self.start,self.end,self.strand,self.feature)

def rounded_interval_size(size):
    """ Round the size of the interval down to the nearest
        power of two. """
    
    approx_size = 1
    while approx_size*2 < size: approx_size *= 2 
    return approx_size

def bisect_left(a, x, key_func):
    lo = 0
    hi = len(a)
    while lo < hi:
        mid = (lo+hi)//2
        if key_func(a[mid]) < x: lo = mid+1
        else: hi = mid
    return lo

class Span_index(object):
   def __init__(self):
       self.items = [ ]
       self.indexes = { }   # log2size -> (item sorted by left, item sorted by right)
       
       self.cache = { }

   def insert(self, start, end, strand, feature):
       item = Span_entry()
       item.start = start
       item.end = end
       item.strand = strand
       item.feature = feature
   
       self.items.append(item)
       size = rounded_interval_size(item.end-item.start)
       if size not in self.indexes:
           self.indexes[size] = ([],[])
       self.indexes[size][0].append(item)
       self.indexes[size][1].append(item)
   
   def prepare(self):
       for size in self.indexes:
           self.indexes[size][0].sort(key=lambda x: x.start)
           self.indexes[size][1].sort(key=lambda x: x.end)

   def get(self, start, end):
       key = (start, end)
       if key not in self.cache:
           if len(self.cache) > 1000000: self.cache = { } #!!!
       
           result = set()
           for size in self.indexes:
               a = bisect_left(self.indexes[size][0], start-size+1, lambda x: x.start)
               b = bisect_left(self.indexes[size][0], end, lambda x: x.start)
               result.update(self.indexes[size][0][a:b])
                
               a = bisect_left(self.indexes[size][1], start+1, lambda x: x.end)
               b = bisect_left(self.indexes[size][1], end+size, lambda x: x.end)
               result.update(self.indexes[size][1][a:b])
           self.cache[key] = result
           
           for item in result:
               assert item.start < end and start < item.end, 'Bad span lookup: '+repr((item.start, item.end, start, end))
           
           #for item in self.items:
           #    if item.start < end and start < item.end:
           #        assert item in result, repr((item.start, item.end, start, end))
           #    else:
           #        assert item not in result, repr((item.start, item.end, start, end))        
       
       return self.cache[key]


