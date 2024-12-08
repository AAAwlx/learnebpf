package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"regexp"
	"strings"
)

type TCPHeader struct {
	SourcePort          int    `json:"source_port"`
	DestinationPort     int    `json:"destination_port"`
	SequenceNumber      uint32 `json:"sequence_number"`
	AcknowledgmentNumber uint32 `json:"ack_number"`
	DataOffset          int    `json:"data_offset"`
	Flags               string `json:"flags"`
	WindowSize          int    `json:"window_size"`
}

func parseTCPHeader(line string) *TCPHeader {
	r := regexp.MustCompile(`Source Port: (\d+).*Destination Port: (\d+).*Sequence Number: (\d+).*Acknowledgment Number: (\d+).*Data Offset: (\d+).*Flags: (0x[0-9a-fA-F]+).*Window Size: (\d+)`)
	matches := r.FindStringSubmatch(line)
	if matches == nil {
		return nil
	}
	header := &TCPHeader{}
	fmt.Sscanf(matches[1], "%d", &header.SourcePort)
	fmt.Sscanf(matches[2], "%d", &header.DestinationPort)
	fmt.Sscanf(matches[3], "%d", &header.SequenceNumber)
	fmt.Sscanf(matches[4], "%d", &header.AcknowledgmentNumber)
	fmt.Sscanf(matches[5], "%d", &header.DataOffset)
	header.Flags = matches[6]
	fmt.Sscanf(matches[7], "%d", &header.WindowSize)
	return header
}

func loadTCPHeaders(filename string) ([]TCPHeader, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var headers []TCPHeader
	scanner := bufio.NewScanner(file)
	var lineBuffer strings.Builder

	for scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, "Captured TCP Header:") {
			if lineBuffer.Len() > 0 {
				header := parseTCPHeader(lineBuffer.String())
				if header != nil {
					headers = append(headers, *header)
				}
				lineBuffer.Reset()
			}
		}
		lineBuffer.WriteString(line + " ")
	}

	// Parse the last header if any
	if lineBuffer.Len() > 0 {
		header := parseTCPHeader(lineBuffer.String())
		if header != nil {
			headers = append(headers, *header)
		}
	}

	return headers, nil
}

func handler(w http.ResponseWriter, r *http.Request) {
	headers, err := loadTCPHeaders("tcp_data.txt")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(headers)
}

func main() {
	http.HandleFunc("/tcp_headers", handler)
	fmt.Println("Server running on http://localhost:8080")
	http.ListenAndServe(":8080", nil)
}
