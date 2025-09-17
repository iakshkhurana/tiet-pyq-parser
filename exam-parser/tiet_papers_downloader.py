#!/usr/bin/env python3
from __future__ import annotations
import os, re, sys, time, pathlib, requests
from typing import List, Dict
from selenium import webdriver
import urllib3
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
from selenium.webdriver.common.keys import Keys


ROOT_URL = "https://cl.thapar.edu"
OLD_PAPERS_PARTIAL_LINK = "Old Question Papers"
# Download to user's Downloads folder
DOWNLOAD_DIR = pathlib.Path.home() / "Downloads" / "ThaparPapers"
HEADLESS = True  # set False to watch the browser

def make_driver(download_dir: pathlib.Path, headless: bool = True) -> webdriver.Chrome:
    download_dir.mkdir(parents=True, exist_ok=True)
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    
    # GPU and rendering fixes
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-gpu-sandbox")
    opts.add_argument("--disable-software-rasterizer")
    opts.add_argument("--disable-background-timer-throttling")
    opts.add_argument("--disable-backgrounding-occluded-windows")
    opts.add_argument("--disable-renderer-backgrounding")
    opts.add_argument("--disable-features=TranslateUI")
    opts.add_argument("--disable-ipc-flooding-protection")
    
    # Memory and stability fixes
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-plugins")
    opts.add_argument("--disable-images")
    opts.add_argument("--window-size=1400,1000")
    
    # Logging suppression
    opts.add_argument('--log-level=3')
    opts.add_argument('--disable-logging')
    opts.add_argument('--silent')
    opts.add_argument('--disable-web-security')
    opts.add_argument('--disable-features=VizDisplayCompositor')
    
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    opts.add_experimental_option("prefs", {
        "download.default_directory": str(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    })
    drv = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
    try:
        drv.execute_cdp_cmd("Page.setDownloadBehavior",
                            {"behavior": "allow", "downloadPath": str(download_dir)})
    except Exception:
        pass
    return drv

def normalize_course_code(course_code: str) -> str:
    """
    Normalize course code to handle different formats:
    - Remove hyphens and spaces
    - Convert to uppercase
    - Examples: 'ucs503' -> 'UCS503', 'ucs-503' -> 'UCS503', 'UCS-530' -> 'UCS530'
    """
    if not course_code:
        return ""
    
    # Remove hyphens, spaces, and convert to uppercase
    normalized = course_code.replace('-', '').replace(' ', '').upper()
    return normalized

def wait_for_results(driver, query_text: str, timeout=12):
    """
    Wait for either the results header OR at least one data row.
    Also tries to wait for a row containing the query (for code searches).
    """
    print(f"Waiting for results with query: '{query_text}'")
    
    banner = (By.XPATH, "//*[contains(., 'These results matches your search criteria')]")
    table_row = (By.XPATH, "//table//tr[td]")
    code_row = (By.XPATH, f"//table//tr[td and normalize-space(td[1])='{query_text}']")
    
    # Also wait for any loading indicators to disappear
    loading_indicators = [
        "//div[contains(@class, 'loading')]",
        "//div[contains(@id, 'loading')]",
        "//*[contains(text(), 'Loading')]",
        "//*[contains(text(), 'Please wait')]"
    ]
    
    try:
        # First wait for loading indicators to disappear
        for indicator in loading_indicators:
            try:
                WebDriverWait(driver, 5).until_not(
                    EC.presence_of_element_located((By.XPATH, indicator))
                )
            except:
                pass  # Loading indicator might not exist, that's fine
        
        # Then wait for actual results
        result = WebDriverWait(driver, timeout).until(
            lambda d: (
                d.find_elements(*banner) or 
                d.find_elements(*code_row) or 
                len(d.find_elements(*table_row)) > 1
            )
        )
        
        # Debug: print what we found
        if driver.find_elements(*banner):
            print("Found results banner")
        if driver.find_elements(*code_row):
            print(f"Found specific course code row for: {query_text}")
        if len(driver.find_elements(*table_row)) > 1:
            print(f"Found {len(driver.find_elements(*table_row))} table rows")
            
        return True
        
    except Exception as e:
        print(f"Timeout waiting for results: {e}")
        # Debug: print current page state
        try:
            page_source = driver.page_source
            if "no results" in page_source.lower() or "no data" in page_source.lower():
                print("Page indicates no results found")
            elif "error" in page_source.lower():
                print("Page shows an error")
            else:
                print("Page loaded but no clear results indicator found")
        except:
            pass
        return False

# ...existing code...


def wait_present(driver, by, selector, timeout=30):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, selector)))

