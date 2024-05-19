package main

/* ********************************************************************
   * Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
/* ********************************************************************/

// Utility class to calculate the current FPS of every incoming livestream

import (
	"sync"
	"time"
)

// FPS counter struct, single FPS counter
type FPSCounter struct {
	counter int
	prev    int
	rate    int
}

// Multi FPS counter struct, multiple FPS counter manager
type MultiFPSCounter struct {
	fpsc map[string]*FPSCounter
	mu   sync.Mutex
}

// Instantiation
func NewMultiFPSCounter() *MultiFPSCounter {
	fpscounters := make(map[string]*FPSCounter)
	return &MultiFPSCounter{fpsc: fpscounters}
}

// Update FPS for each FPS counter every second
func (c *MultiFPSCounter) tick() {
	defer wg.Done()
	for {
		select {
		case <-time.After(time.Second):
			// every second
			for key, _ := range c.fpsc {
				// for each FPS counter, update the fps
				c.mu.Lock()
				c.fpsc[key].rate = c.fpsc[key].counter - c.fpsc[key].prev
				c.fpsc[key].prev = c.fpsc[key].counter
				c.mu.Unlock()
			}
		}
	}
}

// Register a frame for a FPS counter
func (c *MultiFPSCounter) frame(id string) {
	c.mu.Lock()
	// Check if counter for id exists
	_, exists := c.fpsc[id]
	if !exists {
		// if it doesn't exists, instantiate it
		c.fpsc[id] = &FPSCounter{
			counter: 0,
			prev:    0,
			rate:    0,
		}
	}
	// increase frame counter for this second
	c.fpsc[id].counter++
	c.mu.Unlock()
}

// Read the current FPS of a FPS counter
func (c *MultiFPSCounter) fps(id string) int {
	c.mu.Lock()
	rate := c.fpsc[id].rate
	c.mu.Unlock()
	return rate
}

// Read the current FPS of all FPS counters
func (c *MultiFPSCounter) fpsAll() map[string]int {
	c.mu.Lock()
	rates := make(map[string]int)
	if len(c.fpsc) > 0 && c.fpsc != nil {
		for key, counter := range c.fpsc {
			rates[key] = counter.rate
		}
	}
	c.mu.Unlock()
	return rates
}
