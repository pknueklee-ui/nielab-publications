import requests
from habanero import Crossref
import yaml
import os

def get_publications(orcid_id):
    cr = Crossref()
    # 1. ORCID에서 논문 목록 가져오기
    orcid_url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    headers = {"Accept": "application/json"}
    response = requests.get(orcid_url, headers=headers)
    data = response.json()

    publications = []
    
    for work in data.get('group', []):
        # 최신 DOI 추출
        try:
            external_ids = work['work-summary'][0]['external-ids']['external-id']
            doi = next((item['external-id-value'] for item in external_ids if item['external-id-type'] == 'doi'), None)
            
            if doi:
                # 2. Crossref에서 상세 정보 추출
                res = cr.works(ids=doi)
                item = res['message']
                
                pub_info = {
                    'title': item.get('title', ['No Title'])[0],
                    'authors': ", ".join([f"{a.get('given')} {a.get('family')}" for a in item.get('author', [])]),
                    'journal': item.get('container-title', [''])[0],
                    'year': item.get('published-print', item.get('published-online', {})).get('date-parts', [[0]])[0][0],
                    'volume': item.get('volume', ''),
                    'issue': item.get('issue', ''),
                    'doi': doi,
                    'url': f"https://doi.org/{doi}",
                    'abstract': item.get('abstract', '').replace('<jats:p>', '').replace('</jats:p>', ''), # 태그 제거
                    'article_number': item.get('article-number', '')
                }
                publications.append(pub_info)
                print(f"✅ Success: {pub_info['title']}")
        except Exception as e:
            continue

    # 3. 년도 순으로 정렬 후 저장
    publications.sort(key=lambda x: x['year'], reverse=True)
    
    with open('_data/publications.yml', 'w', encoding='utf-8') as f:
        yaml.dump(publications, f, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    get_publications("0000-0001-5727-5716")
