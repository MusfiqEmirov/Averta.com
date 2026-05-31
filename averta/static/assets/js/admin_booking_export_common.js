// Shared booking export helpers (admin CSV / Excel)
window.BookingExport = (function () {
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

  function buildDetail(forExcel) {
    var headers;
    if (forExcel) {
      headers = [
        'ID',
        'Tarix',
        'Ad soyad',
        'Mobil nömrə',
        'E-poçt',
        'Gediş / Qayıdış tarixi',
        'Qeyd',
        'Böyük sayı',
        'Uşaq sayı',
        'Xidmətlər',
        'Paketlər'
      ];
    } else {
      headers = [
        'ID',
        'Tarix',
        'Ad soyad',
        'Mobil nömrə',
        'E-poçt',
        'Gediş tarixi',
        'Qayıdış tarixi',
        'Qeyd',
        'Böyük sayı',
        'Uşaq sayı',
        'Xidmətlər',
        'Paketlər'
      ];
    }
    return { headers: headers, buildRow: function (data) { return rowFromDetail(data, forExcel); } };
  }

  function rowFromDetail(data, forExcel) {
    var services = (data.services || []).join(' | ');
    var packages = (data.packages || []).join(' | ');
    if (forExcel) {
      return [
        data.id,
        data.created_at,
        data.full_name,
        data.phone,
        data.email,
        formatTravelDates(data.date_from, data.date_to),
        data.note,
        data.adults_count,
        data.children_count,
        services,
        packages
      ];
    }
    return [
      data.id,
      data.created_at,
      data.full_name,
      data.phone,
      data.email,
      data.date_from || '',
      data.date_to || '',
      data.note,
      data.adults_count,
      data.children_count,
      services,
      packages
    ];
  }

  function buildList(forExcel) {
    var headers;
    if (forExcel) {
      headers = [
        'Ad soyad',
        'Seçim',
        'Gediş / Qayıdış tarixi',
        'Böyük sayı',
        'Uşaq sayı',
        'E-poçt',
        'Mobil nömrə',
        'Oxunub',
        'Müştəri',
        'Silinib',
        'Tarix'
      ];
    } else {
      headers = [
        'Ad soyad',
        'Seçim',
        'Gediş tarixi',
        'Qayıdış tarixi',
        'Böyük sayı',
        'Uşaq sayı',
        'E-poçt',
        'Mobil nömrə',
        'Oxunub',
        'Müştəri',
        'Silinib',
        'Tarix'
      ];
    }
    return { headers: headers, buildRow: function (data) { return rowFromList(data, forExcel); } };
  }

  function rowFromList(data, forExcel) {
    if (forExcel) {
      return [
        data.full_name,
        data.booking_target,
        formatTravelDates(data.date_from, data.date_to),
        data.adults_count,
        data.children_count,
        data.email,
        data.phone,
        boolLabel(data.is_read),
        boolLabel(data.is_customer),
        boolLabel(data.is_deleted),
        data.created_at
      ];
    }
    return [
      data.full_name,
      data.booking_target,
      data.date_from || '',
      data.date_to || '',
      data.adults_count,
      data.children_count,
      data.email,
      data.phone,
      boolLabel(data.is_read),
      boolLabel(data.is_customer),
      boolLabel(data.is_deleted),
      data.created_at
    ];
  }

  function buildCsv(headers, rows, sep) {
    sep = sep || ';';
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
      + '<html><head><meta charset="utf-8" /></head><body>'
      + '<table style="border-collapse:collapse; font-family:Arial, sans-serif; font-size:12px;">'
      + '<colgroup>' + cols + '</colgroup>'
      + '<thead><tr>' + ths + '</tr></thead>'
      + '<tbody>' + bodyRows + '</tbody>'
      + '</table>'
      + '</body></html>';
  }

  function readJsonScript(id) {
    var el = document.getElementById(id);
    if (!el) return null;
    var raw = (el.textContent || '').trim();
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch (err) {
      return null;
    }
  }

  return {
    formatTravelDates: formatTravelDates,
    csvEscape: csvEscape,
    htmlEscape: htmlEscape,
    excelCell: excelCell,
    buildDetail: buildDetail,
    buildList: buildList,
    buildCsv: buildCsv,
    buildXls: buildXls,
    readJsonScript: readJsonScript
  };
})();
