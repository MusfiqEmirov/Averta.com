// Booking changelist: export list to CSV/XLS from server JSON (reliable dates)
(function () {
  var BE = window.BookingExport;
  if (!BE) return;

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

  function readRows() {
    var data = BE.readJsonScript('bookingExportListData');
    return Array.isArray(data) ? data : null;
  }

  function onReady(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  onReady(function () {
    var csvBtn = document.getElementById('bookingExportListCsvBtn');
    var xlsBtn = document.getElementById('bookingExportListXlsBtn');
    if (!csvBtn && !xlsBtn) return;

    if (csvBtn) csvBtn.addEventListener('click', function (e) {
      e.preventDefault();
      var rows = readRows();
      if (!rows || !rows.length) return;
      var spec = BE.buildList(false);
      var dataRows = rows.map(spec.buildRow);
      var csv = BE.buildCsv(spec.headers, dataRows);
      downloadBlob('bookings_' + timestamp() + '.csv', new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    });

    if (xlsBtn) xlsBtn.addEventListener('click', function (e) {
      e.preventDefault();
      var rows = readRows();
      if (!rows || !rows.length) return;
      var spec = BE.buildList(true);
      var dataRows = rows.map(spec.buildRow);
      var html = BE.buildXls(spec.headers, dataRows, [26, 38, 16, 10, 10, 22, 18, 10, 10, 10, 22]);
      downloadBlob('bookings_' + timestamp() + '.xls', new Blob([html], { type: 'application/vnd.ms-excel;charset=utf-8' }));
    });
  });
})();
