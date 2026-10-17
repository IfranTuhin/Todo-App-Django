/**
 * TaskFlow / Todo App - Client Scripting & Interactive Animation Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initToasts();
  initAjaxTaskToggles();
  initLiveSearch();
  initKeyboardShortcuts();
});

/* ===================================================================
   1. Theme Management (Dark / Light Mode)
   =================================================================== */
function initTheme() {
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const themeIcon = document.getElementById('themeIcon');
  const storedTheme = localStorage.getItem('taskflow_theme');

  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const currentTheme = storedTheme || (prefersDark ? 'dark' : 'light');

  applyTheme(currentTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const activeTheme = document.documentElement.getAttribute('data-theme') || 'light';
      const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
      applyTheme(newTheme);
      localStorage.setItem('taskflow_theme', newTheme);
    });
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    if (themeIcon) {
      if (theme === 'dark') {
        themeIcon.className = 'fa-solid fa-sun';
        themeIcon.setAttribute('title', 'Switch to Light Mode');
      } else {
        themeIcon.className = 'fa-solid fa-moon';
        themeIcon.setAttribute('title', 'Switch to Dark Mode');
      }
    }
  }
}

/* ===================================================================
   2. Toast Auto-Dismissal & Close Interaction
   =================================================================== */
function initToasts() {
  const toasts = document.querySelectorAll('.toast-item');

  toasts.forEach((toast) => {
    // Auto dismiss after 4.5 seconds
    const timer = setTimeout(() => {
      dismissToast(toast);
    }, 4500);

    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        clearTimeout(timer);
        dismissToast(toast);
      });
    }
  });

  function dismissToast(toast) {
    toast.classList.add('closing');
    setTimeout(() => {
      toast.remove();
    }, 300);
  }
}

/* ===================================================================
   3. AJAX Instant Task Toggle (Progressive Enhancement)
   =================================================================== */
function initAjaxTaskToggles() {
  const toggleForms = document.querySelectorAll('.js-toggle-form');

  toggleForms.forEach((form) => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const url = form.getAttribute('action');
      const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]')?.value;
      const card = form.closest('.task-card');

      if (!url || !card) {
        form.submit();
        return;
      }

      // Optimistic visual feedback
      const wasCompleted = card.classList.contains('is-completed');
      const willBeCompleted = !wasCompleted;
      setCardCompletedVisuals(card, willBeCompleted);

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken || '',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          if (data && data.success) {
            setCardCompletedVisuals(card, data.completed);
            updateDashboardStats(data);
          } else {
            // Revert on failure
            setCardCompletedVisuals(card, wasCompleted);
          }
        } else {
          form.submit(); // Fallback to normal post
        }
      } catch (err) {
        console.error('Toggle error:', err);
        form.submit(); // Fallback
      }
    });
  });

  function setCardCompletedVisuals(card, isCompleted) {
    const checkboxIcon = card.querySelector('.custom-checkbox i');
    const badge = card.querySelector('.status-badge');

    if (isCompleted) {
      card.classList.add('is-completed');
      if (checkboxIcon) checkboxIcon.className = 'fa-solid fa-check';
      if (badge) {
        badge.className = 'status-badge completed';
        badge.innerHTML = '<i class="fa-solid fa-circle-check"></i> Completed';
      }
    } else {
      card.classList.remove('is-completed');
      if (checkboxIcon) checkboxIcon.className = '';
      if (badge) {
        badge.className = 'status-badge pending';
        badge.innerHTML = '<i class="fa-solid fa-clock"></i> In Progress';
      }
    }
  }

  function updateDashboardStats(data) {
    const totalEl = document.getElementById('statTotal');
    const pendingEl = document.getElementById('statPending');
    const completedEl = document.getElementById('statCompleted');
    const progressFill = document.getElementById('progressFill');
    const progressPercent = document.getElementById('progressPercent');

    if (totalEl && data.total_count !== undefined) totalEl.textContent = data.total_count;
    if (pendingEl && data.pending_count !== undefined) pendingEl.textContent = data.pending_count;
    if (completedEl && data.completed_count !== undefined) completedEl.textContent = data.completed_count;

    if (progressFill && data.completion_percentage !== undefined) {
      progressFill.style.width = `${data.completion_percentage}%`;
    }
    if (progressPercent && data.completion_percentage !== undefined) {
      progressPercent.textContent = `${data.completion_percentage}%`;
    }
  }
}

/* ===================================================================
   4. Live Client-Side Search Filtering
   =================================================================== */
function initLiveSearch() {
  const searchInput = document.getElementById('liveSearchInput');
  const taskCards = document.querySelectorAll('.task-card');

  if (!searchInput || taskCards.length === 0) return;

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();

    taskCards.forEach((card) => {
      const title = card.querySelector('.task-title')?.textContent.toLowerCase() || '';
      const desc = card.querySelector('.task-description')?.textContent.toLowerCase() || '';

      if (title.includes(query) || desc.includes(query)) {
        card.style.display = 'flex';
      } else {
        card.style.display = 'none';
      }
    });
  });
}

/* ===================================================================
   5. Keyboard Shortcuts
   =================================================================== */
function initKeyboardShortcuts() {
  const searchInput = document.getElementById('liveSearchInput');
  const titleInput = document.getElementById('id_title');

  // Auto-focus title on form page
  if (titleInput) {
    titleInput.focus();
  }

  window.addEventListener('keydown', (e) => {
    // Press '/' to jump to search bar if not currently typing in an input
    if (e.key === '/' && searchInput && document.activeElement !== searchInput && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
      e.preventDefault();
      searchInput.focus();
    }
    // Press 'Escape' to blur search bar
    if (e.key === 'Escape' && searchInput && document.activeElement === searchInput) {
      searchInput.blur();
    }
  });
}
