const form = document.querySelector('#recommend-form');
const dateInput = document.querySelector('#travel-date');
const styleInput = document.querySelector('#travel-style');
const submitButton = document.querySelector('#submit-button');
const formMessage = document.querySelector('#form-message');
const resultTitle = document.querySelector('#result-title');
const resultBadge = document.querySelector('#result-badge');
const resultContent = document.querySelector('#result-content');
const menuToggle = document.querySelector('.menu-toggle');
const siteNav = document.querySelector('#site-nav');

const today = new Date();
const localDate = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
dateInput.value = localDate;

document.querySelectorAll('.site-nav a').forEach((link) => {
  link.addEventListener('click', () => siteNav.classList.remove('open'));
});

menuToggle.addEventListener('click', () => {
  const open = siteNav.classList.toggle('open');
  menuToggle.setAttribute('aria-expanded', String(open));
});

function setMessage(message = '', type = '') {
  formMessage.textContent = message;
  formMessage.className = `form-message ${type}`.trim();
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function renderResult(data) {
  const cities = Array.isArray(data.recommended_cities) ? data.recommended_cities : [];
  const reason = data.reason || '추천 이유가 제공되지 않았습니다.';
  const weather = data.weather || '날씨 정보가 제공되지 않았습니다.';
  const events = Array.isArray(data.events) ? data.events : [];
  const itinerary = data.itinerary && typeof data.itinerary === 'object' ? data.itinerary : {};

  resultTitle.textContent = cities.length ? cities.join(' · ') : 'AI 추천 결과';
  resultBadge.textContent = '완료';
  resultContent.className = 'result-content';

  const cityCards = cities.map((city, index) => `
    <article class="city-card">
      <h4>${index + 1}. ${escapeHtml(city)}</h4>
      <p>${escapeHtml(weather)}</p>
    </article>
  `).join('');

  const eventList = events.length
    ? events.map((item) => `<li>${escapeHtml(item)}</li>`).join('')
    : '<li>행사 정보가 없습니다.</li>';

  const dayPlan = ['morning', 'afternoon', 'evening']
    .map((key, index) => {
      const label = ['오전', '오후', '저녁'][index];
      const text = itinerary[key] || '세부 일정은 여행지 상황에 맞게 조정하세요.';
      return `<li><strong>${label}</strong> ${escapeHtml(text)}</li>`;
    }).join('');

  resultContent.innerHTML = `
    <div class="city-grid">${cityCards}</div>
    <div class="reason-box"><strong>추천 이유</strong><span>${escapeHtml(reason)}</span></div>
    <div class="itinerary-box">
      <strong>하루 여행 예시</strong>
      <ul>${dayPlan}</ul>
      <strong>볼거리</strong>
      <ul>${eventList}</ul>
    </div>
  `;
}

async function requestRecommendation(payload) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 18000);

  try {
    const response = await fetch('/api/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.error || 'AI 추천 요청에 실패했습니다.');
    }
    return data;
  } finally {
    clearTimeout(timer);
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  setMessage('AI가 여행지를 고르고 있어요. 잠시만 기다려 주세요.', '');
  submitButton.disabled = true;
  resultBadge.textContent = '처리 중';
  resultTitle.textContent = 'AI가 여행 계획을 만드는 중…';

  const date = dateInput.value.trim();
  const style = styleInput.value.trim();

  if (!date || !style) {
    setMessage('여행 날짜와 여행 스타일을 모두 입력해 주세요.', 'error');
    resultBadge.textContent = '입력 필요';
    submitButton.disabled = false;
    return;
  }

  try {
    const data = await requestRecommendation({ date, style });
    renderResult(data);
    setMessage('추천 결과가 완성됐어요.', 'success');
    document.querySelector('#recommend').scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (error) {
    if (error.name === 'AbortError') {
      setMessage('응답이 늦어지고 있어요. 잠시 후 다시 시도해 주세요.', 'error');
    } else {
      setMessage(error.message || 'AI 추천 중 문제가 발생했습니다.', 'error');
    }
    resultBadge.textContent = '오류';
    resultTitle.textContent = '추천 결과를 불러오지 못했습니다.';
    resultContent.className = 'result-content empty-state';
    resultContent.innerHTML = '<p>잠시 후 다시 시도해 주세요.</p>';
  } finally {
    submitButton.disabled = false;
  }
});
