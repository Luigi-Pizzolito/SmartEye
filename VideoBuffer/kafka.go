package main

/* ********************************************************************
   * Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
/* ********************************************************************/

// Class to handle sending MJPEG streams to Kafka topics

import (
	"log"
	"strings"

	"github.com/IBM/sarama"
)

// KafkaProducer represents a Kafka producer that sends messages to Kafka topics.
type KafkaProducer struct {
	producer sarama.AsyncProducer
}

// NewKafkaProducer creates a new KafkaProducer instance.
func NewKafkaProducer(brokers []string) (*KafkaProducer, error) {
	config := sarama.NewConfig()
	config.Producer.RequiredAcks = sarama.NoResponse // Only wait for the leader to ack
	// config.Producer.Compression = sarama.CompressionSnappy  // Compress messages
	// config.Producer.Flush.Frequency = 30 * time.Millisecond // Flush batches every 30ms
	// config.Producer.Return.Successes = true
	config.Producer.Retry.Max = 0

	producer, err := sarama.NewAsyncProducer(brokers, config)
	if err != nil {
		return nil, err
	}
	// defer func(producer sarama.AsyncProducer) {
	// 	// if err := producer.Close(); err != nil {
	// 	// 	log.Fatalln(err)
	// 	// }
	// 	producer.AsyncClose()
	// }(producer)

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
		// _, _, err := kp.producer.SendMessage(&sarama.ProducerMessage{
		// 	Topic: topic,
		// 	Value: sarama.ByteEncoder(message),
		// })
		kp.producer.Input() <- &sarama.ProducerMessage{Topic: topic, Value: sarama.ByteEncoder(message)}
		go func(producer sarama.AsyncProducer) {
			select {
			case success := <-producer.Successes():
				log.Println("Message produced:", success.Offset)
			case err := <-producer.Errors():
				log.Println("Failed to produce message", err)
			}
		}(kp.producer)

		// if err != nil {
		// 	log.Printf("Error sending message to Kafka: %v\n", err)
		// }
	}()
}

// Close closes the Kafka producer.
func (kp *KafkaProducer) Close() {
	if kp.producer != nil {
		kp.producer.Close()
	}
}
