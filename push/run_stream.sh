#!/bin/bash

$SPARK_HOME/bin/spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2,com.datastax.spark:spark-cassandra-connector_2.11:2.0.0 --conf spark.cassandra.connection.host="127.0.0.1" streamingKafka.py
 
