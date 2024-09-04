package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"strings"
)

// Your AI/LLM logic or API calls would go here
func getResponseFromPrompt(prompt string) (string, error) {
	url := "https://week1-ido3ocn3pq-uc.a.run.app/callGemini15Flash" // Replace with the actual URL

	// Create the JSON data
	jsonData := map[string]string{"data": prompt}
	jsonValue, _ := json.Marshal(jsonData)

	// Make the POST request
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonValue))
	if err != nil {
		return "", fmt.Errorf("error making POST request: %v", err)
	}
	defer resp.Body.Close()

	// Read the response body
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("error reading response body: %v", err)

	}

	// Trim the response and return the JSON
	trimmedResponse := strings.TrimSpace(string(body))
	fmt.Println(trimmedResponse)

	// Remove the trailinig /n from this trimmedResponse
	trimmedResponse = strings.TrimSuffix(trimmedResponse, "\\n")
	fmt.Println(trimmedResponse)

	//Parse out the result from this JSON and return only the result
	var response map[string]interface{}
	err = json.Unmarshal([]byte(trimmedResponse), &response)
	if err != nil {
		return "", fmt.Errorf("error unmarshaling JSON: %v", err)
	}

	// Extract the result from the JSON
	result, ok := response["result"].(string)
	if !ok {
		return "", fmt.Errorf("result not found in JSON response")
	}

	// Return the result
	trimmedResponse = strings.TrimSpace(result)

	return trimmedResponse, nil
}

func ChatHandler(w http.ResponseWriter, r *http.Request) {
	// Parse the prompt from the request body
	err := r.ParseForm()
	if err != nil {
		http.Error(w, "Error parsing form data", http.StatusBadRequest)
		return
	}

	// Print all received form values
	prompt := r.FormValue("prompt")
	if strings.TrimSpace(prompt) == "" {
		http.Error(w, "Prompt is required", http.StatusBadRequest)
	}

	log.Printf("Received prompt: %s", prompt)
	response, err := getResponseFromPrompt(prompt)
	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	jsonResponse, _ := json.Marshal(map[string]string{"response": response})
	w.Header().Set("Content-Type", "application/json")
	w.Write(jsonResponse)
}
