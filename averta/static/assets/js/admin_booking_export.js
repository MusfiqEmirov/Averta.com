// Admin booking Excel export (list + single order)
(function () {
  function formatTravelDates(from, to, arrival) {
    var parts = [(from || '').trim(), (to || '').trim(), (arrival || '').trim()].filter(Boolean);
    if (!parts.length) return '—';
    return parts.join('\n');
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

  function excelCell(value) {
    return htmlEscape(value == null ? '' : String(value)).replace(/\n/g, '<br/>');
  }

  function boolLabel(v) {
    return v ? 'Bəli' : 'Xeyr';
  }

  function readJsonScript(id) {
    var el = document.getElementById(id);
    if (!el) return null;
    var raw = (el.textContent || el.innerHTML || '').trim();
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch (err) {
      return null;
    }
  }

  function downloadBlob(filename, blob) {
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1500);
  }

  function fileTs() {
    var d = new Date();
    var pad = function (n) { return String(n).padStart(2, '0'); };
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) + '_' + pad(d.getHours()) + '-' + pad(d.getMinutes());
  }

  function buildXls(headers, rows, colWidths) {
    colWidths = colWidths || [];
    var cols = headers.map(function (_, i) {
      var w = colWidths[i] || 22;
      return '<col style="width:' + (w * 8) + 'px" />';
    }).join('');

    var ths = headers.map(function (h) {
      return '<th style="border:1px solid #d1d5db; padding:7px; background:#13357b; color:#fff; font-weight:700; text-align:left;">' + htmlEscape(h) + '</th>';
    }).join('');

    var bodyRows = rows.map(function (row) {
      var tds = row.map(function (v) {
        return '<td style="border:1px solid #d1d5db; padding:6px; vertical-align:top; white-space:pre-wrap;">' + excelCell(v) + '</td>';
      }).join('');
      return '<tr>' + tds + '</tr>';
    }).join('');

    return ''
      + '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel">'
      + '<head><meta charset="utf-8" /></head><body>'
      + '<table style="border-collapse:collapse; font-family:Arial, sans-serif; font-size:12px;">'
      + '<colgroup>' + cols + '</colgroup>'
      + '<thead><tr>' + ths + '</tr></thead>'
      + '<tbody>' + bodyRows + '</tbody>'
      + '</table>'
      + '</body></html>';
  }

  function buildDetail(data) {
    var services = (data.services || []).join(' | ');
    var packages = (data.packages || []).join(' | ');
    return {
      headers: ['ID', 'Tarix', 'Ad soyad', 'Mobil nömrə', 'E-poçt', 'Gediş / Qayıdış / Gəliş tarixi', 'Qeyd', 'Böyük sayı', 'Uşaq sayı', 'Xidmətlər', 'Paketlər'],
      row: [data.id, data.created_at, data.full_name, data.phone, data.email, formatTravelDates(data.date_from, data.date_to, data.arrival_date), data.note, data.adults_count, data.children_count, services, packages]
    };
  }

  function buildListRow(data) {
    return {
      headers: ['Ad soyad', 'Seçim', 'Gediş / Qayıdış / Gəliş tarixi', 'Böyük sayı', 'Uşaq sayı', 'E-poçt', 'Mobil nömrə', 'Oxunub', 'Müştəri', 'Silinib', 'Tarix'],
      row: [data.full_name, data.booking_target, formatTravelDates(data.date_from, data.date_to, data.arrival_date), data.adults_count, data.children_count, data.email, data.phone, boolLabel(data.is_read), boolLabel(data.is_customer), boolLabel(data.is_deleted), data.created_at]
    };
  }

  function extractTableFallback() {
    var table = document.getElementById('result_list');
    if (!table) return null;
    var trs = Array.from(table.querySelectorAll('tr'));
    var rows = [];

    trs.forEach(function (tr) {
      var cells = Array.from(tr.querySelectorAll('th,td'));
      if (!cells.length) return;
      if (cells[0] && cells[0].querySelector('input.action-select, input#action-toggle')) {
        cells = cells.slice(1);
      }
      rows.push(cells.map(function (cell) {
        return (cell.innerText || cell.textContent || '').trim().replace(/\s+/g, ' ');
      }));
    });

    if (rows.length < 2) return null;
    return { headers: rows[0], data: rows.slice(1) };
  }

  function bindExport(btn, handler) {
    if (!btn) return;
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      handler();
    });
  }

  function init() {
    bindExport(document.getElementById('bookingExportOneXlsBtn'), function () {
      var data = readJsonScript('bookingExportOneData');
      if (!data) {
        window.alert('Export məlumatı tapılmadı. Səhifəni yeniləyin.');
        return;
      }
      var spec = buildDetail(data);
      downloadBlob('booking_' + data.id + '_' + fileTs() + '.xls', new Blob([buildXls(spec.headers, [spec.row], [8, 22, 26, 18, 22, 16, 42, 10, 10, 38, 38])], { type: 'application/vnd.ms-excel;charset=utf-8' }));
    });

    bindExport(document.getElementById('bookingExportListXlsBtn'), function () {
      var rows = readJsonScript('bookingExportListData');
      if (!Array.isArray(rows) || !rows.length) {
        var fallback = extractTableFallback();
        if (!fallback) {
          window.alert('Export üçün məlumat tapılmadı.');
          return;
        }
        downloadBlob('bookings_' + fileTs() + '.xls', new Blob([buildXls(fallback.headers, fallback.data)], { type: 'application/vnd.ms-excel;charset=utf-8' }));
        return;
      }
      var spec = buildListRow(rows[0]);
      var dataRows = rows.map(function (r) { return buildListRow(r).row; });
      downloadBlob('bookings_' + fileTs() + '.xls', new Blob([buildXls(spec.headers, dataRows, [26, 38, 16, 10, 10, 22, 18, 10, 10, 10, 22])], { type: 'application/vnd.ms-excel;charset=utf-8' }));
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
