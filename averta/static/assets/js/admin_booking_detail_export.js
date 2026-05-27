// Booking change form: export THIS order to CSV (client-side only)
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

  function getFilename(id) {
    var d = new Date();
    var pad = function (n) { return String(n).padStart(2, '0'); };
    var ts = d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) + '_' + pad(d.getHours()) + '-' + pad(d.getMinutes());
    return 'booking_' + (id || 'unknown') + '_' + ts + '.csv';
  }

  function getXlsFilename(id) {
    var d = new Date();
    var pad = function (n) { return String(n).padStart(2, '0'); };
    var ts = d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) + '_' + pad(d.getHours()) + '-' + pad(d.getMinutes());
    return 'booking_' + (id || 'unknown') + '_' + ts + '.xls';
  }

  function onReady(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  onReady(function () {
    var btn = document.getElementById('bookingExportOneCsvBtn');
    var xlsBtn = document.getElementById('bookingExportOneXlsBtn');
    var dataEl = document.getElementById('bookingExportOneCsvData');
    if ((!btn && !xlsBtn) || !dataEl) return;

    function readData() {
      var raw = (dataEl.textContent || '').trim();
      if (!raw) return null;
      try {
        return JSON.parse(raw);
      } catch (err) {
        return null;
      }
    }

    function buildHeadersAndRow(data) {
      var headers = [
        'ID',
        'Tarix',
        'Ad soyad',
        'Mobil nömrə',
        'E-poçt',
        'Qeyd',
        'Böyük sayı',
        'Uşaq sayı',
        'Xidmətlər',
        'Paketlər'
      ];

      var row = [
        data.id,
        data.created_at,
        data.full_name,
        data.phone,
        data.email,
        data.note,
        data.adults_count,
        data.children_count,
        (data.services || []).join(' | '),
        (data.packages || []).join(' | ')
      ];

      return { headers: headers, row: row };
    }

    if (btn) btn.addEventListener('click', function (e) {
      e.preventDefault();
      var data = readData();
      if (!data) return;
      var built = buildHeadersAndRow(data);

      // Use ";" for Excel locales where comma isn't treated as separator.
      // "sep=;" hints Excel to split columns correctly.
      var sep = ';';
      var csv = '\uFEFF' + 'sep=' + sep + '\r\n'
        + built.headers.join(sep) + '\r\n'
        + built.row.map(csvEscape).join(sep) + '\r\n';
      var blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
      downloadBlob(getFilename(data.id), blob);
    });

    // Excel export with controlled column widths (HTML .xls)
    if (xlsBtn) xlsBtn.addEventListener('click', function (e) {
      e.preventDefault();
      var data = readData();
      if (!data) return;
      var built = buildHeadersAndRow(data);

      var colWidths = [8, 22, 26, 18, 22, 42, 10, 10, 38, 38]; // approx "characters"
      var cols = colWidths.map(function (w) { return '<col style="width:' + (w * 8) + 'px" />'; }).join('');

      function td(v) {
        var s = (v == null ? '' : String(v));
        // Basic HTML escape
        s = s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        s = s.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
        return '<td style="border:1px solid #d1d5db; padding:6px; vertical-align:top; white-space:pre-wrap;">' + s + '</td>';
      }

      var ths = built.headers.map(function (h) {
        return '<th style="border:1px solid #d1d5db; padding:7px; background:#13357b; color:#fff; font-weight:700; text-align:left;">' + h + '</th>';
      }).join('');

      var tds = built.row.map(td).join('');

      var html = ''
        + '<html><head><meta charset="utf-8" /></head><body>'
        + '<table style="border-collapse:collapse; font-family:Arial, sans-serif; font-size:12px;">'
        + '<colgroup>' + cols + '</colgroup>'
        + '<thead><tr>' + ths + '</tr></thead>'
        + '<tbody><tr>' + tds + '</tr></tbody>'
        + '</table>'
        + '</body></html>';

      var blob = new Blob([html], { type: 'application/vnd.ms-excel;charset=utf-8' });
      downloadBlob(getXlsFilename(data.id), blob);
    });
  });
})();

