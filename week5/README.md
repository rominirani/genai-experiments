# rag-genkit-go-app

This is a simple question-answering application built with Genkit and Vertex AI. It allows users to ask questions about hotels based on a JSON dataset.

## Features

* Uses Vertex AI's Gemini Flash model for text generation.
* Employs local vector indexing and retrieval for efficient document search.
* Provides a simple REST API for querying the application.

## Requirements

* Go 1.18 or higher
* Google Cloud Project with Vertex AI API enabled
* Service account with permissions to access Vertex AI and Cloud Storage

## Data
The application uses a JSON file named hotels.json to store hotel data. Each line in the file represents a hotel record in JSON format.

This Go program is a simple question-answering application that leverages the power of Genkit and Vertex AI. It allows users to ask questions about hotels, and the application retrieves relevant information from a JSON dataset (`hotels.json`) to provide comprehensive answers.

## Code breakdown

**1. Initialization and Setup:**

- The program starts by initializing the Vertex AI plugin, setting up the project ID and location.
- It defines a prompt template (`simpleQaPromptTemplate`) that structures the interaction with the language model, providing context and a user query.

**2. Data Loading and Indexing:**

- The `readJSONFile` function reads hotel data from the `hotels.json` file.
- The data is then indexed using the `localvec` plugin, which enables efficient vector-based search for relevant information.

**3. Question Answering Flow:**

- The core logic resides in the `genkit.DefineFlow` function, which defines a flow named "simpleQaFlow."
- When a user submits a question, the flow retrieves relevant hotel information from the indexed data.
- It then constructs a prompt using the `simpleQaPromptTemplate`, incorporating the user's question and the retrieved context.
- The prompt is sent to the Vertex AI language model (Gemini Pro) for generating a comprehensive answer.

**4. Response Generation:**

- The language model's response is returned to the user as a text output.

**Key Features:**

- **Vertex AI Integration:** Leverages Vertex AI's Gemini Pro model for advanced text generation and question answering.
- **Local Vector Indexing:** Employs local vector indexing for efficient retrieval of relevant information from the hotel dataset.
- **Structured Prompting:** Uses a well-defined prompt template to guide the language model in generating accurate and contextually relevant answers.

Overall, this program demonstrates a practical application of Genkit and Vertex AI for building a simple yet powerful question-answering system.
