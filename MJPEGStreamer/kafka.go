package main

/* ********************************************************************
   * Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
/* ********************************************************************/

// Class to handle reading MJPEG streams from Kafka topics
// as well as listing Kafka topics with valid streams

import (
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/IBM/sarama"
)

// Kafka Multi-Stream reader struct
type KafkaMultiStreamReader struct {
	brokers []string
	config  *sarama.Config

	framestreams []string
}

// Kafka Multi-Stream reader initialiser
func NewKafkaMultiStreamReader(brokers []string, validstreams []string) *KafkaMultiStreamReader {
	// Initialize Kafka consumer
	config := sarama.NewConfig()
	config.Consumer.Return.Errors = true
	// Return struct
	return &KafkaMultiStreamReader{
		brokers:      brokers,
		config:       config,
		framestreams: validstreams,
	}
}

// Method for getting a list of valid MJPEG stream Kafka topics
func (k *KafkaMultiStreamReader) getFrameTopicsList() []string {
fetch_topics:
	// Start a Kafka cluster admin to be able to access the topic list
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

	//  Check if valid topics have already been created, if not, wait and try again
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

	// return list of valid MJPEG stream topics
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

// Method for consuming MJPEG frames
// forwarding the frame data to a broadcast group
// and updating the stream's FPS counter
func (k *KafkaMultiStreamReader) consumeTopicFrames(topic string, bcast *Broadcast) {
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
