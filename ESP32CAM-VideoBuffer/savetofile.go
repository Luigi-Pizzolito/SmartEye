package main

import (
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
)

func main() {
	startrecv:
	url := "http://192.168.1.104:81/"

	client := &http.Client{}

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		fmt.Println("Error creating request:", err)
		goto startrecv
		return
	}

	req.Header.Set("Connection", "keep-alive")

	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Error sending request:", err)
		goto startrecv
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Println("Unexpected status code:", resp.StatusCode)
		goto startrecv
		return
	}

	boundary := "123456789000000000000987654321"
	multipartReader := multipart.NewReader(resp.Body, boundary)

	frameCount := 0 // Variable to keep track of frame count

	for {
		part, err := multipartReader.NextPart()
		if err == io.EOF {
			fmt.Println("End of stream")
			goto startrecv
			break
		}
		if err != nil {
			fmt.Println("Error reading part:", err)
			goto startrecv
			continue
		}

		// Assuming each part is an image frame
		frameCount++
		fileName := fmt.Sprintf("img/frame%d.jpg", frameCount)
		frameFile, err := os.Create(fileName)
		if err != nil {
			fmt.Println("Error creating file:", err)
			continue
		}

		_, err = io.Copy(frameFile, part)
		if err != nil {
			fmt.Println("Error writing frame to file:", err)
		}

		frameFile.Close()
		fmt.Println("Saved frame:", fileName)
	}
}
