# coding: utf-8
"""
Supernova
---------

This is a library that can be used to build feature generation
code. It has components for state management and extensible feature
generators (called processors), and associated manager. It has
built-in rule-based processor that provides a DSL for specifying
features, and a mixin for common metrics in the retail industry.
"""
import re 
import copy
import logging 
import collections
try:
    import cytoolz as toolz
except:
    import toolz 

class HFEAtomicState(object):
    """
    Feature State for a unit entity such as a customer. This is updated
    by feature engineering libraries.
    """
    def __init__(self, *args, **kwargs):
        self.history = []
        self.state = {
            'features': collections.OrderedDict([]),
            'data': {
            }
        }

    def get_feature_list(self):
        return list(self.state['features'].keys())

    def get_all_features(self):
        return copy.copy(self.state['features'])

    def set_feature(self, name, value):
        self.state['features'][name] = value

    def get_feature(self, name,):
        return self.state['features'][name]

    def get_data(self, name):
        if name not in self.state['data']:
            raise Exception("Unknown dataset: {}".format(name))
        return self.state['data'][name]

    def set_data(self, name, value):
        self.state['data'][name] = value


class HFEProcessor(object):
    """
    This module generates new multi-level features.


    """
    def __init__(self, conf, *args, **kwargs):
        self.conf = conf
        
        if 'name' not in conf or 'owner' not in conf: 
            raise Exception("Missing 'name' or 'owner' in Processor configuration") 

        self.name  = conf['name']
        self.owner = conf['owner']
        self.manager = conf['manager'] 
        
    def process(self, state, level):
        """
        Run this processor on the state at level

        Args:
          state (class): Feature state for the entity
          level (int): Level of the feature
        """
        pass

    def autodoc(self):
        """
        Automatic documentation 
        """
        return {}
    
    
class MetricHandlerMixin(object):
    """
    Mixin with helper functions to make life simpler
    """
    def toolz_sum(self, col, rows, dtype=None):
        """
        Sum a given column in a list of dictionaries

        Args:
           col (str): Column to process
           rows (list): Records
        """
        values = list(toolz.pluck(col, rows))
        if dtype is not None:
            values = [dtype(v) for v in values]

        return sum(values) 

    def toolz_min(self, col, rows):
        """
        Min of values for a given column in a list of dictionaries

        Args:
           col (str): Column to process
           rows (list): Records
        """
        return min(list(toolz.pluck(col, rows)))

    def toolz_max(self, col, rows):
        """
        Max of values for a given column in a list of dictionaries

        Args:
           col (str): Column to process
           rows (list): Records
        """
        return max(list(toolz.pluck(col, rows)))

    def toolz_count(self, col, rows):
        """
        Unique values for a given column in a list of dictionaries

        Args:
           col (str): Column to process
           rows (list): Records

        """
        return len(set(list(toolz.pluck(col, rows))))

    def toolz_avg(self, col, rows):
        """
        Unique values for a given column in a list of dictionaries

        Args:
           col (str): Column to process
           rows (list): Records

        """

        count = len(rows)
        total = sum(list(toolz.pluck(col, rows)))
        return total/count if count > 0 else None

    def clean_string(self, name):
        """
        Make the name column safe for use in URLs and database

        Args:
           name (str): string to clean
        """
        cleaned = ''.join([e if e.isalnum() else "_" for e in name])
        cleaned = re.sub('_+', '_', cleaned)
        return cleaned

