package main

import (
	"fmt"

	"github.com/IBM/sarama"
)

// Kafka Multi-Stream reader struct
type kafkaMultiStreamReader struct {
	brokers []string
	config  *sarama.Config
}

func NewKafkaMultiStreamReader(brokers []string) *kafkaMultiStreamReader {
	// Initialize Kafka consumer
	config := sarama.NewConfig()
	config.Consumer.Return.Errors = true
	// Return struct
	return &kafkaMultiStreamReader{
		brokers: brokers,
		config:  config,
	}
}

func (k *kafkaMultiStreamReader) consumeTopicFrames(topic string, bcast *broadcast) {
	defer wg.Done()

	// Create new Kafka consumer
	consumer, err := sarama.NewConsumer(k.brokers, k.config)
	if err != nil {
		panic(err)
	}
	defer consumer.Close()

	partitionConsumer, err := consumer.ConsumePartition(topic, 0, sarama.OffsetOldest)
	if err != nil {
		panic(err)
	}
	defer partitionConsumer.Close()

	// Recieve messages
	for {
		select {
		case msg := <-partitionConsumer.Messages():
			// send frames to broadcast group
			bcast.SendMessage(msg.Value)
			// update FPS counters
			fpsman.frame(topic)
		case err := <-partitionConsumer.Errors():
			fmt.Println("Error consuming from Kafka:", err)
		}
	}
}
