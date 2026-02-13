import requests
import time
import re

# ==========================================
# [설정] 교수님의 ORCID ID
ORCID_ID = "0000-0001-5727-5716" 
OUTPUT_FILE = "publications.bib"
# ==========================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json"
}

def get_works_summary(orcid_id):
    """ORCID에서 논문 목록과 DOI 정보를 가져옵니다."""
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    print(f"📡 ORCID 접속 중: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"❌ ORCID 접속 실패 (Code: {response.status_code})")
            return []
        
        data = response.json()
        works = data.get("group", [])
        print(f"✅ ORCID에서 {len(works)}개의 논문 그룹 발견")
        return works
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return []

def extract_doi(work_group):
    """논문 정보에서 DOI를 추출합니다."""
    try:
        summaries = work_group.get("work-summary", [])
        if not summaries: return None, None
        
        # 첫 번째 요약본 사용
        summary = summaries[0]
        put_code = summary["put-code"]
        external_ids = summary.get("external-ids", {}).get("external-id", [])
        
        for eid in external_ids:
            if eid.get("external-id-type") == "doi":
                return eid.get("external-id-value"), put_code
                
        return None, put_code
    except:
        return None, None

def get_bibtex_from_doi(doi):
    """DOI를 이용해 Crossref에서 깨끗한 BibTeX를 가져옵니다."""
    url = f"https://doi.org/{doi}"
    headers = {"Accept": "application/x-bibtex; charset=utf-8"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        return None
    except:
        return None

def get_bibtex_from_orcid(orcid_id, put_code):
    """DOI가 없을 때 ORCID에서 직접 가져오기 (비상용)"""
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/work/{put_code}"
    headers = {"Accept": "application/x-bibtex", "User-Agent": HEADERS["User-Agent"]}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
    except:
        pass
    return None

def main():
    works = get_works_summary(ORCID_ID)
    
    if not works:
        print("🛑 논문을 찾지 못했습니다. ORCID 상태를 확인해주세요.")
        return

    all_bibtex = []
    success_count = 0
    
    print("🚀 데이터 변환 시작 (DOI 우선 검색)...")
    
    for i, work in enumerate(works):
        doi, put_code = extract_doi(work)
        bib = None
        
        # 1. DOI가 있으면 Crossref에서 가져오기 (가장 확실함)
        if doi:
            bib = get_bibtex_from_doi(doi)
            if bib:
                print(f"  [{i+1}] DOI 성공: {doi}")
        
        # 2. DOI 실패시 ORCID에서 직접 시도
        if not bib and put_code:
            bib = get_bibtex_from_orcid(ORCID_ID, put_code)
            if bib:
                print(f"  [{i+1}] ORCID 직접 가져오기 성공 (DOI 없음)")
        
        if bib:
            all_bibtex.append(bib)
            success_count += 1
        else:
            print(f"  [{i+1}] ⚠️ 실패: 정보를 가져올 수 없음")
            
        time.sleep(0.3) # 서버 부하 방지

    # 파일 저장
    if all_bibtex:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n\n".join(all_bibtex))
        print(f"\n🎉 최종 완료! 총 {success_count}편의 논문이 저장되었습니다.")
    else:
        print("\n❌ 저장된 논문이 없습니다.")

if __name__ == "__main__":
    main()
