import urllib.request, ssl, json, sys
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def fetch(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        return resp.read().decode('utf-8', errors='ignore')

print("================================================================")
print(" 1. CHECKING RESIDENCE & REALESTATEAGENT SCHEMA ON PROJECT PAGES")
print("================================================================")

project_urls = [
    'https://gurupunvaanii.com/our-projects/villas/elegance/',
    'https://gurupunvaanii.com/elegance-villas-on-mysore-road/',
    'https://gurupunvaanii.com/our-projects/residential/ernika-premium-villa-plots-in-anekal-bangalore/',
    'https://gurupunvaanii.com/our-projects/residential/eureka-plots-in-bidadi-for-sale/',
    'https://gurupunvaanii.com/our-projects/residential/eka-plots-for-sale-in-anekal-bangalore/',
    'https://gurupunvaanii.com/our-projects/residential/ekansh-plots-for-sale-in-mysore/',
    'https://gurupunvaanii.com/our-projects/residential/etasha-site-for-sale-in-tumkur/',
    'https://gurupunvaanii.com/our-projects/residential/exotica-plots-in-attibele/',
    'https://gurupunvaanii.com/our-projects/residential/shyam-residency-sites-in-magadi-road/',
    'https://gurupunvaanii.com/our-projects/residential/sankeshwar-padmavathi-nagar-plots-in-kolar/'
]

def check_project(url):
    slug = url.replace('https://gurupunvaanii.com/', '')
    try:
        html = fetch(url)
        soup = BeautifulSoup(html, 'html.parser')
        types = set()
        for s in soup.find_all('script', type='application/ld+json'):
            try:
                js = json.loads(s.string)
                def extract(obj):
                    if isinstance(obj, dict):
                        t = obj.get('@type')
                        if isinstance(t, list): types.update(t)
                        elif t: types.add(t)
                        for v in obj.values(): extract(v)
                    elif isinstance(obj, list):
                        for item in obj: extract(item)
                extract(js)
            except Exception:
                pass
        has_agent = 'RealEstateAgent' in types
        has_res = any(r in types for r in ['Residence', 'SingleFamilyResidence', 'RealEstateListing', 'House', 'ApartmentComplex'])
        has_bc = 'BreadcrumbList' in types
        return (slug, has_agent, has_res, has_bc, None)
    except Exception as e:
        return (slug, False, False, False, str(e))

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(check_project, project_urls))

for slug, has_agent, has_res, has_bc, err in results:
    if err:
        print(f"[ERROR] {slug} -> {err}")
    else:
        status_text = "[PASS]" if has_res else "[FAIL]"
        print(f"{status_text} {slug} -> RealEstateAgent: {has_agent} | Residence/Listing: {has_res} | Breadcrumb: {has_bc}")

print("\n================================================================")
print(" 2. CHECKING BREADCRUMBLIST SCHEMA (BLOGS, ARCHIVES, PAGES)")
print("================================================================")

sample_urls = [
    'https://gurupunvaanii.com/',
    'https://gurupunvaanii.com/blog/',
    'https://gurupunvaanii.com/blog/category/legal-documentation/',
    'https://gurupunvaanii.com/blog/category/property-buying-guide/',
    'https://gurupunvaanii.com/blog/legal-documentation/what-is-an-encumbrance-certificate-ec-why-its-important/',
    'https://gurupunvaanii.com/blog/property-buying-guide/how-to-check-property-ownership-in-bangalore/'
]

def check_bc(url):
    try:
        html = fetch(url)
        soup = BeautifulSoup(html, 'html.parser')
        types = set()
        for s in soup.find_all('script', type='application/ld+json'):
            try:
                js = json.loads(s.string)
                def extract(obj):
                    if isinstance(obj, dict):
                        t = obj.get('@type')
                        if isinstance(t, list): types.update(t)
                        elif t: types.add(t)
                        for v in obj.values(): extract(v)
                    elif isinstance(obj, list):
                        for item in obj: extract(item)
                extract(js)
            except Exception:
                pass
        return (url, 'BreadcrumbList' in types, None)
    except Exception as e:
        return (url, False, str(e))

with ThreadPoolExecutor(max_workers=6) as executor:
    bc_results = list(executor.map(check_bc, sample_urls))

for url, has_bc, err in bc_results:
    if err:
        print(f"[ERROR] {url} -> {err}")
    else:
        status_text = "[PASS]" if has_bc else ("[INFO - Homepage]" if url == 'https://gurupunvaanii.com/' else "[FAIL]")
        print(f"{status_text} {url} -> BreadcrumbList: {has_bc}")

print("\n================================================================")
print(" 3. CHECKING INTERNAL LINK SILOS (LEGAL / BUYING GUIDES -> PROJECTS)")
print("================================================================")

legal_and_guide_urls = [
    'https://gurupunvaanii.com/blog/legal-documentation/what-is-an-encumbrance-certificate-ec-why-its-important/',
    'https://gurupunvaanii.com/blog/property-buying-guide/how-to-check-property-ownership-in-bangalore/',
    'https://gurupunvaanii.com/blog/legal-documentation/what-is-a-sale-deed-format-types-registration-in-karnataka/',
    'https://gurupunvaanii.com/blog/legal-documentation/difference-between-a-khata-and-b-khata-properties/',
    'https://gurupunvaanii.com/blog/legal-documentation/detailed-guide-to-rera-registration-process-charges-and-documents-required/',
    'https://gurupunvaanii.com/blog/legal-documentation/what-is-e-khata-how-to-apply-download-and-check-status/',
    'https://gurupunvaanii.com/blog/property-buying-guide/why-bmrda-approved-sites-in-anekal-are-the-best-investment-option/',
    'https://gurupunvaanii.com/blog/property-buying-guide/why-investing-in-a-villa-project-in-bidadi-bengaluru-is-a-wise-choice/',
    'https://gurupunvaanii.com/blog/property-buying-guide/exploring-anekal-the-emerging-hotspot-in-bangalore-real-estate/',
    'https://gurupunvaanii.com/blog/property-buying-guide/top-luxury-residential-projects-in-bangalore-2026/'
]

def check_silos(url):
    slug = url.replace('https://gurupunvaanii.com/blog/', '')
    try:
        html = fetch(url)
        soup = BeautifulSoup(html, 'html.parser')
        article = soup.find('div', class_='entry-content') or soup.find('article') or soup.find('div', class_='elementor-widget-theme-post-content') or soup
        content_links = []
        for a in article.find_all('a', href=True):
            href = a['href'].strip()
            text = a.get_text(strip=True)
            content_links.append((href, text))
        
        project_links = [
            (h, t) for h, t in content_links 
            if any(k in h for k in ['/our-projects/', 'elegance', 'ernika', 'eureka', 'eka-plots', 'ekansh', 'etasha', 'exotica', 'shyam-residency', 'sankeshwar'])
        ]
        return (slug, project_links, None)
    except Exception as e:
        return (slug, [], str(e))

with ThreadPoolExecutor(max_workers=10) as executor:
    silo_results = list(executor.map(check_silos, legal_and_guide_urls))

with_links = 0
for slug, proj_links, err in silo_results:
    if err:
        print(f"[ERROR] {slug} -> {err}")
    elif proj_links:
        with_links += 1
        print(f"[FOUND LINKS] {slug}")
        for pl, txt in proj_links[:3]:
            print(f"     -> Link: {pl} (Anchor: \"{txt}\")")
    else:
        print(f"[NO LINKS] {slug} -> NO direct project landing page links found in body.")

print(f"\nInternal Silo Link Summary: {with_links}/{len(legal_and_guide_urls)} guides contain project links.")
