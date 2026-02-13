import requests
import json
import time

# ==========================================
# [설정] 교수님의 ORCID ID (자동 입력됨)
ORCID_ID = "0000-0001-5727-5716" 
OUTPUT_FILE = "publications.bib"
# ==========================================

def get_works_ids(orcid_id):
    """ORCID에서 전체 논문 목록(ID)을 가져옵니다."""
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching works: {response.status_code}")
        return []
    
    data = response.json()
    works = data.get("group", [])
    
    # 각 논문 그룹에서 첫 번째 work-summary의 put-code 추출
    put_codes = []
    for work_group in works:
        summaries = work_group.get("work-summary", [])
        if summaries:
            put_codes.append(summaries[0]["put-code"])
            
    return put_codes

def get_bibtex(orcid_id, put_code):
    """개별 논문의 정보를 BibTeX 형식으로 가져옵니다."""
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/work/{put_code}"
    headers = {"Accept": "application/x-bibtex"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.text
    return None

def main():
    print(f"Starting BibTeX update for ORCID: {ORCID_ID}")
    
    put_codes = get_works_ids(ORCID_ID)
    print(f"Found {len(put_codes)} works.")
    
    all_bibtex = []
    
    for i, code in enumerate(put_codes):
        print(f"Fetching work {i+1}/{len(put_codes)} (ID: {code})...")
        bib = get_bibtex(ORCID_ID, code)
        if bib:
            all_bibtex.append(bib)
        time.sleep(0.5) # API 과부하 방지
        
    # 결과 저장
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_bibtex))
        
    print(f"Successfully saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
