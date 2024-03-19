package main

//TODO: read from Kafka topic
//TODO: read multiple topics and handle multiple streams
//TODO: read opts from ENV

import (
	"fmt"
	"log"

	"encoding/json"
	"net/http"
	"sync"
)

var (
	streamChannels []string

	bcastMap map[string]*broadcast

	fpsman *MultiFPSCounter

	wg sync.WaitGroup
)

func main() {
	// params
	addr := ":8095"
	kafkaBrokers := []string{"kafka:9092"}
	//? any kafka topic containing these substrings is processed as a JPEG stream
	frameStreams := []string{"camera"}

	// connect to Kafka brokers
	kafkaCon := NewKafkaMultiStreamReader(kafkaBrokers, frameStreams)

	// get channels from Kafka
	streamChannels = kafkaCon.getFrameTopicsList()
	fmt.Println("Found frame topics: ", streamChannels)

	// setup FPS counters
	fpsman = NewMultiFPSCounter()
	wg.Add(1)
	go fpsman.tick()

	// create broadcast group map
	bcastMap = make(map[string]*broadcast)

	// Setup HTTP server mux to handle multiple endpoints/streams
	mux := http.NewServeMux()

	for _, channel := range streamChannels {
		// for each channel, asynchronously setup the server backend
		go func() {
			// Create broadcast group to send the frames to all clients' server routines
			channelName := "/" + channel
			bcastMap[channelName] = NewBroadcast()

			// Start FPS counter
			fpsman.frame(channel)

			// Start goroutines for Kafka consumer
			wg.Add(1)
			go kafkaCon.consumeTopicFrames(channel, bcastMap[channelName])

			// Start the server handler
			mux.HandleFunc("/"+channel, ServeMJPEG)
			// Get the host and port
			fmt.Printf("Handling endpoint at %s/%s\n", addr, channel)
		}()
	}

	// Setup stream listing JSON endpoint
	mux.HandleFunc("/list", listStreams)

	// Serve
	server := &http.Server{Addr: addr, Handler: mux}
	fmt.Println("Server started")
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("HTTP server ListenAndServe: %v", err)
	}

	wg.Wait()
}

func listStreams(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("Client %s requested stream list\n", r.RemoteAddr)

	// Create an object with the streams slice
	streamInfo := struct {
		Streams []string
		FPS     map[string]int
	}{
		Streams: streamChannels,
		FPS:     fpsman.fpsAll(),
	}

	// Marshal the slice into JSON format
	jsonData, err := json.Marshal(streamInfo)
	if err != nil {
		http.Error(w, "Failed to marshal data", http.StatusInternalServerError)
		return
	}

	// Set content type header
	w.Header().Set("Content-Type", "application/json")

	// Write JSON response
	_, err = w.Write(jsonData)
	if err != nil {
		http.Error(w, "Failed to write response", http.StatusInternalServerError)
		return
	}
}
