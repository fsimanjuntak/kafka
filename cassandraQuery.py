from cassandra.cluster import Cluster
from cassandra.query import tuple_factory
from kafka import KafkaProducer
import datetime
from datetime import datetime
import time
import json


#Declare message queue variables
producer = KafkaProducer(bootstrap_servers = 'localhost:9092')

#producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))

#Set configuration of cassandra
cluster= Cluster()
session = cluster.connect('demo')
from cassandra.query import SimpleStatement
query = "SELECT * FROM tweets limit 1000"
statement = SimpleStatement(query, fetch_size=10)
for row in session.execute(statement):
    #Constructs JSON format
    data = {}
    #data['id'] = row.id
    data['tweet'] = row.tweet
    #data['created_at'] = str(row.tweet_date)
    json_data = json.dumps(data)
    print 'Sending message to queue',row.tweet
    #channel.basic_publish(exchange='',routing_key='tweet_fromdb_queue',body=row.tweet)
    producer.send('twitterstreaming',row.tweet.encode('utf-8'))
    #producer.flush()
