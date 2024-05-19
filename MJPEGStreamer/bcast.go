package main

/* ********************************************************************
   * Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
/* ********************************************************************/

// Broadcast class to allow broadcasting []byte from one goroutine
// to many other goroutines in a brodcast group
// Used for sharing the livestream frames from the Kafka consumer
// to each instance(goroutine) handling each client connection

import "sync"

// Broadcast struct
type Broadcast struct {
	listeners map[int]chan []byte
	mu        sync.Mutex
}

// NewBroadcast creates a new broadcast instance (broadcast group)
func NewBroadcastGroup() *Broadcast {
	return &Broadcast{
		listeners: make(map[int]chan []byte),
	}
}

// NewListener creates a new listener and returns its channel and member ID
func (b *Broadcast) NewListener() (int, chan []byte) {
	listener := make(chan []byte)
	memberID := len(b.listeners) + 1
	b.mu.Lock()
	b.listeners[memberID] = listener
	b.mu.Unlock()
	return memberID, listener
}

// LeaveGroup closes the channel and removes it from the array
func (b *Broadcast) LeaveGroup(memberID int) {
	b.mu.Lock()
	if listener, ok := b.listeners[memberID]; ok {
		close(listener)
		delete(b.listeners, memberID)
	}
	b.mu.Unlock()
}

// SendMessage sends a message to all listener channels
func (b *Broadcast) SendMessage(message []byte) {
	b.mu.Lock()
	for _, listener := range b.listeners {
		listener <- message
	}
	b.mu.Unlock()
}
