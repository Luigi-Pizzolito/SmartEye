package main

import (
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/IBM/sarama"
)

// Kafka Multi-Stream reader struct
type kafkaMultiStreamReader struct {
	brokers []string
	config  *sarama.Config

	framestreams []string
}

func NewKafkaMultiStreamReader(brokers []string, validstreams []string) *kafkaMultiStreamReader {
	// Initialize Kafka consumer
	config := sarama.NewConfig()
	config.Consumer.Return.Errors = true
	// Return struct
	return &kafkaMultiStreamReader{
		brokers:      brokers,
		config:       config,
		framestreams: validstreams,
	}
}

func (k *kafkaMultiStreamReader) getFrameTopicsList() []string {
fetch_topics:
	admin, err := sarama.NewClusterAdmin(k.brokers, k.config)
	if err != nil {
		log.Fatalf("Error creating Kafka admin client: %v", err)
	}
	defer admin.Close()

	// List all topics
	topics, err := admin.ListTopics()
	if err != nil {
		log.Fatalf("Error listing topics: %v", err)
	}

	//  Check if topics have already been created, if not, wait
	found := false
	for topic := range topics {
		if ContainsAnySubstring(topic, k.framestreams) {
			found = true
			break
		}
	}
	if !found {
		fmt.Println("Waiting for streams to start...")
		time.Sleep(time.Second)
		goto fetch_topics
	}

	// Filter topics that contain k.framestreams substrings
	frameTopics := make([]string, 0)
	for topic := range topics {
		if ContainsAnySubstring(topic, k.framestreams) {
			frameTopics = append(frameTopics, topic)
		}
	}

	return frameTopics
}

// ContainsAnySubstring checks if any string in a slice contains any of the substrings
func ContainsAnySubstring(str string, substrs []string) bool {
	for _, sub := range substrs {
		if strings.Contains(str, sub) {
			return true
		}
	}
	return false
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
