# update_publications.py 수정 부분
def get_publications(orcid_id):
    # ... (중간 생략: 기존 추출 로직은 동일) ...
    
    # 1. 교수님 성함 강조 (Bold)
    name_to_highlight = "Eun Kwang Lee"
    for pub in publications:
        if name_to_highlight in pub['authors']:
            pub['authors'] = pub['authors'].replace(name_to_highlight, f"<b>{name_to_highlight}</b>")

    # 2. 연도별 그룹화 데이터 생성
    grouped_pubs = {}
    for pub in publications:
        year = str(pub['year'])
        if year not in grouped_pubs:
            grouped_pubs[year] = []
        grouped_pubs[year].append(pub)

    # 3. 정렬된 리스트로 변환 (최신순)
    final_data = [{"year": y, "items": grouped_pubs[y]} for y in sorted(grouped_pubs.keys(), reverse=True)]

    with open('_data/publications.yml', 'w', encoding='utf-8') as f:
        yaml.dump(final_data, f, allow_unicode=True, sort_keys=False)
