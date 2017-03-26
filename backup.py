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


def getSqlContextInstance(sparkContext):
    if ('sqlContextSingletonInstance' not in globals()):
        globals()['sqlContextSingletonInstance'] = SQLContext(sparkContext)
    return globals()['sqlContextSingletonInstance']

def writetocassandra(dframewrite):
    dframewrite.write \
        .format("org.apache.spark.sql.cassandra") \
        .options(table="kafkaresults", keyspace="demo") \
        .save(mode="append")


#lines.pprint()
#lines.saveAsTextFiles('/home/frans/Desktop/TutorialKafka/output')

def process(time, rdd):
	sqlContext = getSqlContextInstance(rdd.context)
	try:
		print("*************************************************")		
		rowRdd = rdd.map(lambda w: Row(word=w))
		wordsDataFrame = sqlContext.createDataFrame(rowRdd)
		wordsDataFrame.registerTempTable("words")
		wordCountsDataFrame = sqlContext.sql("select word, count as total from words")
		wordCountsDataFrame.printSchema()
		writetocassandra(wordCountsDataFrame)
	except Exception as e:
		print (str(e))

#counts.foreachRDD(process)

#for(word, count) in output:
 #    print word + ': ' + str(count)

#lines = kvs.map(lambda x: x[1])

#counts = lines.flatMap(lambda line: line.split(" ")) \
#        .map(lambda word: (word, 1)) \
#        .reduceByKey(lambda a, b: a+b)
#counts.pprint()

#pairs = kafka_stream.map(wordsToPairsFunc)
#counts = pairs.reduceByKey(reduceToCount)

# Get the first top 100 words
#output = counts.takeOrdered(100, lambda (k, v): -v)
#print("testing")

#parsed.saveAsTextFile("/home/frans/Desktop/TutorialKafka/output")

#summed = parsed.map(lambda event: (event['site_id'], 1)).\
#                reduceByKey(lambda x,y: x + y).\
#                map(lambda x: {"site_id": x[0], "ts": str(uuid1()), "pageviews": x[1]})






counts = lines.flatMap(lambda line: line.split(" ")) \
        .map(lambda word: (word, 1)) \
        .reduceByKey(lambda a, b: a+b)
counts.pprint()

