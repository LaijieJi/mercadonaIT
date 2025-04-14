# ---- 1.START-UP SETUP ----
import requests
import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
es = Elasticsearch("http://localhost:8001")

# ---------- 1.1 GET ALL THE NEEDED PRODUCT INFO ------------

productos = []
url = "https://tienda.mercadona.es/api/categories/"
response = requests.get(url)


if response.status_code == 200:
    data = response.json()

    for categoria in data['results']:
        for subcategoria in categoria['categories']:
            # ID de cada uno de los extended url
            id = str(subcategoria['id'])
            categoria_url = "https://tienda.mercadona.es/api/categories/" + id +"/"
            response = requests.get(categoria_url)

            if response.status_code == 200:
                data = response.json()
                for subcategoria in data['categories']:
                    for products in subcategoria['products']:
                        productos.append({'id': products['id'],
                                            'name': products['slug'],
                                            'category': subcategoria['name'],
                                            'thumbnail': products['thumbnail'],
                                            'price': products['price_instructions']['unit_price']
                                            })
            else:
                print(f"Error al hacer la solicitud de subcategoria: {response.status_code}")
else:
    print(f"Error al hacer la solicitud general: {response.status_code}")



# ---------- 1.2 INDEX IT SMARTLY AND TRY QUERIES ------------

if es.indices.exists(index="productos"):
    es.indices.delete(index="productos")

es.indices.create(
    index="productos",
    body={
        "mappings": {
            "properties": {
                "name": {"type": "text"},
                "category": {"type": "text"}, #not keyword because categories can be various words
                "price": {"type": "float"}
            }
        }
    }
)

success, errors = bulk(es, [
    {
        "_index": "productos",
        "_id": p['id'],
        "_source": p
    }
    for p in productos
], stats_only=False)
# explicit refresh for indexing
es.indices.refresh(index="productos")






# ---------- 2. QUERIES ------------
def query(ingredients):
    ans = []
    stopwords = ["cucharadas", "cucharada", "cucharadita", "cucharaditas", "taza", "tazas", "1/2", "1/4", "1", "2", "3", "4", "pizca"]

    for ingredient in ingredients:
        subingredients = ingredient.split(" ")
        ingredient = ""
        for subingredient in subingredients:
            if subingredient not in stopwords:
                ingredient += subingredient + " "
            
        query = {
            "query": {
                "function_score": {
                    "query": {
                        "match": {
                            "name": ingredient
                        }
                    },
                    "boost_mode": "sum", 
                    "functions": [
                        {
                            "filter": {
                                "term": {
                                    "category": ingredient
                                }
                            },
                            "weight": 7  #boost if category is the same
                        }
                    ]
                }
            }
        }
        res = es.search(index="productos", body=query)

        all_results = []
        for hit in res["hits"]["hits"]:
            all_results.append({
                "score": hit["_score"],
                "ingredient": ingredient,
                "source": hit["_source"]
            })
        
        # best result for the moment the one with higher score (CAN BE IMPROVED)
        if not all_results:
            best_result = {'source':
                            {
                                'id': "",
                                'name': "NOT FOUND",
                                'category': "",
                                'thumbnail': "",
                                'price': 0
                            }
                        }
        else: 
            sorted_results = sorted(all_results, key=lambda x: x["score"], reverse=True)
            best_result = sorted_results[0]

        #print(sorted_results)
        ans.append(best_result)
    
    ans2 = []
    for n in ans:
        ans2.append(n["source"])
    return ans2
