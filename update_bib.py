import requests
import time
import json
import re

# ==========================================
# [설정] 교수님의 ORCID ID
ORCID_ID = "0000-0001-5727-5716" 
OUTPUT_FILE = "publications.bib"
# ==========================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

def get_works_summary(orcid_id):
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    print(f"📡 ORCID 데이터 조회 중: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get("group", [])
        return []
    except:
        return []

def extract_doi(work_group):
    """DOI 추출"""
    try:
        summary = work_group["work-summary"][0]
        put_code = summary["put-code"]
        external_ids = summary.get("external-ids", {}).get("external-id", [])
        for eid in external_ids:
            if eid.get("external-id-type") == "doi":
                return eid.get("external-id-value"), put_code
        return None, put_code
    except:
        return None, None

def get_bibtex_from_doi(doi):
    """DOI -> BibTeX 변환 (가장 고품질)"""
    url = f"https://doi.org/{doi}"
    headers = {"Accept": "application/x-bibtex; charset=utf-8"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
    except:
        pass
    return None

def get_bibtex_from_orcid(orcid_id, put_code):
    """ORCID -> BibTeX 변환"""
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/work/{put_code}"
    headers = HEADERS.copy()
    headers["Accept"] = "application/x-bibtex"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
    except:
        pass
    return None

def generate_fallback_bibtex(work_group):
    """[중요] DOI도 없고 변환도 안 될 때, 강제로 BibTeX 생성"""
    try:
        summary = work_group["work-summary"][0]
        title = summary.get("title", {}).get("title", {}).get("value", "No Title")
        year = summary.get("publication-date", {}).get("year", {}).get("value", "")
        journal = summary.get("journal-title", {}).get("value", "Unknown Journal")
        put_code = summary["put-code"]
        url = summary.get("url", {}).get("value", "")
        
        # 특수문자 제거 (BibTeX 오류 방지)
        title = title.replace('"', '').replace('{', '').replace('}', '')
        
        # 수동 BibTeX 포맷 생성
        bib_entry = f"""@article{{orcid_{put_code},
  title = {{{title}}},
  journal = {{{journal}}},
  year = {{{year}}},
  url = {{{url}}},
  note = {{Generated from ORCID record}}
}}"""
        return bib_entry
    except Exception as e:
        print(f"⚠️ 강제 생성 실패: {e}")
        return None

def main():
    works = get_works_summary(ORCID_ID)
    if not works:
        print("🛑 ORCID에서 논문을 찾지 못했습니다.")
        return

    all_bibtex = []
    
    print(f"🚀 총 {len(works)}건의 논문 처리 시작...")
    
    for i, work in enumerate(works):
        bib = None
        doi, put_code = extract_doi(work)
        title = work["work-summary"][0].get("title", {}).get("title", {}).get("value", "No Title")
        
        # 1단계: DOI 시도
        if doi:
            bib = get_bibtex_from_doi(doi)
        
        # 2단계: ORCID 변환 시도
        if not bib and put_code:
            bib = get_bibtex_from_orcid(ORCID_ID, put_code)
            
        # 3단계: [추가된 기능] 강제 생성 (Fallback)
        if not bib:
            print(f"  [{i+1}] ⚠️ DOI/변환 실패 -> 강제 생성 시도: {title}")
            bib = generate_fallback_bibtex(work)
            
        if bib:
            all_bibtex.append(bib)
            print(f"  [{i+1}] ✅ 저장 완료: {title[:30]}...")
        else:
            print(f"  [{i+1}] ❌ 최종 실패 (데이터 부족): {title}")
            
        time.sleep(0.2)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_bibtex))
    print(f"\n🎉 작업 끝! 총 {len(all_bibtex)}편 저장됨.")

if __name__ == "__main__":
    main()
