import requests
from habanero import Crossref
import yaml
import os
import re

# HTML 태그 제거를 위한 함수 추가
def clean_text(text):
    if not text:
        return ""
    # <sub>, <i>, <jats:p> 등 모든 HTML 형태의 태그 제거
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

def get_publications(orcid_id):
    cr = Crossref()
    orcid_url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    headers = {"Accept": "application/json"}
    response = requests.get(orcid_url, headers=headers)
    data = response.json()

    publications = []
    
    for work in data.get('group', []):
        try:
            summary = work['work-summary'][0]
            external_ids = summary.get('external-ids', {}).get('external-id', [])
            doi = next((item['external-id-value'] for item in external_ids if item['external-id-type'] == 'doi'), None)
            
            if doi:
                res = cr.works(ids=doi)
                item = res['message']
                
                # 데이터 정제 적용
                raw_title = item.get('title', ['No Title'])[0]
                raw_abstract = item.get('abstract', '')
                
                pub_info = {
                    'title': clean_text(raw_title),
                    'authors': ", ".join([f"{a.get('given')} {a.get('family')}" for a in item.get('author', [])]),
                    'journal': item.get('container-title', [''])[0],
                    'year': item.get('published-print', item.get('published-online', {})).get('date-parts', [[0]])[0][0],
                    'volume': item.get('volume', ''),
                    'issue': item.get('issue', ''),
                    'doi': doi,
                    'url': f"https://doi.org/{doi}",
                    'abstract': clean_text(raw_abstract),
                    'article_number': item.get('article-number', '')
                }
                publications.append(pub_info)
                print(f"✅ Success: {pub_info['title']}")
        except Exception as e:
            print(f"❌ Error processing a paper: {e}")
            continue

    # 결과 저장
    publications.sort(key=lambda x: x.get('year', 0), reverse=True)
    
    # 폴더가 없을 경우 생성
    if not os.path.exists('_data'):
        os.makedirs('_data')

    with open('_data/publications.yml', 'w', encoding='utf-8') as f:
        yaml.dump(publications, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

if __name__ == "__main__":
    get_publications("0000-0001-5727-5716")
