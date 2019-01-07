import os
import sys
import json 
import pytest

import hallmarkfe

clue = True
abs_path = os.path.dirname(os.path.realpath(__file__))

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
def user_json_list():

    # => Gets automatically registered
    class Alpha(hallmarkfe.spec.SpecBase):
        schema = "user:default:v1"
        schema_list = ["user:default:v1"]
  
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
                             os.path.join(abs_path,'fixtures/user.json'),
                         ],
                         indirect=True)
def test_user_nohandler(testdata):
    """
    Test complex spec 
    """
    with pytest.raises(hallmarkfe.spec.SpecNoHandler) as exc:    
        obj = hallmarkfe.spec.parse_generic(testdata)

@pytest.mark.parametrize('testdata',
                         [
                             os.path.join(abs_path,'fixtures/user.json'),
                         ],
                         indirect=True)
def test_user_incomplete_handler(testdata, user_incomplete):
    """
    Test complex spec 
    """
    # This should go through 
    obj = hallmarkfe.spec.parse_generic(testdata)

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
        obj = hallmarkfe.spec.parse_generic(testdata)
    
        
    
#                             'fixtures/storage.json',
#                             'fixtures/entity.json'
@pytest.mark.parametrize('testdata',
                         [
                             os.path.join(abs_path,'fixtures/user_list.json'),
                         ],
                         indirect=True)
def test_user_json_list(testdata, user_json_list):
    """
    Test complex spec with list of dicts
    """
    # This should pass
    obj = hallmarkfe.spec.parse_generic(testdata)

@pytest.mark.parametrize('testdata',
                         [
                             os.path.join(abs_path,'fixtures/user.yaml'),
                             os.path.join(abs_path,'fixtures/user.yml'),                             
                         ],
                         indirect=False)
def test_user_yaml_list(testdata, user_json_list):
    """
    Test complex spec with list of dicts
    """
    # This should pass
    obj = hallmarkfe.spec.parse_generic(testdata)

@pytest.mark.parametrize('testdata',
                         [
                             os.path.join(abs_path,'fixtures/user_list.json')                        
                         ],
                         indirect=False)
def test_user_json_file(testdata, user_json_list):
    """
    Test complex spec with list of dicts
    """
    # This should pass
    obj = hallmarkfe.spec.parse_generic(testdata)

@pytest.mark.parametrize('testdata',
                         [
                             os.path.join(abs_path,'fixtures/')                        
                         ],
                         indirect=False)
def test_SpecManager(testdata, user_json_list):
    """
    Test complex spec with list of dicts
    """
    # This should pass
    obj = hallmarkfe.SpecManagerBase.scan_dir(testdata)