class TableRuleMixin(object):

    def table_evaluate_rule(self, row, rule, depth=0):
        """
        Recursively evaluate a rule on a record

        Args:
          row (dict): Raw tags/transactions over which the rule must be applied
          rule (dict): Rule specification
        """
        match = rule["match"].strip().upper()
        values = rule["values"]

        # Non-root
        if match in ['AND', 'ALL']:
            results = []
            for subrule in values:
                result = self.table_evaluate_rule(row, subrule, depth+1)
                results.append(result)
            return all(results)
        elif match in ["OR", "ANY"]:
            results = []
            for subrule in values:
                result = self.table_evaluate_rule(row, subrule, depth+1)
                results.append(result)
            return any(results)
        elif match in ["NAND"]:
            # 0 if all
            # 1 otherwise
            results = []
            for subrule in values:
                result = self.table_evaluate_rule(row, subrule, depth+1)
                results.append(result)
            return not all(results)
        elif match in ["XNAND"]:
            # 1 if any of them is true but not all
            # 0 otherwise
            results = []
            for subrule in values:
                result = self.table_evaluate_rule(row, subrule, depth+1)
                results.append(result)
            return (not all(results)) and (any(results))
        elif match in ["NOR"]:
            results = []
            for subrule in values:
                result = self.table_evaluate_rule(row, subrule, depth+1)
                results.append(result)
            return not any(results)

        # Leaf node
        elif match in ["CONTAINS_ALL", "CONTAINS_ANY", "CONTAINS_NONE"]:
            col = rule['column']
            data = row[col].upper()
            results = [v.strip().upper() in data for v in values]
            if match == "CONTAINS_ALL":
                return all(results)
            elif match == "CONTAINS_ANY":
                return any(results)
            else:
                # contains_none
                return not any(results)

        elif match in ["IN"]:
            col = rule['column']
            data = row[col].upper()
            return data in [v.upper() for v in values]
        elif match in ["NOTIN"]:
            col = rule['column']
            data = row[col].upper()
            return data not in [v.upper() for v in values]
        elif match in ["GT", "GTE", "LT", "LTE"]:
            col = rule['column']
            data = row[col]
            if not (isinstance(values, int) or
                    instance(values, float)):
                raise Exception("Invalid specification: GT/LT spec should have an integer or float")
            if match == "GT":
                result = data > values
            elif match == "GTE":
                result = data >= values
            elif match == "LT":
                result = data < values
            else:
                result = data <= values

            return result

        return False

    def handler_table_apply_rule(self, state, rule, details):

        rule_name = rule['name']

        # print("Applying rule", rule_name)
        
        level  = details['level']
        params = details['params']

        table    = params['table']
        match    = params.get('match',None) 
        rule     = params.get('rule', None) 
        metrics  = params['metrics']

        rows = state.get_data(table)

        if len(rows) == 0:
            # print("Empty table") 
            return

        # Get the columns that should be processed
        # using this rule.
        row0 = rows[0]
        if hasattr(row0, 'asDict'):
            # Special case: Handle Pyspark Row object...
            row0 = row0.asDict()
        row_keys = [str(i) for i in list(row0.keys())]
        allcols = sorted(row_keys)

        cols = []
        if match is not None:
            search = "^" + match + "$"
            for c in allcols:
                if re.search(search, c): 
                    cols.append(c)
            # print("Matched Cols", cols)
            # print("All cols", allcols) 
        else:
            cols = allcols[:1] 
                    
        # Now apply the filter for the rows...
        if rule is not None: 
            filtered_rows = [r for r in rows \
                             if self.table_evaluate_rule(r, rule)]
        else:
            # Include every thing if no rule is specified 
            filtered_rows = rows
        # print("Filtered rows", len(filtered_rows))

        if len(filtered_rows) == 0:
            return
        
        for col in cols: 
            for mparams in metrics:

                mname = mparams['name']
                
                # Make a copy of the metrics...
                margs = copy.copy(mparams.get('args',{}))
                
                mhandler = mparams['handler'] 
                mhandler = self.metric_handlers[mhandler] 
                stream_type = self.stream_type

                # Insert extra information 
                margs.update({
                    'owner': self.owner,
                    'rule_name': rule_name, 
                    'name': mname, 
                    'level': level,
                    'match': col,
                    'stream_type': stream_type,
                })

                # If no suffix is specified, then use the name..
                if 'suffix' not in margs:
                    margs['suffix'] = mname

                if 'feature' not in margs: 
                    margs['feature'] = "tag__%(owner)s__%(rule_name)s__%(level)s__%(suffix)s"
                    
                # Now compute value...
                value = mhandler(margs, filtered_rows)
                
                # Generate a name for the feature...
                feature = self.generate_feature_name(margs) 

                # print("Value", col, mname, feature, value)
                
                # Now update the feature table...
                state.set_feature(feature, value)

    def generate_feature_name(self, params): 
        """
        Generate feature name...
        """
        feature = params['feature'] % params 
        return feature 
            
    def table_autodoc_rule(self, rule, depth=0):

        match = rule["match"].upper()
        values = rule["values"]

        # Non-root
        if match in ['AND', 'ALL']:
            results = []
            for subrule in values:
                result = self.table_autodoc_rule(subrule, depth+1)
                results.append(result)
            return "( '" + "' ) AND ( '".join(results) + "' )"
        elif match in ["OR", "ANY"]:
            results = []
            for subrule in values:
                result = self.table_autodoc_rule(subrule, depth+1)
                results.append(result)
            return "( '" + "' ) OR ( '".join(results) + "' )"

        elif match in ["NAND"]:
            results = []
            for subrule in values:
                result = self.table_autodoc_rule(subrule, depth+1)
                results.append(result)
            return "not matching ( '" + "' ) AND ( '".join(results) + "' )"
        elif match in ["NOR"]:
            results = []
            for subrule in values:
                result = self.table_autodoc_rule(subrule, depth+1)
                results.append(result)
            return "not matching ( '" + "' ) OR ( '".join(results) + "' )"
        # Leaf node
        elif match in ["CONTAINS_ALL", "CONTAINS_ANY"]:
            col = rule['column']
            if match == "CONTAINS_ALL":
                return "{} value contains all ({}) ".format(col, ", ".join(values))
            else:
                return "{} value contains one of ({}) ".format(col, ", ".join(values))

        elif match in ["IN"]:
            col = rule['column']
            return "{} value is in ({}) ".format(col, ", ".join(values))
        elif match in ["NOTIN"]:
            col = rule['column']
            return "{} value is not in ({}) ".format(col, ", ".join(values))
        elif match in ["GT", "GTE", "LT", "LTE"]:
            col = rule['column']
            if not (isinstance(values, int) or
                    instance(values, float)):
                raise Exception("Invalid specification: GT/LT spec should have an integer or float")
            if match == "GT":
                doc = "{} value is > {}".format(col, values)
            elif match == "GTE":
                doc = "{} value is >= {}".format(col, values)
            elif match == "LT":
                doc = "{} value is < {}".format(col, values)
            else:
                doc = "{} value is <= {}".format(col, values)

            return doc

        return "Unknown condition: {}".format(match)

