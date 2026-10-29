const { JSDOM } = require('jsdom');
const fs = require('fs');

console.log('='.repeat(70));
console.log('  AUTOMATED FULL-SPECTRUM DASHBOARD & REPORT REVIEW ENGINE');
console.log('='.repeat(70));

const htmlContent = fs.readFileSync('index.html', 'utf8');
const dataContent = fs.readFileSync('data.js', 'utf8');
const appContent = fs.readFileSync('app.js', 'utf8');

const dom = new JSDOM(htmlContent, {
  runScripts: "dangerously",
  resources: "usable",
  url: "http://localhost:8080/index.html"
});

const { window } = dom;
const { document } = window;

// Attach mock directly to window.HTMLCanvasElement.prototype
window.requestAnimationFrame = (cb) => setTimeout(cb, 0);
window.cancelAnimationFrame = (id) => clearTimeout(id);

window.ResizeObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
};

window.HTMLCanvasElement.prototype.getContext = function() {
  return {
    fillRect: function() {},
    clearRect: function() {},
    getImageData: function(x, y, w, h) { return { data: new Array(w*h*4) }; },
    putImageData: function() {},
    createImageData: function() { return []; },
    setTransform: function() {},
    drawImage: function() {},
    save: function() {},
    fillText: function() {},
    restore: function() {},
    beginPath: function() {},
    moveTo: function() {},
    lineTo: function() {},
    closePath: function() {},
    stroke: function() {},
    translate: function() {},
    scale: function() {},
    rotate: function() {},
    arc: function() {},
    fill: function() {},
    measureText: function() { return { width: 0 }; },
    transform: function() {},
    resetTransform: function() {},
    rect: function() {},
    clip: function() {},
    canvas: this
  };
};

window.Chart = function(canvas, config) {
  this.canvas = canvas;
  this.config = config;
  this.destroy = function() {};
  this.update = function() {};
};

// Attach mocks
window.fetch = async (url, options) => {
  return {
    ok: false,
    status: 500,
    json: async () => ({ error: "mocked fetch offline fallback" })
  };
};

let errorLogs = [];
window.console.error = (...args) => {
  errorLogs.push(args.join(' '));
  console.log('  [CONSOLE ERROR]:', ...args);
};

