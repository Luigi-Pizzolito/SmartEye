package main

import (
	"log"
	"strings"
	"time"

	"github.com/IBM/sarama"
)

// KafkaProducer represents a Kafka producer that sends messages to Kafka topics.
type KafkaProducer struct {
	producer sarama.SyncProducer
}

// NewKafkaProducer creates a new KafkaProducer instance.
func NewKafkaProducer(brokers []string) (*KafkaProducer, error) {
	config := sarama.NewConfig()
	config.Producer.RequiredAcks = sarama.WaitForLocal       // Only wait for the leader to ack
	config.Producer.Compression = sarama.CompressionSnappy   // Compress messages
	config.Producer.Flush.Frequency = 200 * time.Millisecond // Flush batches every 500ms
	config.Producer.Return.Successes = true

	producer, err := sarama.NewSyncProducer(brokers, config)
	if err != nil {
		return nil, err
	}

	return &KafkaProducer{
		producer: producer,
	}, nil
}

// SendMessage sends a message to the specified Kafka topic asynchronously.
func (kp *KafkaProducer) SendMessage(topic string, message []byte) {
	go func() {
		// Ensure the topic name is valid
		if strings.TrimSpace(topic) == "" {
			log.Println("Empty topic name")
			return
		}

		// Produce message and send it to Kafka
		_, _, err := kp.producer.SendMessage(&sarama.ProducerMessage{
			Topic: topic,
			Value: sarama.ByteEncoder(message),
		})

		if err != nil {
			log.Printf("Error sending message to Kafka: %v\n", err)
		}
	}()
}

// Close closes the Kafka producer.
func (kp *KafkaProducer) Close() {
	if kp.producer != nil {
		kp.producer.Close()
	}
}