class HFERuleBasedProcessor(HFEProcessor, TableRuleMixin):
    """
    Given a set of rules it apply the rules to rows
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix_template = "tag_%(owner)s_%(name)s_%(level)s_v%(version)s_rules_"
        self.rules = []
        self.stream_type=""
        self.metric_handlers = {
        }
        self.operator_handlers = {
            'handler_table_apply_rule': self.handler_table_apply_rule
        }


    def process(self, state, level):
        """
        Run function of rule-based tagger

        Args:
          state (class): Feature state for the entity
          level (int): Level of the feature
        """

        # print("Process function of FERuleBasedProcessor")
        for rule in self.rules:
            for operator in rule['operators']:

                # Look at operators that match a given level
                if operator.get('level', 1) != level:
                    continue

                handler_name = operator.get('handler')
                operator_handler = self.operator_handlers[handler_name]
                
                # This will update the state inline
                operator_handler(state, rule, details=operator)

    def autodoc(self):
        """
        Automatic documentation 
        """
        result = {} 
        for r in self.rules:        
            pass 
            
        return result
    
class HFEManager(object):
    """
    Hallmark Feature Engineering manager. This creates the
    states and runs through all the fe processors
    """
    def __init__(self, conf, *args, **kwargs):

        if not isinstance(conf, dict):
            raise Exception("Invalid FEManager configuration. Expecting dict") 
        self.conf = conf
        self.sequence = conf.get('sequence', []) 
        self.processors = {}

    def add_processor(self, name, proc):
        self.processors[name] = proc

    def resolve(self, path, extra={}):
        """
        Resolve path that the processor needs. Separating 
        this from the processor allows the processor to be
        used in multiple contexts. 
        """
        if 'config' in self.conf:
            config = self.conf['config']
            if hasattr(config, 'get_file'):
                return config.get_file(path, extra)
            elif hasattr(config, 'resolve'):
                return config.resolve(path, extra)

        return path % extra 

    def set_sequence(self, sequence):
        if not isinstance(sequence, list):
            raise Exception("Invalid FEManager configuration. Expecting sequence as a list") 

        self.sequence = sequence
        
    def process(self, festate):
        # Collect the processor instances
        processors = [self.processors[n] for n in self.sequence] 
        
        # Go through all the processors for all levels of
        # computation...
        for level in [1,2,3,4]:
            computed = festate.get_all_features()
            # Create a table that the rules can use..
            festate.set_data('__computed__', [computed])
            for proc in processors:
                proc.process(festate, level)

    def get_processors(self):

        # Collect the processor instances
        processors = [self.processors[n] for n in self.sequence] 
        return processors

    def get_taggers(self):
        return self.get_processors() 
