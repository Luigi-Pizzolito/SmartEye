package main

import (
	"fmt"
	"os"
	"strings"
)

func getENVvar(key string) string {
	value, ok := os.LookupEnv(key)
	if !ok {
		fmt.Printf("Critical error: ENV %s not found.", key)
		panic("ENVS NOT FOUND")
	}
	fmt.Printf("Got ENV %s=%s\n", key, value)
	return value
}

func getENVproperty(obj, prop string) string {
	lookup := strings.ToUpper(obj) + "_" + strings.ToUpper(prop)
	return getENVvar(lookup)
}

func getENVlist(key string) []string {
	vals := getENVvar(key)
	return strings.Split(vals, ",")
}
