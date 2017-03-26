#import pyspark_cassandra
#import pyspark_cassandra.streaming

#from pyspark_cassandra import CassandraSparkContext
from pyspark.sql import SQLContext,Row
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from uuid import uuid1
import json

from kafka import SimpleProducer, KafkaClient
from kafka import KafkaProducer


offsetRanges = []
positive_vocab = []
negative_vocab = []

#load dictionary positive and negative sentiment
fpos = open("/home/frans/Desktop/TutorialHDFS/dictionary/positive-words.txt","r")
for line in fpos:
    positive_vocab.append(line.strip())
fneg = open("/home/frans/Desktop/TutorialHDFS/dictionary/negative-words.txt","r")
for line in fneg:
    negative_vocab.append(line.strip())

#perform map function
def wordsToPairsFunc(word):
    #tupleword = ''.join(word)
    arrwords = word.lower().split(' ')
    total_pos = 0;
    total_neg = 0;

    for w in arrwords:
        if w in positive_vocab:
           total_pos = total_pos + 1;
        if w in negative_vocab:
           total_neg = total_neg + 1;
    
    sentiment = total_pos - total_neg;
    
    if sentiment > 0:
       return ("positive", 1)
    if sentiment < 0:
       return ("negative", 1)
    else:
       return ("neutral", 1)

#perform reduce function
def reduceToCount(a, b):
    return (a + b)


def storeOffsetRanges(rdd):
	global offsetRanges
	offsetRanges = rdd.offsetRanges()
	return rdd

def printOffsetRanges(rdd):
	for o in offsetRanges:
		print "%s %s %s %s" % (o.topic, o.partition, o.fromOffset, o.untilOffset)

def getSqlContextInstance(sparkContext):
    if ('sqlContextSingletonInstance' not in globals()):
        globals()['sqlContextSingletonInstance'] = SQLContext(sparkContext)
    return globals()['sqlContextSingletonInstance']

def writetocassandra(dframewrite):
    dframewrite.write \
        .format("org.apache.spark.sql.cassandra") \
        .options(table="realtimedata", keyspace="demo") \
        .save(mode="append")

# set up our contexts
conf = SparkConf().setAppName("PythonStreamingKafkaWordCount").setMaster("local[2]")
sc = SparkContext(conf=conf)
ssc = StreamingContext(sc, 2)

directKafkaStream = KafkaUtils.createDirectStream(ssc, ["twitterstreaming"], {"metadata.broker.list": "localhost:9092"})
print('=====================================================================')

rdd = directKafkaStream\
     .transform(storeOffsetRanges)

lines = rdd.map(lambda x: x[1])
pairs = lines.map(wordsToPairsFunc)
counts = pairs.reduceByKey(reduceToCount)
counts.pprint()


def process(time, rdd):
	sqlContext = getSqlContextInstance(rdd.context)
	try:
		print("*************************************************")		
		rowRdd = rdd.map(lambda s: Row(name=str(s[0]), count=long(s[1]), ts=str(uuid1())))
		wordsDataFrame = sqlContext.createDataFrame(rowRdd)
		wordsDataFrame.registerTempTable("words")
		wordCountsDataFrame = sqlContext.sql("select name as sentiment, count as total, ts from words")
		wordCountsDataFrame.printSchema()
		writetocassandra(wordCountsDataFrame)
	except Exception as e:
		print (str(e))

counts.foreachRDD(process)


print('=====================================================================')


ssc.start()
ssc.awaitTermination()


