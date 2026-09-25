// Joanne Amelie SANITO - Skater Progress Application Logic

let skaterAppState = {
  data: null,
  activeMetric: 'totalScore',
  activeCategory: 'all',
  chartInstance: null
};

// Initialize App
document.addEventListener('DOMContentLoaded', async () => {
  try {
    const res = await fetch(`data/skater-data.json?v=${Date.now()}`);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    skaterAppState.data = data;

    renderHeroStats(data);
    setupChart(data);
    renderCategoryFilters(data);
    renderCompetitionsList(data);
    setupEventListeners();
  } catch (err) {
    console.error('Failed to load skater data:', err);
    document.getElementById('competitionsList').innerHTML = `
      <div style="text-align: center; padding: 40px; color: #f87171;">
        <p>⚠️ Could not load <code>data/skater-data.json</code>.</p>
        <p style="font-size: 0.85rem; color: #94a3b8; margin-top: 8px;">Ensure you have run the results parser or are accessing via a local web server.</p>
      </div>
    `;
  }
});

// Render Header & Highlights
function renderHeroStats(data) {
  const { skater, records, competitions } = data;

  document.getElementById('currentCategory').textContent = skater.currentCategory || 'Novice Girls B1';
  document.getElementById('pbTotal').textContent = records.personalBestTotal.toFixed(2);
  document.getElementById('pbTES').textContent = records.personalBestTES.toFixed(2);

  // Find competition where PB Total was achieved
  const pbComp = competitions.find(c => c.totalScore === records.personalBestTotal);
  if (pbComp) {
    document.getElementById('pbEvent').textContent = `${pbComp.competition} (${pbComp.date.split('-')[0]})`;
  }

  document.getElementById('goldCount').textContent = records.medals.gold;
  document.getElementById('silverCount').textContent = records.medals.silver;
  document.getElementById('bronzeCount').textContent = records.medals.bronze;
  document.getElementById('totalEvents').textContent = records.totalEvents;

  // Best Solo Jump
  const soloJump = records.bestSoloJump || records.bestJump;
  if (soloJump && document.getElementById('bestSoloJumpCode')) {
    document.getElementById('bestSoloJumpCode').textContent = soloJump.code;
    document.getElementById('bestSoloJumpScore').textContent = soloJump.score.toFixed(2);
    document.getElementById('bestSoloJumpDetail').textContent = `Score: ${soloJump.score.toFixed(2)} pts (${soloJump.competition})`;
  }

  // Best Combo Jump
  if (records.bestCombo && document.getElementById('bestComboCode')) {
    document.getElementById('bestComboCode').textContent = records.bestCombo.code;
    document.getElementById('bestComboScore').textContent = records.bestCombo.score.toFixed(2);
    document.getElementById('bestComboDetail').textContent = `Score: ${records.bestCombo.score.toFixed(2)} pts (${records.bestCombo.competition})`;
  }

  // Best Spin
  if (records.bestSpin && document.getElementById('bestSpinCode')) {
    document.getElementById('bestSpinCode').textContent = records.bestSpin.code;
    document.getElementById('bestSpinScore').textContent = records.bestSpin.score.toFixed(2);
    document.getElementById('bestSpinDetail').textContent = `Score: ${records.bestSpin.score.toFixed(2)} pts (${records.bestSpin.competition})`;
  }

  // Best Step Sequence
  if (records.bestStepSeq && document.getElementById('bestStepCode')) {
    document.getElementById('bestStepCode').textContent = records.bestStepSeq.code;
    document.getElementById('bestStepScore').textContent = records.bestStepSeq.score.toFixed(2);
    document.getElementById('bestStepDetail').textContent = `Score: ${records.bestStepSeq.score.toFixed(2)} pts (${records.bestStepSeq.competition})`;
  }
}

