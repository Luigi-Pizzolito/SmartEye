package main

/* ********************************************************************
   * Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
/* ********************************************************************/

// Broadcast class to allow broadcasting []byte from one goroutine
// to many other goroutines in a brodcast group
// Used for sharing the livestream frames from the Kafka consumer
// to each instance(goroutine) handling each client connection

// broadcast struct
type broadcast struct {
	listeners map[int]chan []byte
}

// NewBroadcast creates a new broadcast instance (broadcast group)
func NewBroadcastGroup() *broadcast {
	return &broadcast{
		listeners: make(map[int]chan []byte),
	}
}

// NewListener creates a new listener and returns its channel and member ID
func (b *broadcast) NewListener() (int, chan []byte) {
	listener := make(chan []byte)
	memberID := len(b.listeners) + 1
	b.listeners[memberID] = listener
	return memberID, listener
}

// LeaveGroup closes the channel and removes it from the array
func (b *broadcast) LeaveGroup(memberID int) {
	if listener, ok := b.listeners[memberID]; ok {
		close(listener)
		delete(b.listeners, memberID)
	}
}

// SendMessage sends a message to all listener channels
func (b *broadcast) SendMessage(message []byte) {
	for _, listener := range b.listeners {
		listener <- message
	}
}
