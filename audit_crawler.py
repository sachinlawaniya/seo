import urllib.request, urllib.parse, urllib.error, ssl, re, json, time
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AntigravitySEOAudit/1.0'
}

def fetch_url(url, follow_redirects=True):
    start = time.time()
    try:
        req = urllib.request.Request(url, headers=headers)
        if not follow_redirects:
            class NoRedirect(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, req, fp, code, msg, hdrs, newurl):
                    return None
            opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=ctx))
            try:
                resp = opener.open(req, timeout=15)
                elapsed = time.time() - start
                return {
                    'status': resp.status,
                    'final_url': resp.geturl(),
                    'headers': dict(resp.getheaders()),
                    'body': resp.read(),
                    'elapsed': elapsed,
                    'error': None
                }
            except urllib.error.HTTPError as he:
                elapsed = time.time() - start
                return {
                    'status': he.code,
                    'final_url': url,
                    'headers': dict(he.headers),
                    'body': b'',
                    'elapsed': elapsed,
                    'error': None,
                    'location': he.headers.get('Location')
                }
        else:
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                elapsed = time.time() - start
                body = resp.read()
                return {
                    'status': resp.status,
                    'final_url': resp.geturl(),
                    'headers': dict(resp.getheaders()),
                    'body': body,
                    'elapsed': elapsed,
                    'error': None
                }
    except Exception as e:
        elapsed = time.time() - start
        return {
            'status': 0,
            'final_url': url,
            'headers': {},
            'body': b'',
            'elapsed': elapsed,
            'error': str(e)
        }

# 1. Test canonical redirects (http vs https, www vs non-www, trailing slash)
redirect_tests = [
    'http://gurupunvaanii.com',
    'http://gurupunvaanii.com/',
    'http://www.gurupunvaanii.com',
    'http://www.gurupunvaanii.com/',
    'https://www.gurupunvaanii.com',
    'https://www.gurupunvaanii.com/',
    'https://gurupunvaanii.com',
    'https://gurupunvaanii.com/'
]

redirect_results = {}
for u in redirect_tests:
    res = fetch_url(u, follow_redirects=False)
    redirect_results[u] = {
        'status': res.get('status'),
        'location': res.get('headers', {}).get('Location') or res.get('location'),
        'elapsed': res.get('elapsed')
    }

print("=== REDIRECT TESTS ===")
print(json.dumps(redirect_results, indent=2))

# 2. Collect URLs from all sitemaps
all_urls = set()
sitemap_urls = [
    'https://gurupunvaanii.com/sitemap.xml',
    'https://gurupunvaanii.com/post-sitemap.xml',
    'https://gurupunvaanii.com/page-sitemap.xml',
    'https://gurupunvaanii.com/category-sitemap.xml'
]

sitemap_data = {}
for sm in sitemap_urls:
    res = fetch_url(sm)
    if res['status'] == 200:
        urls = re.findall(r'<loc>(.*?)</loc>', res['body'].decode('utf-8', errors='ignore'))
        sitemap_data[sm] = {
            'count': len(urls),
            'urls': urls,
            'headers': res['headers']
        }
        for u in urls:
            if not u.endswith('.xml'):
                all_urls.add(u)

print(f"Total Unique URLs found across sitemaps: {len(all_urls)}")

# 3. Crawl each page and analyze SEO
results = {}
images_inventory = []
broken_links = []
internal_links_graph = {}
external_links = set()

