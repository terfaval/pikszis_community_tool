function initOptionRow(row) {
  const remove = row.querySelector('.remove-option');
  remove.addEventListener('click', () => {
    row.remove();
    watchLastRow();
  });
}

function addEmptyRow() {
  const list = document.getElementById('options-list');
  if (!list) return;
  const row = document.createElement('div');
  row.className = 'option-row flex items-center gap-2';
  row.innerHTML = "<span class='handle cursor-move select-none'>☰</span>" +
    "<input type='text' class='border rounded w-full p-1 option-label' placeholder='Szöveg'/>" +
    "<input type='text' class='border rounded w-full p-1 option-value' placeholder='Érték'/>" +
    "<button type='button' class='remove-option text-red-600'>&times;</button>";
  list.appendChild(row);
  initOptionRow(row);
  watchLastRow();
}

function watchLastRow() {
  const list = document.getElementById('options-list');
  if (!list) return;
  const rows = list.querySelectorAll('.option-row');
  if (!rows.length) {
    addEmptyRow();
    return;
  }
  const last = rows[rows.length - 1];
  const input = last.querySelector('.option-label');
  input.addEventListener('input', function handler() {
    if (input.value.trim() !== '') {
      input.removeEventListener('input', handler);
      addEmptyRow();
    }
  });
}

function serializeOptions(form) {
  const list = document.getElementById('options-list');
  if (!list) return;
  form.querySelectorAll('input[name="option_label[]"],input[name="option_value[]"]').forEach(e => e.remove());
  const rows = list.querySelectorAll('.option-row');
  rows.forEach(row => {
    const label = row.querySelector('.option-label').value.trim();
    const value = row.querySelector('.option-value').value;
    if (label) {
      const l = document.createElement('input');
      l.type = 'hidden';
      l.name = 'option_label[]';
      l.value = label;
      form.appendChild(l);
      const v = document.createElement('input');
      v.type = 'hidden';
      v.name = 'option_value[]';
      v.value = value;
      form.appendChild(v);
    }
  });
}

function toggleSections() {
  const qtype = document.getElementById('qtype');
  const optionsSection = document.getElementById('options-section');
  const lv = document.getElementById('likert-variant');
  const list = document.getElementById('options-list');
  if (!qtype) return;
  const val = qtype.value;
  if (['single_choice','multiple_choice','true_false'].includes(val)) {
    optionsSection.classList.remove('hidden');
    if (val === 'true_false' && list && list.querySelectorAll('.option-row').length <= 1) {
      list.innerHTML = '';
      ['Igaz','Hamis'].forEach((txt, idx) => {
        const row = document.createElement('div');
        row.className = 'option-row flex items-center gap-2';
        row.innerHTML = "<span class='handle cursor-move select-none'>☰</span>"+
          `<input type='text' class='border rounded w-full p-1 option-label' value='${txt}' placeholder='Szöveg'/>`+
          `<input type='text' class='border rounded w-full p-1 option-value' value='${idx===0?'true':'false'}' placeholder='Érték'/>`+
          "<button type='button' class='remove-option text-red-600'>&times;</button>";
        list.appendChild(row);
        initOptionRow(row);
      });
      addEmptyRow();
    }
  } else {
    optionsSection.classList.add('hidden');
  }
  if (val.startsWith('likert')) {
    lv.classList.remove('hidden');
  } else {
    lv.classList.add('hidden');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('question-form');
  if (!form) return;
  document.querySelectorAll('#options-list .option-row').forEach(initOptionRow);
  watchLastRow();
  const list = document.getElementById('options-list');
  if (list && typeof Sortable !== 'undefined') {
    Sortable.create(list, {
      handle: '.handle',
      animation: 150,
      onEnd: function() {
        const id = form.dataset.questionId;
        if (!id) return;
        const ids = Array.from(list.querySelectorAll('.option-id')).map(i => parseInt(i.value));
        if (ids.length) {
          fetch(`/admin/q/${id}/options_reorder`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(ids)
          });
        }
      }
    });
  }
  form.addEventListener('submit', (e) => serializeOptions(form));
  const qtype = document.getElementById('qtype');
  qtype.addEventListener('change', toggleSections);
  toggleSections();
});