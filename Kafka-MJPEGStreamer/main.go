package main

import (
	"bytes"
	"fmt"
	"io"
	"log"

	"mime/multipart"
	"net/http"
	"net/textproto"
	"strconv"
	"sync"
	"time"

	"io/ioutil"
	"path/filepath"
)

var (
	mux sync.Mutex
	// kafkaChannel chan []byte
	JPEGFrames []string
	// frameChannel chan []byte
	bcast *broadcast

	wg sync.WaitGroup
)

func consumeFromKafka(topic string) {
	// // Initialize Kafka consumer
	// config := sarama.NewConfig()
	// config.Consumer.Return.Errors = true

	// brokers := []string{"localhost:9092"} // Update with your Kafka broker address
	// consumer, err := sarama.NewConsumer(brokers, config)
	// if err != nil {
	// 	panic(err)
	// }
	// defer consumer.Close()

	// partitionConsumer, err := consumer.ConsumePartition("image-topic", 0, sarama.OffsetOldest)
	// if err != nil {
	// 	panic(err)
	// }
	// defer partitionConsumer.Close()

	// for {
	// 	select {
	// 	case msg := <-partitionConsumer.Messages():
	// 		select {
	// 		case kafkaChannel <- msg.Value:
	// 		default:
	// 			// If kafkaChannel is full, remove the oldest frame (first inserted)
	// 			<-kafkaChannel
	// 			kafkaChannel <- msg.Value
	// 			fmt.Println("Removed oldest frame - Kafka channel is full")
	// 		}
	// 	case err := <-partitionConsumer.Errors():
	// 		fmt.Println("Error consuming from Kafka:", err)
	// 	}
	// }

	defer wg.Done()

	var err error
	JPEGFrames, err = readJPEGFrames("../img")
	if err != nil {
		fmt.Println("Read frame error: ", err)
		panic(err)
	}
	for _, frame := range JPEGFrames {
		/*
			select {
			case kafkaChannel <- []byte(frame):
			default:
				// if full, remove oldest and insert
				<-kafkaChannel
				kafkaChannel <- []byte(frame)
				fmt.Println("Removed oldest frame - Kafka channel is full")
			}
			time.Sleep(100 * time.Millisecond)
		*/
		bcast.SendMessage([]byte(frame))
		time.Sleep(100 * time.Millisecond)
	}
}

func readFileToString(filename string) (string, error) {
	// Read the entire file into a byte slice
	content, err := ioutil.ReadFile(filename)
	if err != nil {
		return "", err
	}

	// Convert the byte slice to a string
	str := string(content)
	return str, nil
}

// readJPEGFrames reads all JPEG files from the specified directory
func readJPEGFrames(directory string) ([]string, error) {
	var frames []string

	// Read all files from the directory
	files, err := ioutil.ReadDir(directory)
	if err != nil {
		return nil, err
	}

	// Loop through each file and check if it's a JPEG file
	for _, file := range files {
		// Check if the file has a .jpg or .jpeg extension
		ext := filepath.Ext(file.Name())
		if ext == ".jpg" || ext == ".jpeg" {
			// append file content
			// Read the file into a string
			content, err := readFileToString(filepath.Join(directory, file.Name()))
			if err != nil {
				log.Fatal(err)
			}
			frames = append(frames, content)
		}
	}

	return frames, nil
}

func main() {
	addr := ":8095"
	channel := "camera0"

	// Create broadcast group to send the frames to all clients' server routines
	bcast = NewBroadcast()

	// Start goroutines for Kafka consumer
	wg.Add(1)
	go consumeFromKafka(channel)

	// Start the server handler
	server := &http.Server{Addr: addr}
	http.HandleFunc("/"+channel, ServeMJPEG)
	// Get the host and port
	fmt.Printf("Server started at %s/%s\n", addr, channel)
	// Serve
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("HTTP server ListenAndServe: %v", err)
	}

	wg.Wait()
}

// ServerHTTP will use the camera in Mjpeg server it over the response.
// Sets all the appropriate headers to be able to stream a Mjpeg over http.
func ServeMJPEG(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Client connected")

	instanceID, instanceChan := bcast.NewListener()
	defer bcast.LeaveGroup(instanceID)

	mimeWriter := multipart.NewWriter(w)
	defer mimeWriter.Close()
	contentType := fmt.Sprintf("multipart/x-mixed-replace;boundary=%s", mimeWriter.Boundary())
	w.Header().Add("Content-Type", contentType)
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")

	// Implementing CloseNotifier to check if client disconnected
	closeNotifier := w.(http.CloseNotifier).CloseNotify()

	for {
		select {
		case img := <-instanceChan:
			partHeader := make(textproto.MIMEHeader)
			partHeader.Add("Content-Type", "image/jpeg")

			partWriter, err := mimeWriter.CreatePart(partHeader)
			if err != nil {
				log.Printf("Could not create Part Writer: %v\n", err)
				break
			}

			partHeader.Add("Content-Length", strconv.Itoa(len(img)))
			if _, err = io.Copy(partWriter, bytes.NewReader(img)); err != nil {
				log.Printf("Could not write the image to the response: %v\n", err)
				break
			}
		case <-closeNotifier:
			log.Println("Client disconnected.")
			return
		default:
			time.Sleep(50 * time.Millisecond)
		}

	}
}
