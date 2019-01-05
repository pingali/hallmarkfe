import os
import sys
import json 
import pytest

import hallmarkfe

clue = True

@pytest.fixture
def testdata(request):

    # => Load the test data...
    filename = request.param    
    if filename is None: 
        testdata = {}
    else:
        if not os.path.isabs(filename):
            filename = os.path.join(os.path.dirname(__file__), filename)
        testdata = json.load(open(filename))

    return testdata 

@pytest.fixture()
def user_incomplete():

    # => Gets automatically registered
    class Alpha(hallmarkfe.spec.SpecBase):
        schema = "user:default:v1"
            
        def initialize(self):
            self.required.extend([
                'id',
                'entity',
                'granularity',
                'uri',
                'tags',
                'options',
                'dataStores',
            ])

    yield Alpha 

    # Cleanup the function 
    hallmarkfe.spec.unregister(Alpha)     

@pytest.fixture()
def user_extra_cols():

    # => Gets automatically registered
    class Alpha(hallmarkfe.spec.SpecBase):
        schema = "user:default:v1"
            
        def initialize(self):
            self.required.extend([
                'id',
                'entity',
                'granularity',
                'uri',
                'tags',
                'options',
                'dataStores',
                'kilo'
            ])

    yield Alpha 

    # Cleanup the function 
    hallmarkfe.spec.unregister(Alpha)     
    
@pytest.mark.parametrize('testdata',
                         [
                             'fixtures/user.json',
                         ],
                         indirect=True)
def test_user_nohandler(testdata):
    """
    Test complex spec 
    """
    with pytest.raises(hallmarkfe.spec.SpecNoHandler) as exc:    
        obj = hallmarkfe.spec.parse(testdata)

@pytest.mark.parametrize('testdata',
                         [
                             'fixtures/user.json',
                         ],
                         indirect=True)
def test_user_incomplete_handler(testdata, user_incomplete):
    """
    Test complex spec 
    """
    # This should go through 
    obj = hallmarkfe.spec.parse(testdata)

@pytest.mark.parametrize('testdata',
                         [
                             'fixtures/user.json',
                         ],
                         indirect=True)
def test_user_invalid_spec(testdata, user_extra_cols):
    """
    Test complex spec 
    """
    # This should go through 
    with pytest.raises(hallmarkfe.spec.SpecInvalidSpecification) as exc:
        obj = hallmarkfe.spec.parse(testdata)
    
        
    
#                             'fixtures/storage.json',
#                             'fixtures/entity.json'
