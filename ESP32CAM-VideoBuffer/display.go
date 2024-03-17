package main

import (
	"fmt"
	"image"
	_ "image/jpeg"
	"image/color"
	"image/draw"
	"io"
	"mime/multipart"
	"net/http"
	"sync"
	"bytes"
	"time"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/ebitenutil"
)

var (
	screenWidth  = 640
	screenHeight = 480
)

var (
	imgFrame		*ebiten.Image
	imgFrameRW 		sync.Mutex

	dataCh   = make(chan []byte, 2)        // Channel to push multipart data
	imageCh  = make(chan *ebiten.Image, 2) // Channel to push decoded images
	wg       sync.WaitGroup

	counter int           // Counter to track the number of function calls
	rate	int
	timedout = false
)

func main() {

	imgFrame = ebiten.NewImage(screenWidth, screenHeight)
	draw.Draw(imgFrame, imgFrame.Bounds(), &image.Uniform{color.RGBA{255,0,255,255}}, image.ZP, draw.Src)

	wg.Add(1)
	go consumeData()
	go consumeImg()
	go requestStream("http://192.168.1.104:81")
	go measureRate()
	go timeOutDetect()
	

	// Initialize window
	if err := ebiten.RunGame(&Game{}); err != nil {
		panic(err)
	}
	wg.Wait()
}

type Game struct{}

func (g *Game) Update() error {
	// fmt.Println("dataCh capacity:", len(dataCh))
	// fmt.Println("imageCh capacity:", len(imageCh))
	return nil
}

func (g *Game) Draw(screen *ebiten.Image) {
	
	imgFrameRW.Lock()
	// imgFrame = <- imageCh
	screen.DrawImage(imgFrame, &ebiten.DrawImageOptions{})
	imgFrameRW.Unlock()

	ebitenutil.DebugPrint(screen, fmt.Sprintf("dataBuf: %d\nimgBuf: %d\nimgFPS: %d\nFPS: %0.2f", len(dataCh), len(imageCh), rate, ebiten.ActualFPS()))
}

func (g *Game) Layout(outsideWidth, outsideHeight int) (screenWidth, screenHeight int) {
	return 640, 480
}

func requestStream(url string) {
	defer wg.Done()

	startvideor:
	timedout = false
	fmt.Println("Requesting video")

	resp, err := http.Get(url)
	if err != nil {
		fmt.Println("Error sending request:", err)
		goto startvideor
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Println("Unexpected status code:", resp.StatusCode)
		goto startvideor
		return
	}

	// boundary := resp.Header.Get("Content-Type")
	// if boundary == "" {
	// 	fmt.Println("Content-Type header not found")
	// 	return
	// }
	boundary := "123456789000000000000987654321"

	multipartReader := multipart.NewReader(resp.Body, boundary)

	for {
		if timedout {
			goto startvideor
		}

		part, err := multipartReader.NextPart()
		if err == io.EOF {
			fmt.Println("End of stream")
			goto startvideor
		}
		if err != nil {
			fmt.Println("Error reading part:", err)
			goto startvideor
		}

		buf := new(bytes.Buffer)
		if _, err := buf.ReadFrom(part); err != nil {
			fmt.Println("Error reading part:", err)
			goto startvideor
		}
		dataCh <- buf.Bytes()
		fmt.Println("Recieved img.")
	}
}

func consumeData() {
	defer close(imageCh)
	for data := range dataCh {
		img, _, err := image.Decode(bytes.NewReader(data))
		if err != nil {
			fmt.Println("Error decoding image:", err)
			continue
		}
		ebitenImg := ebiten.NewImageFromImage(img)
		// fmt.Println("Decoded img.")
		imageCh <- ebitenImg
	}
}

func consumeImg() {
	for img := range imageCh {
		imgFrameRW.Lock()
		imgFrame = img
		// screen.DrawImage(imgFrame, &ebiten.DrawImageOptions{})
		imgFrameRW.Unlock()
		counter++
		timedout = false
	}
}

func measureRate() {
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

func timeOutDetect() {
	for {
		if rate == 0 {
		select {
		case <-time.After(10*time.Second):
			if rate == 0 {
				fmt.Println("Timed out")
				timedout = true
			}
		}
	}
	}
}