// Chart.js Setup & Interactive Controls
function setupChart(data) {
  const ctx = document.getElementById('progressionChart').getContext('2d');
  const comps = data.competitions;

  const labels = comps.map(c => {
    const year = c.date.split('-')[0];
    const shortComp = c.competition.replace('KONKURRENCE', 'KONK.').replace('KONKURRENCEN', 'KONK.');
    return `${shortComp} ('${year.slice(2)})`;
  });

  const getMetricData = (metric) => comps.map(c => c[metric]);

  const gradient = ctx.createLinearGradient(0, 0, 0, 300);
  gradient.addColorStop(0, 'rgba(56, 189, 248, 0.45)');
  gradient.addColorStop(1, 'rgba(56, 189, 248, 0.0)');

  skaterAppState.chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Total Score',
        data: getMetricData('totalScore'),
        borderColor: '#38bdf8',
        backgroundColor: gradient,
        borderWidth: 3,
        fill: true,
        tension: 0.35,
        pointBackgroundColor: '#fff',
        pointBorderColor: '#38bdf8',
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(7, 13, 30, 0.95)',
          titleFont: { family: 'Outfit', size: 14, weight: '700' },
          bodyFont: { family: 'Inter', size: 12 },
          borderColor: 'rgba(56, 189, 248, 0.3)',
          borderWidth: 1,
          padding: 12,
          callbacks: {
            title: (items) => {
              const idx = items[0].dataIndex;
              return comps[idx].competition;
            },
            label: (item) => {
              const comp = comps[item.dataIndex];
              const rankIcon = comp.rank === 1 ? '🥇' : comp.rank === 2 ? '🥈' : comp.rank === 3 ? '🥉' : `#${comp.rank}`;
              return [
                ` Category: ${comp.category}`,
                ` Rank: ${rankIcon} (${comp.rank || 'N/A'})`,
                ` Total Score: ${comp.totalScore.toFixed(2)} pts`,
                ` Elements (TES): ${comp.tes.toFixed(2)} | Components (PCS): ${comp.pcs.toFixed(2)}`
              ];
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
        },
        y: {
          min: 0,
          max: 28,
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: {
            color: '#94a3b8',
            font: { family: 'Inter', size: 11 },
            callback: (val) => `${val} pts`
          }
        }
      }
    }
  });
}

// Category Filter Pills
function renderCategoryFilters(data) {
  const container = document.getElementById('categoryFilters');
  const categories = [...new Set(data.competitions.map(c => c.category))];

  categories.forEach(cat => {
    const btn = document.createElement('button');
    btn.className = 'filter-pill';
    btn.dataset.filter = cat;
    
    // Shorten category label for pills
    let label = cat.replace('FREE SKATING', '').replace('PIGER OG DRENGE', '').replace('GIRLS AND BOYS', '').replace('MIXED', '').trim();
    const count = data.competitions.filter(c => c.category === cat).length;
    btn.textContent = `${label} (${count})`;
    container.appendChild(btn);
  });
}

