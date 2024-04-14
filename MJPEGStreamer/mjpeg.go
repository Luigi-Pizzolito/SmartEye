package main

/* ******************************************************************
* Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
/* *****************************************************************/

// Method for serving MJPEG streams over HTTP
// each connected client spawns a new instance of this handler function
// therefor, each handler function must recieve another copy of the original
// stream via broadcast group; in order to support many clients simultaneously

import (
	"bytes"
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"net/textproto"
	"strconv"
)

// ServerHTTP will use the camera in Mjpeg server it over the response.
// Sets all the appropriate headers to be able to stream a Mjpeg over http.
func ServeMJPEG(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("Client %s connected to %s\n", r.RemoteAddr, r.URL.String())

	// Start a new broadcast group listener
	instanceID, instanceChan := bcastMap[r.URL.Path].NewListener()
	defer bcastMap[r.URL.Path].LeaveGroup(instanceID)

	// Start a multipart reader
	mimeWriter := multipart.NewWriter(w)
	defer mimeWriter.Close()
	contentType := fmt.Sprintf("multipart/x-mixed-replace;boundary=%s", mimeWriter.Boundary())
	w.Header().Add("Content-Type", contentType)
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")

	// Implementing CloseNotifier to check if client disconnected
	closeNotifier := w.(http.CloseNotifier).CloseNotify()

	// Event processing loop
	for {
		select {
		case img := <-instanceChan:
			// frame recieved, create a new part
			partHeader := make(textproto.MIMEHeader)
			partHeader.Add("Content-Type", "image/jpeg")

			partWriter, err := mimeWriter.CreatePart(partHeader)
			if err != nil {
				log.Printf("Could not create Part Writer: %v\n", err)
				break
			}

			// Write part to client
			partHeader.Add("Content-Length", strconv.Itoa(len(img)))
			if _, err = io.Copy(partWriter, bytes.NewReader(img)); err != nil {
				log.Printf("Could not write the image to the response: %v\n", err)
				break
			}
		case <-closeNotifier:
			// Client disconnected
			fmt.Printf("Client %s disconnected to %s\n", r.RemoteAddr, r.URL.String())
			bcastMap[r.URL.Path].LeaveGroup(instanceID)
			return
		default:
			// If no frames were recieved, wait a little
			// time.Sleep(50 * time.Millisecond)
		}

	}
}
