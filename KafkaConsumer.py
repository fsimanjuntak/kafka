from kafka import KafkaConsumer
consumer = KafkaConsumer('twitterstreaming')
for msg in consumer:
	print (msg)
