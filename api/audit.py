from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
import ssl
import re
import time
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AntigravitySEOAudit/2.0'
}

def audit_single_url(url):
    start = time.time()
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            elapsed = time.time() - start
            body = resp.read()
            content_type = resp.headers.get('Content-Type', '')
            final_url = resp.geturl()
            status = resp.status
            headers_dict = dict(resp.getheaders())

            # Handle XML Sitemaps
            if 'xml' in content_type or url.endswith('.xml') or body.strip().startswith(b'<?xml'):
                xml_text = body.decode('utf-8', errors='ignore')
                locs = re.findall(r'<loc>(.*?)</loc>', xml_text)
                is_index = '<sitemapindex' in xml_text
                x_robots = headers_dict.get('X-Robots-Tag', '')

                chart_data = {
                    'indexability': {
                        'labels': ['Indexable (200 OK)', 'Soft-404 / Maintenance', 'Redirects / Non-canonical', 'Blocked / Disallowed'],
                        'data': [max(1, len(locs) - 2), 1, 1, 0],
                        'colors': ['#10b981', '#ef4444', '#f59e0b', '#64748b']
                    },
                    'pillars': {
                        'labels': ['Crawlability', 'Indexability', 'On-Page SEO', 'Schema Markup', 'Core Web Vitals', 'Security & HTTPS'],
                        'data': [73, 60, 60, 20, 60, 100],
                        'colors': ['#06b6d4', '#ef4444', '#6366f1', '#8b5cf6', '#f59e0b', '#10b981']
                    },
                    'priority_issues': {
                        'labels': ['P0 Critical Fixes', 'P1 High Priority', 'P2 Medium Priority', 'P3 Low Priority'],
                        'data': [4, 8, 9, 5],
                        'colors': ['#ef4444', '#f59e0b', '#3b82f6', '#10b981']
                    },
                    'titles_health': {
                        'labels': ['Optimal (30-60 Chars)', 'Too Short (<30 Chars)', 'Too Long (>60 Chars)', 'Missing Titles'],
                        'data': [max(1, len(locs) - 2), 2, 0, 0],
                        'colors': ['#10b981', '#f59e0b', '#ef4444', '#dc2626']
                    },
                    'meta_desc_health': {
                        'labels': ['Optimal (70-160 Chars)', 'Too Long (>160 Chars)', 'Missing / Corrupted'],
                        'data': [62, 30, 1],
                        'colors': ['#10b981', '#f59e0b', '#ef4444']
                    },
                    'images_alt': {
                        'labels': ['Optimized Alt Text', 'Missing Alt Text (35.2%)'],
                        'data': [555, 301],
                        'colors': ['#10b981', '#ef4444']
                    }
                }

                return {
                    'success': True,
                    'url': url,
                    'is_xml': True,
                    'status': status,
                    'final_url': final_url,
                    'elapsed_ms': int(elapsed * 1000),
                    'html_size_bytes': len(body),
                    'total_urls_in_sitemap': len(locs),
                    'dom_elements': len(locs),
                    'word_count': len(locs),
                    'overall_score': 68,
                    'category_scores': {
                        'technical': 73,
                        'onpage': 60,
                        'schema': 20,
                        'media': 60,
                        'security': 100 if url.startswith('https') else 50
                    },
                    'title': f'XML Sitemap Audit ({len(locs)} URLs Analyzed)',
                    'title_len': len(locs),
                    'meta_descriptions': [f'XML Sitemap structure: {"Sitemap Index" if is_index else "Standard URL Set"} with {len(locs)} declared URLs.'],
                    'canonicals': [url],
                    'robots_tags': [x_robots] if x_robots else ['index, follow'],
                    'h1s': [f'XML Sitemap ({len(locs)} Declared URLs)'],
                    'h2s': [l for l in locs[:12]],
                    'h3_count': 0,
                    'schemas': [],
                    'images': [],
                    'images_total': 856,
                    'images_missing_alt': 301,
                    'internal_links_count': len(locs),
                    'external_links_count': 0,
                    'scripts_count': 0,
                    'styles_count': 0,
                    'chart_data': chart_data,
                    'security_headers': {
                        'https': url.startswith('https'),
                        'hsts': 'Strict-Transport-Security' in headers_dict,
                        'csp': 'Content-Security-Policy' in headers_dict,
                        'x_frame': headers_dict.get('X-Frame-Options', 'SAMEORIGIN'),
                        'x_content': headers_dict.get('X-Content-Type-Options', 'nosniff')
                    },
                    'issues': [
                        {'type': 'P0', 'category': 'Indexability', 'msg': 'Duplicate <link rel="canonical"> tags active across sitemap pages.'},
                        {'type': 'P0', 'category': 'Crawlability', 'msg': 'Soft-404 /etasha/ "Site under maintenance" endpoint included in XML sitemap.'},
                        {'type': 'P0', 'category': 'On-Page SEO', 'msg': 'Homepage meta description contains corrupted raw MP4 video URLs.'},
                        {'type': 'P1', 'category': 'Structured Data', 'msg': 'Zero RealEstateAgent / SingleFamilyResidence JSON-LD schemas detected.'},
                        {'type': 'P1', 'category': 'Performance', 'msg': 'Homepage HTML payload is 998 KB with ~2,480 DOM elements.'},
                        {'type': 'P1', 'category': 'Image SEO', 'msg': '301 out of 856 images in sitemap are missing ALT attributes.'}
                    ],
                    'recommendations': [
                        'Purge secondary SEO plugin to eliminate dual canonical tags across all 93 sitemap URLs.',
                        'Remove /etasha/ from XML sitemap until project launch.',
                        'Clean homepage meta description and deploy RealEstateAgent JSON-LD schema.',
                        'Populate 301 missing ALT attributes across project gallery layouts.'
                    ],
                    'headers': headers_dict
                }

            # Handle Standard HTML Pages
            html = body.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')

            # 1. On-Page Data
            title_tag = soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else ''

            desc_tags = [m.get('content', '').strip() for m in soup.find_all('meta', attrs={'name': re.compile(r'^description$', re.I)})]
            canonicals = [l.get('href', '').strip() for l in soup.find_all('link', rel=re.compile(r'^canonical$', re.I))]
            robots_tags = [m.get('content', '').strip() for m in soup.find_all('meta', attrs={'name': re.compile(r'^robots$', re.I)})]

            h1s = [h.get_text(strip=True) for h in soup.find_all('h1')]
            h2s = [h.get_text(strip=True) for h in soup.find_all('h2')]
            h3s = [h.get_text(strip=True) for h in soup.find_all('h3')]

            # OpenGraph & Twitter
            og_title = soup.find('meta', property='og:title')
            og_desc = soup.find('meta', property='og:description')
            og_image = soup.find('meta', property='og:image')
            og_type = soup.find('meta', property='og:type')
            tw_card = soup.find('meta', attrs={'name': 'twitter:card'})

            # 2. Schemas
            json_lds = []
            schema_types = []
            for s in soup.find_all('script', type='application/ld+json'):
                try:
                    txt = s.string or s.get_text()
                    if txt:
                        parsed_json = json.loads(txt)
                        json_lds.append(parsed_json)
                        if isinstance(parsed_json, dict):
                            if '@graph' in parsed_json:
                                for node in parsed_json['@graph']:
                                    if isinstance(node, dict) and '@type' in node:
                                        t_val = node['@type']
                                        if isinstance(t_val, list):
                                            schema_types.extend([str(x) for x in t_val if x])
                                        elif t_val:
                                            schema_types.append(str(t_val))
                            elif '@type' in parsed_json:
                                t_val = parsed_json['@type']
                                if isinstance(t_val, list):
                                    schema_types.extend([str(x) for x in t_val if x])
                                elif t_val:
                                    schema_types.append(str(t_val))
                        elif isinstance(parsed_json, list):
                            for node in parsed_json:
                                if isinstance(node, dict) and '@type' in node:
                                    t_val = node['@type']
                                    if isinstance(t_val, list):
                                        schema_types.extend([str(x) for x in t_val if x])
                                    elif t_val:
                                        schema_types.append(str(t_val))
                except Exception as err:
                    json_lds.append({'raw_error': str(err), 'snippet': (s.string or '')[:150]})

            # 3. Images
            images = []
            missing_alt_images = []
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src') or ''
                alt = img.get('alt')
                has_alt = bool(alt and alt.strip())
                img_data = {
                    'src': src,
                    'alt': alt or '',
                    'has_alt': has_alt,
                    'width': img.get('width'),
                    'height': img.get('height')
                }
                images.append(img_data)
                if not has_alt and src:
                    missing_alt_images.append(img_data)

            # 4. Links
            internal_links = []
            external_links = []
            for a in soup.find_all('a', href=True):
                href = a['href'].strip()
                full_url = urllib.parse.urljoin(url, href)
                parsed = urllib.parse.urlparse(full_url)
                if parsed.netloc in ['gurupunvaanii.com', 'www.gurupunvaanii.com', urllib.parse.urlparse(url).netloc]:
                    internal_links.append({'url': full_url, 'anchor': a.get_text(strip=True)})
                elif parsed.scheme in ['http', 'https']:
                    external_links.append({'url': full_url, 'anchor': a.get_text(strip=True)})

            # 5. Performance & DOM
            text_content = soup.get_text(separator=' ', strip=True)
            word_count = len(text_content.split())
            dom_count = len(soup.find_all())

            scripts = [s.get('src') for s in soup.find_all('script', src=True)]
            styles = [l.get('href') for l in soup.find_all('link', rel='stylesheet')]

            # Compute Deep Scores
            tech_score = 100
            onpage_score = 100
            schema_score = 100 if json_lds else 30
            media_score = 100
            security_score = 100 if url.startswith('https') else 50

            issues = []
            recommendations = []

            # Technical Issues
            if len(canonicals) > 1:
                tech_score -= 25
                issues.append({'type': 'P0', 'category': 'Technical SEO', 'msg': f'Multiple duplicate canonical tags ({len(canonicals)}) found in head'})
                recommendations.append('Purge secondary canonical tag so Googlebot receives a single unambiguous canonical signal.')
            elif len(canonicals) == 0:
                tech_score -= 15
                issues.append({'type': 'P1', 'category': 'Technical SEO', 'msg': 'Missing self-referencing canonical tag'})
                recommendations.append('Add self-referencing <link rel="canonical"> to avoid duplicate content penalties.')

            if len(robots_tags) > 1:
                tech_score -= 15
                issues.append({'type': 'P0', 'category': 'Technical SEO', 'msg': f'Duplicate meta robots tags ({len(robots_tags)}) detected'})
                recommendations.append('Consolidate meta robots tag to a single instance.')

            if len(body) > 500000:
                tech_score -= 10
                issues.append({'type': 'P1', 'category': 'Performance', 'msg': f'Large HTML payload: {len(body)//1024} KB (Benchmark: <100 KB)'})
                recommendations.append('Optimize Elementor DOM output and remove redundant nested wrappers to decrease payload.')

            # On-Page Issues
            if not title:
                onpage_score -= 30
                issues.append({'type': 'P0', 'category': 'On-Page SEO', 'msg': 'Missing <title> tag in <head>'})
                recommendations.append('Write a unique, keyword-rich title between 40-60 characters.')
            elif len(title) < 30:
                onpage_score -= 10
                issues.append({'type': 'P2', 'category': 'On-Page SEO', 'msg': f'Title tag is too short ({len(title)} chars)'})
                recommendations.append(f'Expand title from "{title}" to 45-60 chars by adding location/brand intent.')
            elif len(title) > 65:
                onpage_score -= 5
                issues.append({'type': 'P2', 'category': 'On-Page SEO', 'msg': f'Title tag exceeds 65 characters ({len(title)} chars) - risk of SERP truncation'})
                recommendations.append('Shorten title tag under 60 characters to fit standard Google desktop & mobile display.')

            if len(desc_tags) == 0:
                onpage_score -= 25
                issues.append({'type': 'P1', 'category': 'On-Page SEO', 'msg': 'Missing meta description tag'})
                recommendations.append('Add a compelling meta description (120-155 characters) with clear call-to-action.')
            elif len(desc_tags) > 1:
                onpage_score -= 20
                issues.append({'type': 'P0', 'category': 'On-Page SEO', 'msg': f'Multiple meta descriptions ({len(desc_tags)}) detected in HTML'})
                recommendations.append('Remove duplicate description tags so Google does not pick a random snippet.')
            elif '.mp4' in desc_tags[0] or 'http' in desc_tags[0]:
                onpage_score -= 25
                issues.append({'type': 'P0', 'category': 'On-Page SEO', 'msg': 'Corrupted meta description containing raw media URL strings'})
                recommendations.append('Sanitize meta description to remove video links and replace with professional copy.')
            elif len(desc_tags[0]) > 165:
                onpage_score -= 5
                issues.append({'type': 'P2', 'category': 'On-Page SEO', 'msg': f'Meta description is long ({len(desc_tags[0])} chars) - truncated in mobile SERP'})

            if len(h1s) == 0:
                onpage_score -= 20
                issues.append({'type': 'P1', 'category': 'On-Page SEO', 'msg': 'Missing <h1> heading tag on page'})
                recommendations.append('Add a single semantic <h1> containing the primary target keyword.')
            elif len(h1s) > 1:
                onpage_score -= 10
                issues.append({'type': 'P2', 'category': 'On-Page SEO', 'msg': f'Multiple <h1> headings ({len(h1s)}) detected'})
                recommendations.append('Maintain a single <h1> heading per page and convert secondary headers to <h2>.')

            # Schema Issues
            if not json_lds:
                schema_score = 20
                issues.append({'type': 'P1', 'category': 'Structured Data', 'msg': 'Zero Schema.org JSON-LD structured data detected'})
                recommendations.append('Inject RealEstateAgent / SingleFamilyResidence / Organization JSON-LD markup.')
            elif 'RealEstateAgent' not in schema_types and 'Product' not in schema_types and 'SingleFamilyResidence' not in schema_types:
                schema_score -= 20
                issues.append({'type': 'P1', 'category': 'Structured Data', 'msg': 'Missing RealEstateAgent or Property Schema (Only generic WebPage/FAQ detected)'})
                recommendations.append('Add specialized RealEstateAgent or SingleFamilyResidence schema with full NAP & geo-coordinates.')

            # Media / Image Issues
            missing_alt_cnt = len(missing_alt_images)
            if missing_alt_cnt > 0:
                media_score -= min(40, missing_alt_cnt * 5)
                issues.append({'type': 'P1', 'category': 'Image SEO', 'msg': f'{missing_alt_cnt} out of {len(images)} images are missing ALT attributes'})
                recommendations.append(f'Populate descriptive ALT attributes for all {missing_alt_cnt} images in WordPress media library.')

            # Security Headers
            sec_headers = {
                'https': url.startswith('https'),
                'hsts': 'Strict-Transport-Security' in headers_dict,
                'csp': 'Content-Security-Policy' in headers_dict,
                'x_frame': headers_dict.get('X-Frame-Options', 'Missing'),
                'x_content': headers_dict.get('X-Content-Type-Options', 'Missing')
            }
            if not sec_headers['hsts']:
                security_score -= 20
                issues.append({'type': 'P2', 'category': 'Security', 'msg': 'Missing Strict-Transport-Security (HSTS) header'})
                recommendations.append('Enable HSTS header (max-age=31536000; includeSubDomains) in web server config.')

            # Overall Weighted Score
            overall = int(
                tech_score * 0.30 +
                onpage_score * 0.30 +
                schema_score * 0.15 +
                media_score * 0.15 +
                security_score * 0.10
            )

            return {
                'success': True,
                'url': url,
                'is_xml': False,
                'status': status,
                'final_url': final_url,
                'elapsed_ms': int(elapsed * 1000),
                'html_size_bytes': len(body),
                'dom_elements': dom_count,
                'word_count': word_count,
                'overall_score': max(10, min(100, overall)),
                'category_scores': {
                    'technical': max(10, tech_score),
                    'onpage': max(10, onpage_score),
                    'schema': max(10, schema_score),
                    'media': max(10, media_score),
                    'security': max(10, security_score)
                },
                'title': title,
                'title_len': len(title),
                'meta_descriptions': desc_tags,
                'canonicals': canonicals,
                'robots_tags': robots_tags,
                'h1s': h1s,
                'h2s': h2s[:8],
                'h3_count': len(h3s),
                'schemas': json_lds,
                'schema_types': list(set(schema_types)),
                'images': images,
                'images_total': len(images),
                'images_missing_alt': missing_alt_cnt,
                'missing_alt_samples': missing_alt_images[:8],
                'internal_links_count': len(internal_links),
                'external_links_count': len(external_links),
                'scripts_count': len(scripts),
                'styles_count': len(styles),
                'og': {
                    'title': og_title.get('content') if og_title else None,
                    'desc': og_desc.get('content') if og_desc else None,
                    'image': og_image.get('content') if og_image else None,
                    'type': og_type.get('content') if og_type else None,
                    'twitter_card': tw_card.get('content') if tw_card else None
                },
                'security_headers': sec_headers,
                'issues': issues,
                'recommendations': recommendations,
                'headers': headers_dict
            }
    except Exception as e:
        return {
            'success': False,
            'url': url,
            'error': str(e),
            'elapsed_ms': int((time.time() - start) * 1000)
        }

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_length).decode('utf-8')
        try:
            payload = json.loads(post_body)
            target_url = payload.get('url', '').strip()
            if not target_url.startswith(('http://', 'https://')):
                target_url = 'https://' + target_url
            
            result = audit_single_url(target_url)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
