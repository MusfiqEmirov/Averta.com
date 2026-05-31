// Admin booking CSV / Excel export (list + single order)
(function () {
  function formatTravelDates(from, to) {
    from = (from || '').trim();
    to = (to || '').trim();
    if (!from && !to) return '—';
    if (from && to) return from + '\n' + to;
    return from || to;
  }

  function csvEscape(value, sep) {
    if (value == null) return '';
    var s = String(value);
    s = s.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    var re = new RegExp('["' + sep + '\\n]');
    if (re.test(s)) s = '"' + s.replace(/"/g, '""') + '"';
    return s;
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

  function buildCsv(headers, rows) {
    var sep = ';';
    var lines = [];
    lines.push(headers.map(function (h) { return csvEscape(h, sep); }).join(sep));
    rows.forEach(function (row) {
      lines.push(row.map(function (v) { return csvEscape(v, sep); }).join(sep));
    });
    return '\uFEFF' + 'sep=' + sep + '\r\n' + lines.join('\r\n') + '\r\n';
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

  function buildDetail(data, forExcel) {
    var services = (data.services || []).join(' | ');
    var packages = (data.packages || []).join(' | ');
    if (forExcel) {
      return {
        headers: ['ID', 'Tarix', 'Ad soyad', 'Mobil nömrə', 'E-poçt', 'Gediş / Qayıdış tarixi', 'Qeyd', 'Böyük sayı', 'Uşaq sayı', 'Xidmətlər', 'Paketlər'],
        row: [data.id, data.created_at, data.full_name, data.phone, data.email, formatTravelDates(data.date_from, data.date_to), data.note, data.adults_count, data.children_count, services, packages]
      };
    }
    return {
      headers: ['ID', 'Tarix', 'Ad soyad', 'Mobil nömrə', 'E-poçt', 'Gediş tarixi', 'Qayıdış tarixi', 'Qeyd', 'Böyük sayı', 'Uşaq sayı', 'Xidmətlər', 'Paketlər'],
      row: [data.id, data.created_at, data.full_name, data.phone, data.email, data.date_from || '', data.date_to || '', data.note, data.adults_count, data.children_count, services, packages]
    };
  }

  function buildListRow(data, forExcel) {
    if (forExcel) {
      return {
        headers: ['Ad soyad', 'Seçim', 'Gediş / Qayıdış tarixi', 'Böyük sayı', 'Uşaq sayı', 'E-poçt', 'Mobil nömrə', 'Oxunub', 'Müştəri', 'Silinib', 'Tarix'],
        row: [data.full_name, data.booking_target, formatTravelDates(data.date_from, data.date_to), data.adults_count, data.children_count, data.email, data.phone, boolLabel(data.is_read), boolLabel(data.is_customer), boolLabel(data.is_deleted), data.created_at]
      };
    }
    return {
      headers: ['Ad soyad', 'Seçim', 'Gediş tarixi', 'Qayıdış tarixi', 'Böyük sayı', 'Uşaq sayı', 'E-poçt', 'Mobil nömrə', 'Oxunub', 'Müştəri', 'Silinib', 'Tarix'],
      row: [data.full_name, data.booking_target, data.date_from || '', data.date_to || '', data.adults_count, data.children_count, data.email, data.phone, boolLabel(data.is_read), boolLabel(data.is_customer), boolLabel(data.is_deleted), data.created_at]
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
    bindExport(document.getElementById('bookingExportOneCsvBtn'), function () {
      var data = readJsonScript('bookingExportOneData');
      if (!data) {
        window.alert('Export məlumatı tapılmadı. Səhifəni yeniləyin.');
        return;
      }
      var spec = buildDetail(data, false);
      downloadBlob('booking_' + data.id + '_' + fileTs() + '.csv', new Blob([buildCsv(spec.headers, [spec.row])], { type: 'text/csv;charset=utf-8' }));
    });

    bindExport(document.getElementById('bookingExportOneXlsBtn'), function () {
      var data = readJsonScript('bookingExportOneData');
      if (!data) {
        window.alert('Export məlumatı tapılmadı. Səhifəni yeniləyin.');
        return;
      }
      var spec = buildDetail(data, true);
      downloadBlob('booking_' + data.id + '_' + fileTs() + '.xls', new Blob([buildXls(spec.headers, [spec.row], [8, 22, 26, 18, 22, 16, 42, 10, 10, 38, 38])], { type: 'application/vnd.ms-excel;charset=utf-8' }));
    });

    bindExport(document.getElementById('bookingExportListCsvBtn'), function () {
      var rows = readJsonScript('bookingExportListData');
      if (!Array.isArray(rows) || !rows.length) {
        var fallback = extractTableFallback();
        if (!fallback) {
          window.alert('Export üçün məlumat tapılmadı.');
          return;
        }
        downloadBlob('bookings_' + fileTs() + '.csv', new Blob([buildCsv(fallback.headers, fallback.data)], { type: 'text/csv;charset=utf-8' }));
        return;
      }
      var spec = buildListRow(rows[0], false);
      var dataRows = rows.map(function (r) { return buildListRow(r, false).row; });
      downloadBlob('bookings_' + fileTs() + '.csv', new Blob([buildCsv(spec.headers, dataRows)], { type: 'text/csv;charset=utf-8' }));
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
      var spec = buildListRow(rows[0], true);
      var dataRows = rows.map(function (r) { return buildListRow(r, true).row; });
      downloadBlob('bookings_' + fileTs() + '.xls', new Blob([buildXls(spec.headers, dataRows, [26, 38, 16, 10, 10, 22, 18, 10, 10, 10, 22])], { type: 'application/vnd.ms-excel;charset=utf-8' }));
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