def fill_and_submit(input_el, text: str):
    print(f"Filling input with: '{text}'")
    
    # Make sure focus is on the input and we overwrite anything present
    input_el.click()
    time.sleep(0.5)  # Small delay to ensure focus
    
    input_el.send_keys(Keys.CONTROL, "a")
    input_el.send_keys(Keys.DELETE)
    time.sleep(0.2)  # Small delay after clearing
    
    input_el.send_keys(text)
    time.sleep(0.5)  # Small delay after typing

    # Try Enter first (many forms wire Enter to submit)
    try:
        print("Trying to submit with Enter key...")
        input_el.send_keys(Keys.ENTER)
        time.sleep(1)  # Wait a moment for form submission
        return
    except Exception as e:
        print(f"Enter key submission failed: {e}")

    # Otherwise click the nearest form's submit control (input/button)
    try:
        print("Looking for submit button in form...")
        form = input_el.find_element(By.XPATH, "ancestor::form[1]")
        submit = form.find_element(
            By.XPATH,
            ".//input[@type='submit' or contains(translate(@value,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'submit')]"
            "|.//button[@type='submit' or contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'submit')]"
        )
        WebDriverWait(input_el.parent, 10).until(EC.element_to_be_clickable(submit))
        submit.click()
        time.sleep(1)  # Wait for form submission
    except Exception as e:
        print(f"Form submit button failed: {e}")
        # Last resort: first submit/button on page
        try:
            print("Looking for any submit button on page...")
            btn = WebDriverWait(input_el.parent, 10).until(EC.element_to_be_clickable((
                By.XPATH,
                "(//input[@type='submit' or contains(translate(@value,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'submit')]"
                "|//button[@type='submit' or contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'submit')])[1]"
            )))
            btn.click()
            time.sleep(1)  # Wait for form submission
        except Exception as e2:
            print(f"All submit methods failed: {e2}")
            raise RuntimeError("Could not submit the search form")


def normalize_filename(t: str) -> str:
    t = re.sub(r"[^\w\s.-]", "", t).strip()
    return re.sub(r"\s+", "_", t) or "file"

def collect_results_rows(driver):
    print("Collecting results from page...")
    tables = driver.find_elements(By.XPATH, "//table")
    print(f"Found {len(tables)} tables on page")
    
    rows_out = []
    for i, tbl in enumerate(tables):
        rows = tbl.find_elements(By.XPATH, ".//tr")
        print(f"Table {i+1}: {len(rows)} rows")
        
        if len(rows) < 2:
            continue
            
        for j, r in enumerate(rows[1:], 1):  # skip first row (header)
            tds = r.find_elements(By.XPATH, ".//td")
            if len(tds) >= 5:
                # extra guard: ignore header-like rows
                first = (tds[0].text or "").strip().lower()
                if first in {"course code", "course code", "course_code"}:
                    print(f"Skipping header row: {first}")
                    continue
                
                # Debug: print the course code we found
                course_code = tds[0].text.strip()
                print(f"Found course: {course_code}")
                rows_out.append(r)
            else:
                print(f"Row {j} has only {len(tds)} columns, skipping")
                
        if rows_out:
            print(f"Using table {i+1} with {len(rows_out)} valid rows")
            break
    
    print(f"Total valid rows collected: {len(rows_out)}")
    return rows_out


def row_to_record(row) -> Dict[str, str]:
    tds = row.find_elements(By.XPATH, ".//td")
    rec = {
        "course_code": tds[0].text.strip(),
        "course_name": tds[1].text.strip(),
        "year": tds[2].text.strip() if len(tds) > 2 else "",
        "semester": tds[3].text.strip() if len(tds) > 3 else "",
        "exam_type": tds[4].text.strip() if len(tds) > 4 else "",
        "download_href": "",
    }
    for a in row.find_elements(By.XPATH, ".//a"):
        if a.text.strip().lower() == "download":
            rec["download_href"] = a.get_attribute("href") or ""
            break
    return rec

