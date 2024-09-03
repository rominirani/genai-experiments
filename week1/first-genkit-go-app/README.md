## Getting started with [Genkit Go framework](https://firebase.google.com/docs/genkit-go/get-started-go)

1. The application was generated using the standard `genkit init` command.
2. Created two flows in the application: `callGemini15Flash` and `callGemini15Pro`.
3. The idea is to invoke any of these flows when needed.
4. You can deploy the same on Cloud Run via the instructions given [here](https://firebase.google.com/docs/genkit-go/cloud-run).

## Invoking the flows
`
1. $ curl -X POST <CLOUD_RUN_APP_BASE_URL>/callGemini15Pro -H "Content-Type: application/json" -d '{"data":"who are you?"}'
`
`
2. $ curl -X POST <CLOUD_RUN_APP_BASE_URL>/callGemini15Flash -H "Content-Type: application/json" -d '{"data":"who are you?"}'
`
