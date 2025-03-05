from vertexai.preview.generative_models import GenerativeModel
from vertexai.preview.generative_models import GenerativeModel
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
from google.cloud import bigquery

PROJECT_DEV = "xxxx"
PROJECT_PROD = "xxxx"

INDEX_ENDPOINT_NAME="xxxx"
VERTEXAI_MODEL="textembedding-gecko@003"
VERTEXAI_NEIGHBORS=30
CLIENT = bigquery.Client()
MODEL = TextEmbeddingModel.from_pretrained(VERTEXAI_MODEL)

intent_and_docs_matching = {
    "ABC Doc": "abc_index",
}

def encode_texts_to_embeddings(sentences):
    try:
        embeddings = MODEL.get_embeddings(sentences)
        return [embedding.values for embedding in embeddings]
    except Exception:
        return [None for _ in range(len(sentences))]

def get_index_name_by_project(project):
    return aiplatform.MatchingEngineIndex(
        aiplatform.MatchingEngineIndexEndpoint.list(
            project=project,
            filter=f'display_name="{INDEX_ENDPOINT_NAME}"'
        )[0].deployed_indexes[0].index,
    ).display_name
    
    
def get_index_endpoint_by_project(project):
    return aiplatform.MatchingEngineIndexEndpoint(
        aiplatform.MatchingEngineIndexEndpoint.list(
            project=project,
            filter=f'display_name="{INDEX_ENDPOINT_NAME}"'
        )[0].resource_name
    )

def vector_search_query(question, project):
    index_endpoint = get_index_endpoint_by_project(project)
    test_embeddings = encode_texts_to_embeddings(sentences=[question])
    return index_endpoint.find_neighbors(
        deployed_index_id=index_endpoint.deployed_indexes[0].id,
        queries=test_embeddings,
        num_neighbors=VERTEXAI_NEIGHBORS,
    )[0]

def filter_chunks_by_intent(similarity_results, intent):
    filtered_results = []
    for result in similarity_results:    
        for doc in intent_and_docs_matching:
            if result.id.startswith(doc) and intent_and_docs_matching[doc] == intent:
                filtered_results.append(result.id)
    return filtered_results
    
def get_text_results_from_bigquery(chunk_ids, project):
    index_name = get_index_name_by_project(project)
    if not chunk_ids: return []
    query = f"""
        SELECT text, id
        FROM `{project}.{project.replace("-","_")}.vertex_ai_embeddings`
        WHERE id IN {str(chunk_ids).replace("[","(").replace("]",")")} AND index = "{index_name}";
    """
    print(f"BQ queries are {query}\n")
    rows = CLIENT.query(query).result()
    texts = []

    for row in rows:
        texts.append(row[0])
    return texts

def generate_llm_response(chunked_context, question):
    response_list = []
    context = ""
    for ix, data in enumerate(chunked_context):
        context += f"Context {ix + 1}: {data}"
    prompt = f"""
    Question: {question}"""

    text_model = GenerativeModel("gemini-1.0-pro-001")
    responses = text_model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": 5100,
            "top_p": 0.8
        },
        safety_settings=[],
        stream=True,
    )
    for response in responses:
        if response.candidates[0].content.parts:
            response_list.append(response.text)

    return ''.join(response_list)