def pick_indices(n: int) -> List[int]:
    while True:
        raw = input("\nSelect items (e.g., 1,3-5) or 'a' for all: ").strip().lower()
        if raw in {"a", "all", "*"}:
            return list(range(1, n + 1))
        try:
            result = set()
            for part in raw.split(","):
                part = part.strip()
                if "-" in part:
                    lo, hi = map(int, part.split("-", 1))
                    if lo < 1 or hi > n or lo > hi: raise ValueError
                    result.update(range(lo, hi + 1))
                else:
                    k = int(part)
                    if k < 1 or k > n: raise ValueError
                    result.add(k)
            return sorted(result)
        except Exception:
            print("Invalid input. Try again.")

def requests_session_from_driver(driver) -> requests.Session:
    s = requests.Session()
    for ck in driver.get_cookies():
        c = {k: ck.get(k) for k in ["domain","name","value","path","secure"]}
        if ck.get("expiry") is not None:
            c["expires"] = ck["expiry"]
        s.cookies.set(**c)
    s.headers.update({"User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"})
    # ↓↓↓ add these two lines ↓↓↓
    s.verify = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    return s


def download_pdf(session: requests.Session, url: str, dest: pathlib.Path):
    with session.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        with open(dest, "wb") as f, tqdm(total=total or None, unit="B", unit_scale=True,
                                         desc=dest.name, leave=False) as pbar:
            for chunk in r.iter_content(65536):
                if chunk:
                    f.write(chunk)
                    if total: pbar.update(len(chunk))

# ---------- NEW: robust open & input finders ----------

def open_old_papers(driver):
    wait_present(driver, By.TAG_NAME, "body", 30)
    link = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
        (By.XPATH, f"//a[contains(., '{OLD_PAPERS_PARTIAL_LINK}')]")))
    href = link.get_attribute("href")
    if href:
        driver.get(href)
    else:
        current = set(driver.window_handles)
        link.click()
        WebDriverWait(driver, 10).until(lambda d: len(set(d.window_handles) - current) > 0)
        new_handle = list(set(driver.window_handles) - current)[0]
        driver.switch_to.window(new_handle)

def find_course_code_input(driver):
    strategies = [
        "//label[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'course code')]/following::input[@type='text'][1]",
        "//input[@type='text' and (contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'code'))]",
        "//input[@type='text' and (contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'code'))]",
        "//input[@type='text' and (contains(translate(@id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'code'))]",
    ]
    for xp in strategies:
        els = driver.find_elements(By.XPATH, xp)
        if els: return els[0]
    return None

def find_course_name_input(driver):
    strategies = [
        "//label[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'course name')]/following::input[@type='text'][1]",
        "//input[@type='text' and (contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'name'))]",
        "//input[@type='text' and (contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'name'))]",
        "//input[@type='text' and (contains(translate(@id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'name'))]",
    ]
    for xp in strategies:
        els = driver.find_elements(By.XPATH, xp)
        if els: return els[0]
    return None

def click_following_submit(inp):
    """
    Submit the search:
    1) Try Enter key in the input (many forms wire this up)
    2) Otherwise click the nearest form's submit button
       (handles <input type=submit> or <button type=submit> or text 'Submit')
    """
    # Try pressing Enter first
    try:
        inp.send_keys(Keys.ENTER)
        # give it a moment—if the URL or DOM changes, we're good
        WebDriverWait(inp.parent, 2).until_not(
            EC.presence_of_element_located((By.XPATH, "//div[@id='loading-please-wait']"))
        )
        return
    except Exception:
        pass

    # Find the nearest form
    form = None
    try:
        form = inp.find_element(By.XPATH, "ancestor::form[1]")
    except Exception:
        form = None

    if form is None:
        # fall back: click the first clickable submit/button on page (last resort)
        btn = WebDriverWait(inp.parent, 10).until(EC.element_to_be_clickable((
            By.XPATH,
            "(//input[@type='submit' or contains(translate(@value,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'submit')]"
            "|//button[@type='submit' or contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'submit')])[1]"
        )))
        btn.click()
        return

    # Prefer a submit control inside the same form
    submit_xpath = (
        ".//input[@type='submit' or contains(translate(@value,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'submit')]"
        "|.//button[@type='submit' or contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'submit')]"
    )
    try:
        btn = form.find_element(By.XPATH, submit_xpath)
        WebDriverWait(inp.parent, 10).until(EC.element_to_be_clickable(btn))
        btn.click()
    except Exception:
        # final fallback: send Enter again
        inp.send_keys(Keys.ENTER)


