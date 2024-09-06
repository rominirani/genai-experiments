// Copyright 2024 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// This program can be manually tested like so:
//
// In development mode (with the environment variable GENKIT_ENV="dev"):
// Start the server listening on port 3100:
//
//	go run . &
//
// Tell it to run a flow:
//
//	curl -d '{"key":"/flow/simpleQaFlow/simpleQaFlow", "input":{"start": {"input":{"question": "What is the capital of UK?"}}}}' http://localhost:3100/api/runAction
//
// In production mode (GENKIT_ENV missing or set to "prod"):
// Start the server listening on port 3400:
//
//	go run . &
//
// Tell it to run a flow:
//
//   curl -d '{"question": "What is the capital of UK?"}' http://localhost:3400/simpleQaFlow

package main

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"strings"

	"github.com/firebase/genkit/go/ai"
	"github.com/firebase/genkit/go/genkit"
	"github.com/firebase/genkit/go/plugins/dotprompt"
	"github.com/firebase/genkit/go/plugins/localvec"
	"github.com/firebase/genkit/go/plugins/vertexai"
	"github.com/invopop/jsonschema"
)

const simpleQaPromptTemplate = `
You're a helpful agent that answers the user's common questions based on the context provided.

Here is the user's query: {{query}}

Here is the context you should use: {{context}}

Please provide the best answer you can.
`

type simpleQaInput struct {
	Question string `json:"question"`
}

type simpleQaPromptInput struct {
	Query   string `json:"query"`
	Context string `json:"context"`
}

func main() {

	GCLOUD_PROJECT := "gcp-experiments-349209"
	GCLOUD_LOCATION := "us-central1"
	ctx := context.Background()

	// Initialize the Vertex AI plugin. When you pass an empty string for the
	// projectID parameter, the Vertex AI plugin will use the value from the
	// GCLOUD_PROJECT environment variable. When you pass an empty string for
	// the location parameter, the plugin uses the default value, us-central1.

	if err := vertexai.Init(ctx, &vertexai.Config{ProjectID: GCLOUD_PROJECT, Location: GCLOUD_LOCATION}); err != nil {
		log.Fatal(err)
	}

	model := vertexai.Model("gemini-1.5-flash")

	err := localvec.Init()
	if err != nil {
		log.Fatal(err)
	}

	HotelsDataIndexer, HotelsDataRetriever, err := localvec.DefineIndexerAndRetriever(
		"hotelQA",
		localvec.Config{
			Embedder: vertexai.Embedder("text-embedding-004"),
		},
	)
	fmt.Println(HotelsDataIndexer)
	if err != nil {
		log.Fatal(err)
	}

	simpleQaPrompt, err := dotprompt.Define("simpleQaPrompt",
		simpleQaPromptTemplate,
		dotprompt.Config{
			Model:        model,
			InputSchema:  jsonschema.Reflect(simpleQaPromptInput{}),
			OutputFormat: ai.OutputFormatText,
		},
	)
	if err != nil {
		log.Fatal(err)
	}

	genkit.DefineFlow("simpleQaFlow", func(ctx context.Context, input *simpleQaInput) (string, error) {

		// Read the JSON records
		// Process each line of JSONL data
		jsonText, err := readJSONFile("hotels.json")
		if err != nil {
			return "", err
		}

		var d []*ai.Document
		scanner := bufio.NewScanner(strings.NewReader(jsonText))
		for scanner.Scan() {
			line := scanner.Text()

			// Decode the JSON line
			var hotelData map[string]interface{}
			err := json.Unmarshal([]byte(line), &hotelData)
			if err != nil {
				fmt.Println("Error decoding JSON:", err)
				continue
			}

			// Extract and print hotel details
			hotelName, ok := hotelData["hotel_name"].(string)
			if !ok {
				// Handle the case where "hotel_name" is missing or not a string
				fmt.Println("Error: hotel_name is missing or not a string")
				continue // Skip to the next JSON line
			}
			hotelAddress, ok := hotelData["hotel_address"].(string)
			if !ok {
				// Handle the case where "hotel_name" is missing or not a string
				fmt.Println("Error: hotel_name is missing or not a string")
				continue // Skip to the next JSON line
			}
			hotelDescription, ok := hotelData["hotel_description"].(string)
			if !ok {
				// Handle the case where "hotel_name" is missing or not a string
				fmt.Println("Error: hotel_name is missing or not a string")
				continue // Skip to the next JSON line
			}
			nearestAttractions, ok := hotelData["nearest_attractions"].(string)
			if !ok {
				// Handle the case where "hotel_name" is missing or not a string
				fmt.Println("Error: nearest_attractions is missing or not a string")
				continue // Skip to the next JSON line
			}
			hotelInfo := fmt.Sprintf("%s,%s,%s,%s", hotelName, hotelAddress, hotelDescription, nearestAttractions)
			d = append(d, ai.DocumentFromText(hotelInfo, nil))
		}

		if err := scanner.Err(); err != nil {
			fmt.Println("Error reading input:", err)
		}

		//d1 := ai.DocumentFromText("Paris is the capital of France", nil)
		//d2 := ai.DocumentFromText("USA is the largest importer of coffee", nil)
		//d3 := ai.DocumentFromText("Water exists in 3 states - solid, liquid and gas", nil)

		//err := ai.Index(ctx, HotelsDataIndexer, ai.WithIndexerDocs(d1, d2, d3))
		err = ai.Index(ctx, HotelsDataIndexer, ai.WithIndexerDocs(d...))
		if err != nil {
			return "", err
		}

		dRequest := ai.DocumentFromText(input.Question, nil)
		response, err := ai.Retrieve(ctx, HotelsDataRetriever, ai.WithRetrieverDoc(dRequest))
		if err != nil {
			return "", err
		}

		var sb strings.Builder
		for _, d := range response.Documents {
			sb.WriteString(d.Content[0].Text)
			sb.WriteByte('\n')
		}

		promptInput := &simpleQaPromptInput{
			Query:   input.Question,
			Context: sb.String(),
		}

		resp, err := simpleQaPrompt.Generate(ctx,
			&dotprompt.PromptRequest{
				Variables: promptInput,
			},
			nil,
		)
		if err != nil {
			return "", err
		}
		return resp.Text(), nil
	})

	if err := genkit.Init(context.Background(), nil); err != nil {
		log.Fatal(err)
	}
}

func readJSONFile(path string) (string, error) {

	// Read the entire file contents into a byte slice.
	data, err := ioutil.ReadFile(path)
	if err != nil {
		return "", err
	}

	// Convert the byte slice to a string.
	return string(data), nil

}
