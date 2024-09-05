package main

import (
	"context"
	"errors"
	"fmt"
	"log"

	// Import the Genkit core libraries.
	"github.com/firebase/genkit/go/ai"
	"github.com/firebase/genkit/go/genkit"

	// Import the Google Cloud Vertex AI plugin.
	"github.com/firebase/genkit/go/plugins/vertexai"
)

func main() {

	GCLOUD_PROJECT := "Your-Google-Cloud-Project-ID"
	GCLOUD_LOCATION := "us-central1"

	ctx := context.Background()

	// Initialize the Vertex AI plugin. When you pass an empty string for the
	// projectID parameter, the Vertex AI plugin will use the value from the
	// GCLOUD_PROJECT environment variable. When you pass an empty string for
	// the location parameter, the plugin uses the default value, us-central1.

	if err := vertexai.Init(ctx, &vertexai.Config{ProjectID: GCLOUD_PROJECT, Location: GCLOUD_LOCATION}); err != nil {
		log.Fatal(err)
	}

	genkit.DefineFlow("callGemini15Flash", callModel("gemini-1.5-flash"))
	genkit.DefineFlow("callGemini15Pro", callModel("gemini-1.5-pro"))

	// Initialize Genkit and start a flow server. This call must come last,
	// after all of your plug-in configuration and flow definitions. When you
	// pass a nil configuration to Init, Genkit starts a local flow server,
	// which you can interact with using the developer UI.

	//The line below is good enough to deploy to Cloud Run from source.
	if err := genkit.Init(ctx, &genkit.Options{FlowAddr: ":3400"}); err != nil {
		//To start a local server, uncomment the line below and comment the one above
		//if err := genkit.Init(ctx, nil); err != nil {
		log.Fatal(err)
	}
}

func callModel(modelName string) func(ctx context.Context, prompt string) (string, error) {
	return func(ctx context.Context, prompt string) (string, error) {
		// The Vertex AI API provides access to several generative models. Here,
		// we specify gemini-1.5-flash.
		m := vertexai.Model(modelName)
		if m == nil {
			return "", errors.New("callGemini15Flash: failed to find model")
		}

		resp, err := ai.Generate(ctx, m,
			ai.WithTextPrompt(prompt),
			ai.WithConfig(ai.GenerationCommonConfig{Temperature: 1, MaxOutputTokens: 300}),
			ai.WithSystemPrompt("You are a helpful Travel assistant. Please assist the users with your expert Travel knowledge. Please great the user and be polite every time. Do not answer any question that is not related to travel. Politely refuse any non-travel related question or follow up."))

		if err != nil {
			return "", err
		}

		// Handle the response from the model API. In this sample, we just
		// convert it to a string, but more complicated flows might coerce the
		// response into structured output or chain the response into another
		// LLM call, etc.

		text := resp.Text()
		return text, nil
	}
}

