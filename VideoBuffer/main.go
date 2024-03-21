package main

/* ********************************************************************
   * Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
/* ********************************************************************/

// Main program for ESP32CAM Video Buffer
// reads JPEG frames from ESP32CAM HTTP servers (running on ESP32)
// and pushes frames to Kafka topics

// Data flow:
// espcam0 -|										 |--> camera0 topic
// espcam1 -|										 |--> camera1 topic
// espcam2 -|--> ESP32CAM Video Buffer --> Kafka --> |--> camera2 topic
// espcam3 -|										 |--> camera3 topic
// espcamX -|										 |--> cameraX topic

// Configuration environment variables:
//  - CAMERA =camera name in all lowercase
//  - CAMERANAME_TYPE =espcam or usbcam
//  - CAMERANAME_IP =http://<ip>:<port>
//  - CAMERANAME_DEVICE =/dev/<device_name>

//TODO: more descriptive FPS print: topic/camera, timestamp
//TODO: WIP - read opts from ENV
//TODO: use a propper logging library
//TODO: clean error exit instead of panic()

import (
	"fmt"
	"log"

	"bytes"
	"io"
	"sync"
	"time"

	"mime/multipart"
	"net/http"
)

var (
	// Variables to store Kafka Producer
	producer *KafkaProducer
	topic    string
	// Data channel & async wait group for reading topic data
	dataCh = make(chan []byte, 2) // Channel to push multipart data
	wg     sync.WaitGroup
	// Variables for FPS counter
	counter int // Counter to track the number of function calls
	rate    int
)

func main() {
	// Configuration from ENV variables
	//TODO: accept usbcam
	// -- Kafka brokers
	brokers := []string{"kafka:9092"}
	topic = getENVvar("CAMERA")
	// -- ESP32CAM Address
	webjpegcam := getENVvar("IP")

	log.Println("Starting ESPcam Buffer for " + topic)
	// Create a new KafkaProducer instance
	var err error
	producer, err = NewKafkaProducer(brokers)
	if err != nil {
		log.Fatalf("Error creating Kafka producer: %v", err)
	}
	defer producer.Close()
	log.Println("Connected to Kafka")

	// Start running concurrent goroutines for each task
	wg.Add(5)

	go consumeData()
	go requestStream(webjpegcam)
	go measureRate()
	go timeOutDetect()
	go printFrameRate()

	wg.Wait()
}

// Request MJPEG stream from ESP32CAM
func requestStream(url string) {
	defer wg.Done()

startvideor:
	log.Println("Requesting video from " + url)

	// Send HTTP GET request
	resp, err := http.Get(url)
	if err != nil {
		log.Println("Error sending request:", err)
		goto startvideor
		// return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		log.Println("Unexpected status code:", resp.StatusCode)
		goto startvideor
		// return
	}

	// Start a new multipart reader to read each frame of the MJPEG stream

	// Get the inter-frame boundary segment
	// boundary := resp.Header.Get("Content-Type")
	// if boundary == "" {
	// 	log.Println("Content-Type header not found")
	// 	return
	// }
	//? frame boundary as defined in ESP32CAM-Firmware
	boundary := "123456789000000000000987654321"

	multipartReader := multipart.NewReader(resp.Body, boundary)

	// Iterate over recieved frames and parse the recieved parts
	for {
		part, err := multipartReader.NextPart()
		if err == io.EOF {
			log.Println("End of stream")
			goto startvideor
		}
		if err != nil {
			log.Println("Error reading part:", err)
			goto startvideor
		}

		buf := new(bytes.Buffer)
		if _, err := buf.ReadFrom(part); err != nil {
			log.Println("Error reading part:", err)
			goto startvideor
		}
		// Send frame JPEG data to data channel
		dataCh <- buf.Bytes()
		// log.Println("Recieved img.")
	}
}

// Consume JPEG frames from data channel and send them as messages to the Kafka topic
func consumeData() {
	defer wg.Done()
	defer close(dataCh)
	for data := range dataCh {
		// Update frame rate counter
		counter++

		// Send to Kafka
		producer.SendMessage(topic, data)
		// log.Println("Message sent asynchronously to Kafka topic:", topic)
	}
}

// FPS counter update
func measureRate() {
	defer wg.Done()
	var prevCounter int // Counter value at the previous measurement

	for {
		select {
		case <-time.After(time.Second):
			currentCounter := counter
			rate = currentCounter - prevCounter
			prevCounter = currentCounter
		}
	}
}

// Print FPS
func printFrameRate() {
	defer wg.Done()
	for {
		select {
		case <-time.After(5 * time.Second):
			// Print frame rate
			fmt.Printf("Framerate: %d\n", rate)
		}
	}
}

// Detect timeouts if we get 0FPS for 30s, if timedout, exit and restart the program
func timeOutDetect() {
	defer wg.Done()
	for {
		// Detect timeout
		if rate == 0 {
			select {
			case <-time.After(30 * time.Second):
				if rate == 0 {
					log.Println("Timed out")
					time.Sleep(2 * time.Second)
					panic("Timed out")
					//! just panic here and exit the program
					//! Docker daemon will automatically restart the program
				}
			}
		}
	}
}
