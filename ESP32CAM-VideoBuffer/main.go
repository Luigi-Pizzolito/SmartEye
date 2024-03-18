package main

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
	producer *KafkaProducer
	topic    string

	dataCh = make(chan []byte, 2) // Channel to push multipart data
	wg     sync.WaitGroup

	counter int // Counter to track the number of function calls
	rate    int
)

func main() {
	// Kafka brokers
	brokers := []string{"kafka:9092"}
	topic = "camera0"

	log.Println("Starting ESPcam Buffer for " + topic)
	// Create a new KafkaProducer instance
	var err error
	producer, err = NewKafkaProducer(brokers)
	if err != nil {
		log.Fatalf("Error creating Kafka producer: %v", err)
	}
	defer producer.Close()
	log.Println("Connected to Kafka")

	go consumeData()
	go requestStream("http://192.168.1.104:81")
	go measureRate()
	go timeOutDetect()

	wg.Wait()
}

func requestStream(url string) {
	wg.Add(1)
	defer wg.Done()

startvideor:
	log.Println("Requesting video from " + url)

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

	// boundary := resp.Header.Get("Content-Type")
	// if boundary == "" {
	// 	log.Println("Content-Type header not found")
	// 	return
	// }
	boundary := "123456789000000000000987654321"

	multipartReader := multipart.NewReader(resp.Body, boundary)

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
		dataCh <- buf.Bytes()
		log.Println("Recieved img.")
	}
}

func consumeData() {
	wg.Add(1)
	defer wg.Done()
	defer close(dataCh)
	for data := range dataCh {
		//? No need to decode when sending jpeg data to Kafka
		/*
			img, _, err := image.Decode(bytes.NewReader(data))
			if err != nil {
				log.Println("Error decoding image:", err)
				continue
			}
			ebitenImg := ebiten.NewImageFromImage(img)
			// log.Println("Decoded img.")
			imageCh <- ebitenImg
		*/
		// Update frame rate counter
		counter++

		// Send to Kafka
		producer.SendMessage(topic, data)
		log.Println("Message sent asynchronously to Kafka topic:", topic)
	}
}

func measureRate() {
	wg.Add(1)
	defer wg.Done()
	var prevCounter int // Counter value at the previous measurement

	for {
		select {
		case <-time.After(time.Second):
			currentCounter := counter
			rate = currentCounter - prevCounter
			prevCounter = currentCounter
		case <-time.After(5 * time.Second):
			fmt.Printf("Framerate: %d\n", rate)
		}
	}
}

func timeOutDetect() {
	wg.Add(1)
	defer wg.Done()
	for {
		if rate == 0 {
			select {
			case <-time.After(10 * time.Second):
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
