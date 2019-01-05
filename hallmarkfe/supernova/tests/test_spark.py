import os
import sys
import json 
import pytest
import glob
import logging
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.functions import udf
from pyspark.sql.types import *

thisdir = os.path.abspath(os.path.dirname(__file__))

@pytest.fixture(scope="function")
def sparkctx_local():
    sc = SparkContext('local')
    return sc 

@pytest.fixture(scope="function")
def sparkctx_master():
    master = os.environ['SPARK_MASTER'] 
    sc = SparkContext(master)
    return sc 


def test_basic_spark(sparkctx_local):
    """
    Test using spark 
    """
    sc = sparkctx_local 
    sqlsc = SQLContext(sc)
    
    # Load as rdd
    fixture = os.path.join(thisdir, "fixtures", "call_log.csv")
    df = sqlsc.read.format("csv").option("header", "true").load(fixture) 

    # Checksum
    count = df.count()

    # Now run an RDD function...
    def reducefunc(g):
        key = g[0]
        rows = g[1] 
        rows = list(rows)
        return (key, len(rows))
    
    rdd = df.rdd
    collected = rdd.groupBy(lambda row: (row['In'])).map(reducefunc) 
    collected = collected.collect()

    # [('8609831078', 1610), ('8114258688', 2865), ('0314642949', 2497), ('2678392560', 5835), ('9598437862', 12053)]
    total = sum([x[1] for x in collected])
    assert count == total 

    

def find_egg():

    eggs = glob.glob(os.path.join(thisdir,
                                  "..", "dist", "*egg"))
                     
    eggs = sorted(eggs, reverse=True)
    if len(eggs) == 0:
        raise Exception("An egg has to be built first") 

    return eggs[0]

def test_basic_spark(sparkctx_local):
    """
    Test using spark 
    """
    sc = sparkctx_local 
    sqlsc = SQLContext(sc)

    # Debug logging...
    sc.setLogLevel("DEBUG")
    
    # Distribute code...
    egg = find_egg() 
    sc.addPyFile(egg) 
    sc.addPyFile(os.path.join(thisdir, 'helper.py'))
    
    # Load as rdd
    fixture = os.path.join(thisdir, "fixtures", "call_log.csv")
    df = sqlsc.read.format("csv").option("header", "true").load(fixture)
    def toseconds(s):
        # s = 0:03:11
        s = s.split(":")
        return (int(s[0]) * 3600) + (int(s[1]) * 60) + (int(s[2].split(".")[0]))

    # Now insert seconds 
    toseconds_udf = udf(toseconds, IntegerType())
    df = df.withColumn('DurationSeconds', toseconds_udf('Duration'))

    # Convert to RDD 
    rdd = df.rdd

    # Now reduce 
    from helper import reducefunc 
    collected = rdd.groupBy(lambda row: (row['In'])).map(reducefunc) 
    collected = collected.collect()
    
    assert len(collected) == df.select('In').distinct().count() 
