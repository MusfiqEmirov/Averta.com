// Booking changelist: export currently visible table to CSV/XLS (client-side only)
(function () {
  function csvEscape(value) {
    if (value == null) return '';
    var s = String(value);
    s = s.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    if (/[",\n]/.test(s)) s = '"' + s.replace(/"/g, '""') + '"';
    return s;
  }

  function downloadBlob(filename, blob) {
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  function timestamp() {
    var d = new Date();
    var pad = function (n) { return String(n).padStart(2, '0'); };
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) + '_' + pad(d.getHours()) + '-' + pad(d.getMinutes());
  }

  function getTable() {
    return document.getElementById('result_list');
  }

  function extractTable() {
    var table = getTable();
    if (!table) return null;
    var trs = Array.from(table.querySelectorAll('tr'));
    var rows = [];

    trs.forEach(function (tr) {
      var cells = Array.from(tr.querySelectorAll('th,td'));
      if (!cells.length) return;

      // skip first checkbox column if present
      if (cells[0] && cells[0].querySelector('input.action-select, input#action-toggle')) {
        cells = cells.slice(1);
      }

      var values = cells.map(function (cell) {
        var text = (cell.innerText || cell.textContent || '').trim().replace(/\s+/g, ' ');
        return text;
      });
      rows.push(values);
    });

    if (rows.length < 2) return null; // need header + at least one row
    return { headers: rows[0], data: rows.slice(1) };
  }

  function buildCsv(extracted) {
    var sep = ';';
    var lines = [];
    lines.push(extracted.headers.map(csvEscape).join(sep));
    extracted.data.forEach(function (r) {
      lines.push(r.map(csvEscape).join(sep));
    });
    return '\uFEFF' + 'sep=' + sep + '\r\n' + lines.join('\r\n') + '\r\n';
  }

  function htmlEscape(s) {
    s = (s == null ? '' : String(s));
    return s
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function buildXls(extracted) {
    var colCount = extracted.headers.length;
    var defaultWidthPx = 180;
    var cols = '';
    for (var i = 0; i < colCount; i++) cols += '<col style="width:' + defaultWidthPx + 'px" />';

    var ths = extracted.headers.map(function (h) {
      return '<th style="border:1px solid #d1d5db; padding:7px; background:#13357b; color:#fff; font-weight:700; text-align:left;">' + htmlEscape(h) + '</th>';
    }).join('');

    var bodyRows = extracted.data.map(function (r) {
      var tds = r.map(function (v) {
        return '<td style="border:1px solid #d1d5db; padding:6px; vertical-align:top; white-space:nowrap;">' + htmlEscape(v) + '</td>';
      }).join('');
      return '<tr>' + tds + '</tr>';
    }).join('');

    return ''
      + '<html><head><meta charset="utf-8" /></head><body>'
      + '<table style="border-collapse:collapse; font-family:Arial, sans-serif; font-size:12px;">'
      + '<colgroup>' + cols + '</colgroup>'
      + '<thead><tr>' + ths + '</tr></thead>'
      + '<tbody>' + bodyRows + '</tbody>'
      + '</table>'
      + '</body></html>';
  }

  function onReady(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  onReady(function () {
    var csvBtn = document.getElementById('bookingExportListCsvBtn');
    var xlsBtn = document.getElementById('bookingExportListXlsBtn');
    if (!csvBtn && !xlsBtn) return;

    function read() { return extractTable(); }

    if (csvBtn) csvBtn.addEventListener('click', function (e) {
      e.preventDefault();
      var ex = read();
      if (!ex) return;
      var csv = buildCsv(ex);
      downloadBlob('bookings_' + timestamp() + '.csv', new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    });

    if (xlsBtn) xlsBtn.addEventListener('click', function (e) {
      e.preventDefault();
      var ex = read();
      if (!ex) return;
      var html = buildXls(ex);
      downloadBlob('bookings_' + timestamp() + '.xls', new Blob([html], { type: 'application/vnd.ms-excel;charset=utf-8' }));
    });
  });
})();

