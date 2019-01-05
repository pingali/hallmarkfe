import sys 
import pytest 
import  hallmarkfe.supernova  as hallmarkfe

def test_processor(): 
    """
    Test the processor class 
    """

    proc = hallmarkfe.HFEProcessor(conf={
        'name': 'hello',
        'owner': 'Brian',
        'manager':'TestManager'
    }) 

    
def test_state():
    """
    Test state access 
    """
    state = hallmarkfe.HFEAtomicState()

    # 
    state.set_feature('hello', 'value')
    assert 'hello' in state.state['features']


def test_data():
    """
    Test data storage 
    """
    state = hallmarkfe.HFEAtomicState()

    # Value could be any time 
    state.set_data('hello', 'value')
    assert 'hello' in state.state['data'] 

    state.set_data('hello', [
        {
            '1': 2,
            '2': 1 
        }
    ])

    assert 'hello' in state.state['data']
        
    d = state.get_data('hello') 
    assert isinstance(d, list) 
