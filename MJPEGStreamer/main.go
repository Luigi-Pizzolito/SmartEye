package main

/* ********************************************************************
   * Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
/* ********************************************************************/

// Main program for MJPEGStreamer
// reads JPEG frames from Kafka topics specified to contain MJPEG streams
// and serves HTTP MJPEG streams to many web clients, for many cameras
// also keeps track of each streams FPS and lists streams.

// Endpoints:
//  - /<Kafka_topic_name>.mjpeg
//     - MJPEG stream of that respective Kafka stream
//  - /list
//     - JSON object containing a list of current streams and their FPS
//        - e.g. {"Streams":["camera0"],"FPS":{"camera0":0}}

// Data flow:
// Kafka topic: camera0 -|					     |--> camera0 stream endpoint: Client 0
// Kafka topic: camera1 -|					     |--> camera0 stream endpoint: Client 1
// Kafka topic: camera2 -|--> MJPEG Streamer --> |--> camera1 stream endpoint: Client 0
// Kafka topic: camera3 -|					     |--> cameraX stream endpoint: Client X
// Kafka topic: cameraX -|					     |--> /list endpoint:		   Client X\

// Configuration environment variables:
//  -
//TODO: fill in this config doc

//TODO: read opts from ENV
//? TODO: update streams if a new camera is detected?
//TODO: use a propper logging library

import (
	"fmt"
	"log"

	"encoding/json"
	"net/http"
	"sync"

	//! profiler deps
	_ "net/http/pprof"

	"github.com/felixge/fgprof"
)

var (
	// List of Kafka topics containing valid MJPEG streams to distribute
	streamChannels []string
	// Map of broadcast groups, used to send the JPEG frames to each handler serving the stream to each connected client
	bcastMap map[string]*broadcast
	// Multiple FPS counter manager, for counting the FPS of each stream
	fpsman *MultiFPSCounter
	// Waitgroup for async goroutines
	wg sync.WaitGroup
)

func main() {
	//! profiler insert
	http.DefaultServeMux.Handle("/debug/fgprof", fgprof.Handler())
	go func() {
		log.Println(http.ListenAndServe(":6060", nil))
	}()
	// params
	addr := ":8095"
	kafkaBrokers := []string{"kafka:9092"}
	//? any kafka topic containing these substrings is processed as a JPEG stream
	frameStreams := []string{"stream"}

	// connect to Kafka brokers
	kafkaCon := NewKafkaMultiStreamReader(kafkaBrokers, frameStreams)

	// get channels from Kafka
	streamChannels = kafkaCon.getFrameTopicsList()
	fmt.Println("Found frame topics: ", streamChannels)

	// setup FPS counters
	fpsman = NewMultiFPSCounter()
	wg.Add(1)
	go fpsman.tick() // Update FPS counters asynchronously

	// create broadcast group map
	bcastMap = make(map[string]*broadcast)

	// Setup HTTP server mux to handle multiple endpoints/streams
	mux := http.NewServeMux()

	for _, channel := range streamChannels {
		// for each channel, asynchronously setup the server backend
		go func() {
			// Create broadcast group to send the frames to all clients' server routines
			channelName := "/" + channel + ".mjpeg"
			bcastMap[channelName] = NewBroadcastGroup()

			// Start FPS counter
			fpsman.frame(channel)

			// Start goroutines for Kafka consumer
			wg.Add(1)
			go kafkaCon.consumeTopicFrames(channel, bcastMap[channelName])

			// Start the server handler
			mux.HandleFunc("/"+channel+".mjpeg", ServeMJPEG)
			// Print the host and port
			fmt.Printf("Handling endpoint at %s/%s.mjpeg\n", addr, channel)
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

// HTTP JSON response handler for stream and fps listing
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