# ---------- main ----------

def main():
    driver = make_driver(DOWNLOAD_DIR, HEADLESS)
    driver.get(ROOT_URL)
    open_old_papers(driver)
    WebDriverWait(driver, 30).until(
        lambda d: (find_course_code_input(d) is not None) or (find_course_name_input(d) is not None)
    )

    import sys
    option = None
    value = None
    mergePdfs = False
    examFilter = "all"
    if len(sys.argv) >= 3:
        option = sys.argv[1]
        value = sys.argv[2]
        if len(sys.argv) >= 4:
            mergePdfs = sys.argv[3].lower() == "true"
        if len(sys.argv) >= 5:
            examFilter = sys.argv[4]
    if option:
        by_code = option != "2"
        query = normalize_course_code(value.strip()) if by_code else value.strip()
    else:
        by_code = input("Enter 1 or 2: ").strip() != "2"
        if by_code:
            raw_input = input("Enter Course Code: ").strip()
            query = normalize_course_code(raw_input)
            print(f"Normalized course code: {query}")
        else:
            query = input("Enter Course Name (or part): ").strip()
    if by_code:
        code_input = find_course_code_input(driver)
        if not code_input:
            raise RuntimeError("Couldn't locate the Course Code input.")
        fill_and_submit(code_input, query)
    else:
        name_input = find_course_name_input(driver)
        if not name_input:
            raise RuntimeError("Couldn't locate the Course Name input.")
        fill_and_submit(name_input, query)

    # Wait for search results to load
    print(f"Waiting for search results for: {query}")
    if not wait_for_results(driver, query, timeout=20):
        print("Search results did not load within timeout period.")
        driver.quit()
        return

    rows = collect_results_rows(driver)
    if not rows:
        print("No results found.")
        driver.quit()
        return

    records = []
    for r in rows:
        rec = row_to_record(r)
        records.append(rec)

    # Apply exam type filter if specified
    if examFilter != "all":
        records = [rec for rec in records if rec['exam_type'] == examFilter]
        if not records:
            print(f"No results found for exam type: {examFilter}")
            driver.quit()
            return

    # Check if running in non-interactive mode (called from backend)
    if len(sys.argv) >= 3:
        # Non-interactive mode: select all records and use provided merge setting
        idxs = list(range(1, len(records) + 1))
        merge_choice = 'y' if mergePdfs else 'n'
    else:
        # Interactive mode: ask user for input
        idxs = pick_indices(len(records))
        merge_choice = input("Would you like to merge all PDFs for each course (only keep merged file)? (y/n): ").strip().lower()
    
    session = requests_session_from_driver(driver)
    chosen = [records[i-1] for i in idxs]
    groups: Dict[str, List[Dict[str, str]]] = {}
    for rec in chosen:
        key = f"{rec['course_code']}__{normalize_filename(rec['course_name'])}"
        groups.setdefault(key, []).append(rec)
    
    total = sum(1 for r in chosen if r["download_href"])
    done = 0
    from PyPDF2 import PdfMerger
    for course_key, group in groups.items():
        cdir = DOWNLOAD_DIR / course_key
        cdir.mkdir(parents=True, exist_ok=True)
        pdf_paths = []
        for rec in group:
            href = rec["download_href"]
            if not href: continue
            if href.startswith("/"): href = ROOT_URL.rstrip("/") + href
            fname = f"{rec['course_code']}_{normalize_filename(rec['course_name'])}_{rec['year']}_{rec['semester']}_{rec['exam_type']}.pdf"
            dest = cdir / fname
            try:
                download_pdf(session, href, dest)
                pdf_paths.append(dest)
                done += 1
            except Exception:
                pass
        if merge_choice == 'y' and len(pdf_paths) > 1:
            merger = PdfMerger()
            for pdf in pdf_paths:
                merger.append(str(pdf))
            merged_path = cdir / f"{course_key}_merged.pdf"
            merger.write(str(merged_path))
            merger.close()
            for pdf in pdf_paths:
                try:
                    pdf.unlink()
                except Exception:
                    pass
    print(f"SUCCESS: Downloaded {done}/{total} file(s) to Downloads/ThaparPapers/")
    driver.quit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