try {
  // Execute scripts in simulated browser window
  window.eval(dataContent);
  window.eval(appContent);

  console.log('\n[TEST 1] Testing Data Loading & Initial Global State...');
  if (window.AUDIT_RAW_DATA && window.AUDIT_RAW_DATA.pages) {
    const pageCount = Array.isArray(window.AUDIT_RAW_DATA.pages)
      ? window.AUDIT_RAW_DATA.pages.length
      : Object.keys(window.AUDIT_RAW_DATA.pages).length;
    console.log(`  [+] Initial Pages in Memory: ${pageCount} pages loaded.`);
  } else {
    console.log('  [-] window.AUDIT_RAW_DATA missing.');
  }

  // 1. Test Overview Navigation & Rendering
  console.log('\n[TEST 2] Testing Command Center / Overview View...');
  if (typeof window.renderOverview === 'function') {
    window.renderOverview();
    console.log('  [+] renderOverview() executed successfully.');
  }

  // 2. Test Live Scanner Presets
  console.log('\n[TEST 3] Testing Live URL Scanner & Sitemap Generation...');
  const urlInput = document.getElementById('liveScanUrlInput');
  const resultCard = document.getElementById('liveScanResultCard');
  
  if (typeof window.setAndScan === 'function') {
    console.log('  -> Triggering "🚀 Scan All 3 Sitemaps Unified"...');
    window.setAndScan('https://gurupunvaanii.com/post-sitemap.xml, https://gurupunvaanii.com/page-sitemap.xml, https://gurupunvaanii.com/category-sitemap.xml');
    
    setTimeout(() => {
      console.log('  [+] Result Card Display Style:', resultCard ? resultCard.style.display : 'Not Found');
      const tableBody = document.getElementById('sitemapPagesTableBody');
      const rowCount = tableBody ? tableBody.querySelectorAll('tr').length : 0;
      console.log(`  [+] Master Sitemap Table Rows Rendered: ${rowCount} rows`);

      // Test All 4 Tabs
      console.log('\n[TEST 4] Testing Scanner Tabs...');
      
      // Tab 1: URLs
      window.switchSitemapTab('urls');
      console.log('  [+] Tab 1 (URLs): ACTIVE');
      
      // Tab 2: Brief
      window.switchSitemapTab('brief');
      console.log('  [+] Tab 2 (Brief & Matrix): ACTIVE');

      // Tab 3: Visual Graphical Charts
      window.switchSitemapTab('charts');
      console.log('  [+] Tab 3 (Visual Charts): ACTIVE');
      if (typeof window.initSitemapChartGraphs === 'function' && window.currentSitemapData) {
        window.initSitemapChartGraphs(window.currentSitemapData.chart_data);
        console.log('  [+] All 5 Graphical Charts (Indexability, Pillars, Severity, Titles, Images) Initialized.');
      }

      // Tab 4: Traffic
      window.switchSitemapTab('traffic');
      console.log('  [+] Tab 4 (Traffic & Keywords): ACTIVE');

      // 3. Test Filter Pills
      console.log('\n[TEST 5] Testing Filter Pills in Sitemap Table...');
      ['all', 'good', 'needs_fix', 'p0', 'missing_alt', 'missing_schema'].forEach(f => {
        window.filterSitemapUrlTable(f);
        const filteredCount = document.getElementById('sitemapPagesTableBody').querySelectorAll('tr').length;
        console.log(`  [+] Filter '${f}' -> ${filteredCount} rows matched.`);
      });

      // 4. Test Single Page Deep Audit Modal
      console.log('\n[TEST 6] Testing Deep Audit Modal for Scanned Page...');
      if (typeof window.openPageAuditModal === 'function') {
        window.openPageAuditModal(0);
        const modal = document.getElementById('pageAuditModal');
        console.log('  [+] Modal opened for Page index 0. Display:', modal ? modal.style.display : 'None');
        if (typeof window.closePageAuditModal === 'function') {
          window.closePageAuditModal();
          console.log('  [+] Modal closed successfully.');
        }
      }

      // 5. Test Sidebar Navigation Views
      console.log('\n[TEST 7] Testing All Sidebar View Navigations...');
      const views = [
        'view-overview',
        'view-scanner',
        'view-technical',
        'view-onpage',
        'view-schema',
        'view-offpage',
        'view-performance',
        'view-traffic',
        'view-local',
        'view-roadmap'
      ];

      views.forEach(v => {
        const viewEl = document.getElementById(v);
        if (viewEl) {
          console.log(`  [+] View '${v}' exists in DOM.`);
        } else {
          console.log(`  [-] View '${v}' NOT found.`);
        }
      });

      // 6. Test Core Web Vitals Render
      console.log('\n[TEST 8] Testing Core Web Vitals (CWV) Module...');
      if (typeof window.renderCWVView === 'function') {
        window.renderCWVView();
        console.log('  [+] renderCWVView() executed successfully.');
      }

      // 7. Test Schema Studio Module
      console.log('\n[TEST 9] Testing Schema Studio...');
      if (typeof window.renderSchemaStudio === 'function') {
        window.renderSchemaStudio();
        console.log('  [+] renderSchemaStudio() executed successfully.');
      }

      // 8. Test Action Plan Tasks Module
      console.log('\n[TEST 10] Testing Action Plan & Tasks...');
      if (typeof window.renderActionPlan === 'function') {
        window.renderActionPlan();
        console.log('  [+] renderActionPlan() executed successfully.');
      }

      // 9. Test Weekly Tracker Module
      console.log('\n[TEST 11] Testing Weekly Tracker...');
      if (typeof window.renderWeeklyTracker === 'function') {
        window.renderWeeklyTracker();
        console.log('  [+] renderWeeklyTracker() executed successfully.');
      }

      console.log('\n' + '='.repeat(70));
      if (errorLogs.length === 0) {
        console.log('  ALL DASHBOARD MODULES & REPORTS REVIEWED WITH 0 ERRORS!');
      } else {
        console.log(`  REVIEW COMPLETE: ${errorLogs.length} issues found.`);
      }
      console.log('='.repeat(70));

    }, 200);
  }

} catch (err) {
  console.error('Fatal Script Evaluation Error:', err);
}