// Render Expandable Competition Cards
function renderCompetitionsList(data) {
  const container = document.getElementById('competitionsList');
  container.innerHTML = '';

  const filtered = skaterAppState.activeCategory === 'all'
    ? data.competitions
    : data.competitions.filter(c => c.category === skaterAppState.activeCategory);

  // Show newest competitions first
  const displayComps = [...filtered].reverse();

  displayComps.forEach((comp, idx) => {
    const card = document.createElement('div');
    card.className = 'comp-card';
    card.dataset.id = comp.sourceFile;

    // Rank styling
    let rankBadgeClass = 'standard';
    let rankText = `#${comp.rank || 'N/A'}`;
    if (comp.rank === 1) { rankBadgeClass = 'gold'; rankText = '🥇 1'; }
    else if (comp.rank === 2) { rankBadgeClass = 'silver'; rankText = '🥈 2'; }
    else if (comp.rank === 3) { rankBadgeClass = 'bronze'; rankText = '🥉 3'; }

    // Elements Rows
    // Generate PCS component rows
    const pcsRows = comp.pcsDetails && comp.pcsDetails.components && comp.pcsDetails.components.length > 0
      ? comp.pcsDetails.components.map(c => {
          const judgesStr = c.judges && c.judges.length > 0 ? c.judges.map(j => j.toFixed(2)).join(', ') : '—';
          return `
            <tr>
              <td style="font-weight: 600; color: #fff;">${c.component}</td>
              <td style="color: var(--text-muted);">${c.factor.toFixed(2)}</td>
              <td style="color: var(--text-muted); font-size: 0.78rem;">${judgesStr}</td>
              <td style="font-weight: 700; color: #22d3ee;">${c.score.toFixed(2)}</td>
            </tr>
          `;
        }).join('')
      : `<tr><td colspan="4" style="text-align: center; color: #94a3b8; padding: 14px;">PCS total: ${comp.pcs.toFixed(2)} (component breakdown not itemized in protocol)</td></tr>`;

    const deductionsHtml = (comp.deductions && comp.deductions > 0)
      ? `<div class="deductions-note">⚠️ Deductions: -${comp.deductions.toFixed(2)} (${(comp.pcsDetails && comp.pcsDetails.deductionsDetail) || 'Falls / Violations'})</div>`
      : '';

    const elementsRows = comp.elements && comp.elements.length > 0
      ? comp.elements.map(el => {
          let goeClass = 'goe-neutral';
          let goePrefix = '';
          if (el.goe > 0) { goeClass = 'goe-positive'; goePrefix = '+'; }
          else if (el.goe < 0) { goeClass = 'goe-negative'; }

          let typeBadge = `<span class="badge-el-type badge-${el.type}">${el.type}</span>`;

          return `
            <tr>
              <td>#${el.number}</td>
              <td style="font-weight: 600; color: #fff;">${el.code}</td>
              <td>${typeBadge}</td>
              <td>${el.baseValue.toFixed(2)}</td>
              <td class="${goeClass}">${goePrefix}${el.goe.toFixed(2)}</td>
              <td style="font-weight: 700; color: #38bdf8;">${el.score.toFixed(2)}</td>
            </tr>
          `;
        }).join('')
      : `<tr><td colspan="6" style="text-align: center; color: #94a3b8; padding: 20px;">Element breakdown recorded in summary sheet.</td></tr>`;

    card.innerHTML = `
      <div class="comp-card-header">
        <div class="comp-info">
          <div class="comp-rank-badge ${rankBadgeClass}">${rankText}</div>
          <div>
            <div class="comp-title">${comp.competition}</div>
            <div class="comp-subtitle">
              <span>📅 ${comp.date}</span>
              <span>•</span>
              <span>🏷️ ${comp.category}</span>
            </div>
          </div>
        </div>

        <div class="comp-scores">
          <div class="score-box">
            <div class="score-total">${comp.totalScore.toFixed(2)}</div>
            <div class="score-breakdown">TES: ${comp.tes.toFixed(2)} | PCS: ${comp.pcs.toFixed(2)}</div>
          </div>
          <div class="expand-chevron">▼</div>
        </div>
      </div>

      <div class="comp-details">
        <div class="comp-details-grid">
          <!-- Technical Elements Score (TES) Breakdown -->
          <div class="details-section">
            <div class="details-section-title">
              <span>Technical Elements (TES)</span>
              <span class="section-score-tag tes-tag">${comp.tes.toFixed(2)} pts</span>
            </div>
            <div class="elements-table-container">
              <table class="elements-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Element</th>
                    <th>Type</th>
                    <th>BV</th>
                    <th>GOE</th>
                    <th>Score</th>
                  </tr>
                </thead>
                <tbody>
                  ${elementsRows}
                </tbody>
              </table>
            </div>
          </div>

          <!-- Program Component Score (PCS) Breakdown -->
          <div class="details-section">
            <div class="details-section-title">
              <span>Program Components (PCS)</span>
              <span class="section-score-tag pcs-tag">${comp.pcs.toFixed(2)} pts</span>
            </div>
            <div class="elements-table-container">
              <table class="elements-table">
                <thead>
                  <tr>
                    <th>Component</th>
                    <th>Factor</th>
                    <th>Judges</th>
                    <th>Score</th>
                  </tr>
                </thead>
                <tbody>
                  ${pcsRows}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        ${deductionsHtml}
      </div>
    `;

    // Toggle Accordion Click
    const header = card.querySelector('.comp-card-header');
    header.addEventListener('click', () => {
      card.classList.toggle('expanded');
    });

    container.appendChild(card);
  });
}

// UI Event Listeners
function setupEventListeners() {
  // Chart Metric Toggles
  document.querySelectorAll('.toggle-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');

      const metric = e.target.dataset.metric;
      skaterAppState.activeMetric = metric;

      const chart = skaterAppState.chartInstance;
      if (chart && skaterAppState.data) {
        chart.data.datasets[0].data = skaterAppState.data.competitions.map(c => c[metric]);
        
        let label = 'Total Score';
        let color = '#38bdf8';
        if (metric === 'tes') { label = 'Technical Elements (TES)'; color = '#a855f7'; }
        if (metric === 'pcs') { label = 'Program Components (PCS)'; color = '#06b6d4'; }

        chart.data.datasets[0].label = label;
        chart.data.datasets[0].borderColor = color;
        chart.data.datasets[0].pointBorderColor = color;
        chart.update();
      }
    });
  });

  // Category Filter Pills
  document.getElementById('categoryFilters').addEventListener('click', (e) => {
    if (e.target.classList.contains('filter-pill')) {
      document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
      e.target.classList.add('active');

      skaterAppState.activeCategory = e.target.dataset.filter;
      renderCompetitionsList(skaterAppState.data);
    }
  });
}