count = 0
for u in sorted(list(all_urls)):
    count += 1
    print(f"Crawling ({count}/{len(all_urls)}): {u}")
    res = fetch_url(u)
    if res['status'] != 200:
        results[u] = {
            'status': res['status'],
            'error': res['error'],
            'elapsed': res['elapsed']
        }
        continue

    html = res['body'].decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')

    # Title
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else ''

    # Meta Description
    meta_desc = soup.find('meta', attrs={'name': re.compile(r'^description$', re.I)})
    desc = meta_desc.get('content', '').strip() if meta_desc else ''

    # Robots meta
    meta_robots = soup.find('meta', attrs={'name': re.compile(r'^robots$', re.I)})
    robots_content = meta_robots.get('content', '').strip() if meta_robots else ''

    # Canonical
    canonical_tag = soup.find('link', rel='canonical')
    canonical = canonical_tag.get('href', '').strip() if canonical_tag else ''

    # Headings
    h1s = [h.get_text(strip=True) for h in soup.find_all('h1')]
    h2s = [h.get_text(strip=True) for h in soup.find_all('h2')]
    h3s = [h.get_text(strip=True) for h in soup.find_all('h3')]

    # Schemas
    json_lds = []
    for s in soup.find_all('script', type='application/ld+json'):
        try:
            txt = s.string or s.get_text()
            if txt:
                json_lds.append(json.loads(txt))
        except Exception as err:
            json_lds.append({'raw_error': str(err), 'raw_text': (s.string or '')[:200]})

    # OpenGraph & Twitter
    og_title = soup.find('meta', property='og:title')
    og_desc = soup.find('meta', property='og:description')
    og_image = soup.find('meta', property='og:image')
    og_type = soup.find('meta', property='og:type')
    tw_card = soup.find('meta', attrs={'name': 'twitter:card'})

    # Images
    page_images = []
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or ''
        alt = img.get('alt')
        width = img.get('width')
        height = img.get('height')
        loading = img.get('loading')
        page_images.append({
            'src': src,
            'alt': alt,
            'width': width,
            'height': height,
            'loading': loading
        })
        images_inventory.append({
            'page': u,
            'src': src,
            'alt': alt,
            'width': width,
            'height': height,
            'loading': loading
        })

    # Links
    page_internal_links = []
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        anchor_text = a.get_text(strip=True)
        full_url = urllib.parse.urljoin(u, href)
        parsed = urllib.parse.urlparse(full_url)
        
        if parsed.netloc in ['gurupunvaanii.com', 'www.gurupunvaanii.com']:
            clean_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
            page_internal_links.append({'url': clean_url, 'anchor': anchor_text})
        elif parsed.scheme in ['http', 'https']:
            external_links.add(full_url)

    internal_links_graph[u] = page_internal_links

    # Scripts and CSS
    scripts = [s.get('src') for s in soup.find_all('script', src=True)]
    stylesheets = [l.get('href') for l in soup.find_all('link', rel='stylesheet')]

    # Word count estimation
    text_content = soup.get_text(separator=' ', strip=True)
    words = len(text_content.split())

    results[u] = {
        'status': res['status'],
        'final_url': res['final_url'],
        'elapsed': round(res['elapsed'], 3),
        'size_bytes': len(res['body']),
        'title': title,
        'title_len': len(title),
        'meta_desc': desc,
        'meta_desc_len': len(desc),
        'meta_robots': robots_content,
        'x_robots_tag': res['headers'].get('X-Robots-Tag'),
        'canonical': canonical,
        'canonical_match': (canonical == u or canonical == u.rstrip('/') or canonical.rstrip('/') == u.rstrip('/')),
        'h1_count': len(h1s),
        'h1s': h1s,
        'h2_count': len(h2s),
        'h2s': h2s[:5],
        'h3_count': len(h3s),
        'word_count': words,
        'json_ld_count': len(json_lds),
        'json_ld_types': [j.get('@type') if isinstance(j, dict) else [item.get('@type') for item in j if isinstance(item, dict)] if isinstance(j, list) else None for j in json_lds],
        'og': {
            'title': og_title.get('content') if og_title else None,
            'desc': og_desc.get('content') if og_desc else None,
            'image': og_image.get('content') if og_image else None,
            'type': og_type.get('content') if og_type else None,
            'twitter_card': tw_card.get('content') if tw_card else None
        },
        'images_count': len(page_images),
        'images_missing_alt': len([img for img in page_images if img['alt'] is None or img['alt'] == '']),
        'internal_outlinks_count': len(page_internal_links),
        'scripts_count': len(scripts),
        'styles_count': len(stylesheets)
    }

# Save crawl results
audit_data = {
    'redirect_tests': redirect_results,
    'sitemap_data': {k: {'count': v['count']} for k, v in sitemap_data.items()},
    'total_crawled': len(results),
    'pages': results,
    'images_summary': {
        'total_images': len(images_inventory),
        'missing_alt': len([img for img in images_inventory if img['alt'] is None or img['alt'] == '']),
        'sample_missing_alt': [img for img in images_inventory if img['alt'] is None or img['alt'] == ''][:20]
    }
}

with open('audit_raw_data.json', 'w', encoding='utf-8') as f:
    json.dump(audit_data, f, indent=2, ensure_ascii=False)

print("Crawl complete! Saved to audit_raw_data.json")
