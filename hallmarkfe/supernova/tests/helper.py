import logging
import  hallmarkfe.supernova  as hallmarkfe
import os, json

logger = logging.getLogger()

mgr1 = None 

class SimpleRuleProcessor1(hallmarkfe.HFERuleBasedProcessor,
                          hallmarkfe.MetricHandlerMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.metric_handlers = {
            'total': lambda args, rows: self.toolz_sum('DurationSeconds', rows),
            'dates': lambda args, rows: self.toolz_count('CallDate', rows),
        }
        
        testsdir = os.path.join(os.environ['ENRICH_DATA'],
                                    'hallmark', 'specs')
        self.datasets = { 
            'complex_data': { 
                'name': 'complex', 
                'metadata': os.path.join(testsdir, 'complex1.json'),
                'params': {
                }
            }
        }
        
def get_mgr1(): 
    global mgr1
    if mgr1 is not None:
        return mgr1

    logger.debug("Creating a new mgr")
    
    mgr1 = hallmarkfe.HFEManager({
        'processors': ['complex1'] 
    }) 

    myproc1 = SimpleRuleProcessor1(conf={
        'name': 'complex1',
        'owner': 'marketing',
        'manager': 'Manager'  
    })

    with open(myproc1.datasets['complex_data']['metadata']) as json_file:  
        myproc1.rules = json.load(json_file)['rules']

    mgr1.add_processor('complex1', myproc1) 
    return mgr1

    
def reducefunc(g):

    mgr1 = get_mgr1() 
    
    key = g[0]
    rows = g[1]
    rows = list(rows)

    # logger.error("One row: " + str(rows[0])) 
    
    state = hallmarkfe.HFEAtomicState()
    state.set_feature('In', key) 
    state.set_data('calls', rows) 
    
    # Now collect all the tags 
    mgr1.process(state) 
    
    features = state.get_all_features()

    return features 
