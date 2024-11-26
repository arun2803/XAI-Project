# XAI-Project

## Creating and querying a model for XAI on Google Cloud

### Data preparation
The code begins by loading the data from Google Drive and splitting it into smaller chunks. 

 

This Python code processes documents from a Google Drive folder, splits the text into manageable chunks, and generates embeddings for each chunk using Google’s Vertex AI Embeddings.

1.	Imports and Configuration: It imports necessary modules from “langchain” and sets constants for Google Drive credentials and the Vertex AI model configuration (“textembedding-gecko@003”).

2.	Embedding Model: “VertexAIEmbeddings” is initialized with the specified model. This model generates embeddings, which are numerical representations of text that can be used for natural language processing tasks.

3.	Document Loading (“load_documents” function): This function uses “GoogleDriveLoader” to load documents from a specified Google Drive folder. It retrieves documents recursively, using the provided credentials and token files.

4.	Document Splitting (“generate_chunks” function): Based on the document’s title or content, the function splits text into smaller parts

5.3.2 Generating Embeddings
Embeddings are created for the chunked text data using the Vertex AI Embeddings API. 

 

This code processes documents from Google Drive by breaking them into smaller sections, generating unique data representations (embeddings) for each section, and organizing them for easy storage and retrieval.
1.	Loading and Chunking Documents: It retrieves documents from Google Drive, then breaks each document into sections, storing them in a list of organized text chunks.
2.	Creating Embeddings: Each text chunk is transformed into a meaningful data format (embedding) using the Vertex AI Embeddings API, which allows the system to interpret the content.
3.	Indexing and Storing Embeddings:
o	Each text chunk is labelled with a unique identifier for easy reference.
o	The identifiers and embeddings are saved in JSON format, making it efficient to look up each chunk by its unique ID.
o	This setup enables a structured format for storing and accessing similar text chunks quickly, supporting tasks like search and recommendation based on content meaning.


### Creating the index
The embeddings are uploaded to a GCS bucket, and an index is created to point to this bucket. 

 

This code uploads text data (converted to embeddings) to Google Cloud Storage, then creates an index for these embeddings using Google’s Vertex AI Matching Engine. This index allows the system to quickly find and match similar text across large volumes of documents. By storing the data in a structured way, it enables efficient searching, recommendation, or comparison of document content based on meaning rather than keywords. This setup is useful for systems needing fast access to related or similar text in a collection, such as document recommendation or retrieval services.



### Deploying the index
The newly created index is deployed to the index endpoint, and the old index is undeployed. 

 
This code is responsible for two main tasks: uploading chunks of data to BigQuery and updating an index endpoint for Vertex AI.
1.	Uploading Chunks to BigQuery (upload_chunks_to_bigquery function):
o	This function uploads data chunks from a list of DataFrames (dfs) to a BigQuery table.
o	It first adds an index name to each DataFrame and then uses the BigQuery client to load the data into the specified table.
o	The BIG_QUERY_TABLE_SCHEMA defines the table structure, ensuring the data is uploaded with the correct format.
2.	Updating the Index Endpoint (update_index_endpoint function):
o	The function retrieves the current index endpoint using the aiplatform.MatchingEngineIndexEndpoint list method.
o	It deploys the new index to the endpoint and updates the deployed index by first undeploying the old one.
o	This process ensures that the system uses the most recent index for efficient querying and matching.
5.3.5 Querying the index
The code then queries the index endpoint with a question. 

 


This code is written to work with Google Cloud's Vertex AI to handle document matching and embedding generation for efficient search and retrieval.
1.	Text Embedding Generation: The code transforms text documents into numerical representations (embeddings) using a pre-trained AI model called textembedding-gecko@003. This transformation helps the system understand and compare the meaning of different pieces of text.
2.	Mapping Documents to Intents: The code maps specific documents to their intended use or category, making it easier to retrieve related documents when needed. 
3.	Generating and Retrieving Embeddings: The encode_texts_to_embeddings function converts sentences into embeddings, and the function can handle errors by returning None if something goes wrong.
4.	Index Retrieval: The functions get_index_name_by_project and get_index_endpoint_by_project are used to find the index (which helps to search for similar documents) and the endpoint (where the index is deployed) based on the project name.

### Filtering the results
The results are filtered by intent to only include those that are relevant to the question. 

 

This code is designed to process a user’s query, search for similar documents based on their intent, and retrieve relevant chunks of text from a database. Here's an overview of what it does:
1.	Vector Search for Similarity:
o	The function vector_search_query takes a user’s question and converts it into an embedding using the previously mentioned encode_texts_to_embeddings. It then searches for similar documents in a deployed index and returns the nearest neighbours (most similar documents) based on the embeddings.
2.	Filtering Results by Intent:
o	The function filter_chunks_by_intent filters the search results based on the intended use of the document. It compares the document IDs to a predefined mapping (intent_and_docs_matching) to ensure that only the relevant results are included based on the intent provided (e.g., whether the document is related to training or delivery readiness).
3.	Retrieving Texts from BigQuery:
o	The function get_text_results_from_bigquery fetches the text data from Google BigQuery based on the filtered chunk IDs. It forms a SQL query to get the text content and its corresponding ID from a specific table, ensuring that it only retrieves chunks associated with the correct index and project.
5.3.7 Generating LLM Response
An LLM response is generated from the text data associated with the filtered result.

 
This code is designed to generate a response to a user question by using the context provided from chunked documents and leveraging a language model (specifically gemini-1.0-pro-001).
Here's a breakdown of what it does:
1.	Preparing the Context:
o	The function starts by combining all the chunks of context (the relevant document sections) into a single string. It iterates over the chunked_context and formats it into a readable form, labelling each chunk sequentially (e.g., "Context 1", "Context 2", etc.).
2.	Creating the Prompt:
o	The question is added to the context to form a complete prompt. This prompt will be sent to the language model, and the model will use both the context and the question to generate a response.
3.	Generating the Response:
o	The GenerativeModel("gemini-1.0-pro-001") is used to generate the response. The prompt is passed to the model along with configuration settings such as the maximum output tokens and the top_p parameter, which influences the diversity of the response.
o	The stream=True setting allows the model to generate content in real-time, providing a continuous stream of text as it's generated.
4.	Collecting the Response:
o	The code iterates through the streamed responses, extracting the content and appending it to response_list. Finally, the list of responses is joined into a single string and returned.
