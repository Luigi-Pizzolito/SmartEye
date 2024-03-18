package main

import (
	"log"
	"time"
)

func main() {
	// Kafka brokers
	brokers := []string{"kafka:9092"}

	// Create a new KafkaProducer instance
	producer, err := NewKafkaProducer(brokers)
	if err != nil {
		log.Fatalf("Error creating Kafka producer: %v", err)
	}
	defer producer.Close()

	// Example of sending a message to a Kafka topic
	topic := "test-topic"
	message := []byte("Hello, Kafka!!")
	producer.SendMessage(topic, message)

	log.Println("Message sent asynchronously to Kafka topic:", topic)
	// Wait for a while to give the goroutine time to execute
	time.Sleep(1 * time.Second)
}
