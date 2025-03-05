from vertexai.preview.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingModel
from google.cloud import aiplatform, bigquery
from google.cloud.aiplatform import MatchingEngineIndex, MatchingEngineIndexEndpoint

PROJECT_PROD = "xxx"
PROJECT_DEV = "xxx"

INDEX_ENDPOINT_NAME="intent-handler"
VERTEXAI_MODEL="textembedding-gecko@003"
MODEL = TextEmbeddingModel.from_pretrained(VERTEXAI_MODEL)
VERTEXAI_NEIGHBORS=5
CLIENT = bigquery.Client()

def encode_texts_to_embeddings(sentences):
    try:
        embeddings = MODEL.get_embeddings(sentences)
        return [embedding.values for embedding in embeddings]
    except Exception:
        return [None for _ in range(len(sentences))]

def get_index_endpoint_by_project(project):
    return aiplatform.MatchingEngineIndexEndpoint(
            aiplatform.MatchingEngineIndexEndpoint.list(
                project=project,
                filter=f'display_name="{INDEX_ENDPOINT_NAME}"'
            )[0].resource_name
    )

def get_index_name_by_project(project):
    return aiplatform.MatchingEngineIndex(
        aiplatform.MatchingEngineIndexEndpoint.list(
            project=project,
            filter=f'display_name="{INDEX_ENDPOINT_NAME}"'
        )[0].deployed_indexes[0].index,
    ).display_name

def vector_search_query(question, project):
    print("Getting index endpoint\n")
    index_endpoint = get_index_endpoint_by_project(project)
    print("Getting embeddings\n")
    test_embeddings = encode_texts_to_embeddings(sentences=[question])
    return index_endpoint.find_neighbors(
        deployed_index_id=index_endpoint.deployed_indexes[0].id,
        queries=test_embeddings,
        num_neighbors=VERTEXAI_NEIGHBORS,
    )[0]

def get_intent_from_id(similarity_result):
    return similarity_result.id.split("-")[0]

def get_text_results_from_bigquery(chunk_ids, project):
    index_name = get_index_name_by_project(project)
    if not chunk_ids: return []
    query = f"""
        SELECT text, id
        FROM `{project}.{project.replace("-","_")}.vertex_ai_embeddings`
        WHERE id IN {str(chunk_ids).replace("[","(").replace("]",")")} AND index = "{index_name}";
    """

    rows = CLIENT.query(query).result()
    texts = []

    for row in rows:
        texts.append(row[0])
    return texts

