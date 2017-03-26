from cassandra.cluster import Cluster
from cassandra.query import tuple_factory
from kafka import KafkaProducer
import datetime
from datetime import datetime
import time
import json


#declare message queue
producer = KafkaProducer(bootstrap_servers = 'localhost:9092')

#set Cassandra configurations
cluster= Cluster()
session = cluster.connect('demo')

#query tweets from Cassandra
from cassandra.query import SimpleStatement
query = "SELECT * FROM tweets limit 1000"
statement = SimpleStatement(query, fetch_size=10)
for row in session.execute(statement):
    print 'Sending message to queue',row.tweet
    #push tweet to message queue
    producer.send('twitterstreaming',row.tweet.encode('utf-8'))
    producer.flush()
