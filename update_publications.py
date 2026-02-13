import requests
from habanero import Crossref
import yaml
import os
import re

def clean_text(text):
    if not text: return ""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

def get_publications(orcid_id):
    cr = Crossref()
    orcid_url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    headers = {"Accept": "application/json"}
    response = requests.get(orcid_url, headers=headers)
    data = response.json()

    raw_publications = []
    name_to_bold = "Eun Kwang Lee" # 교수님 성함 강조 설정

    for work in data.get('group', []):
        try:
            summary = work['work-summary'][0]
            external_ids = summary.get('external-ids', {}).get('external-id', [])
            doi = next((item['external-id-value'] for item in external_ids if item['external-id-type'] == 'doi'), None)
            
            if doi:
                res = cr.works(ids=doi)
                item = res['message']
                
                # 저자 정보 처리 및 교수님 성함 강조
                authors_list = [f"{a.get('given')} {a.get('family')}" for a in item.get('author', [])]
                authors_str = ", ".join(authors_list)
                if name_to_bold in authors_str:
                    authors_str = authors_str.replace(name_to_bold, f"<b>{name_to_bold}</b>")

                pub_info = {
                    'title': clean_text(item.get('title', ['No Title'])[0]),
                    'authors': authors_str,
                    'journal': item.get('container-title', [''])[0],
                    'year': int(item.get('published-print', item.get('published-online', {})).get('date-parts', [[0]])[0][0]),
                    'doi': doi,
                    'url': f"https://doi.org/{doi}",
                    'abstract': clean_text(item.get('abstract', ''))[:500] + "...", # 초록 요약
                }
                raw_publications.append(pub_info)
        except: continue

    # 연도별 그룹화 로직
    grouped_data = {}
    for pub in raw_publications:
        year = str(pub['year'])
        if year not in grouped_data:
            grouped_data[year] = []
        grouped_data[year].append(pub)

    # 최신 연도순으로 정렬된 리스트 생성
    final_output = []
    for year in sorted(grouped_data.keys(), reverse=True):
        final_output.append({
            'year': year,
            'items': grouped_data[year]
        })

    if not os.path.exists('_data'): os.makedirs('_data')
    with open('_data/publications.yml', 'w', encoding='utf-8') as f:
        yaml.dump(final_output, f, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    get_publications("0000-0001-5727-5716")
