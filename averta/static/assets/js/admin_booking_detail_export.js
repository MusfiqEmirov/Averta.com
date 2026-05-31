// Booking change form: export THIS order to CSV/XLS (client-side)
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

  function timestamp(id) {
    var d = new Date();
    var pad = function (n) { return String(n).padStart(2, '0'); };
    var ts = d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) + '_' + pad(d.getHours()) + '-' + pad(d.getMinutes());
    return 'booking_' + (id || 'unknown') + '_' + ts;
  }

  function onReady(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  onReady(function () {
    var csvBtn = document.getElementById('bookingExportOneCsvBtn');
    var xlsBtn = document.getElementById('bookingExportOneXlsBtn');
    if (!csvBtn && !xlsBtn) return;

    function readData() {
      return BE.readJsonScript('bookingExportOneData');
    }

    if (csvBtn) csvBtn.addEventListener('click', function (e) {
      e.preventDefault();
      var data = readData();
      if (!data) return;
      var spec = BE.buildDetail(false);
      var csv = BE.buildCsv(spec.headers, [spec.buildRow(data)]);
      downloadBlob(timestamp(data.id) + '.csv', new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    });

    if (xlsBtn) xlsBtn.addEventListener('click', function (e) {
      e.preventDefault();
      var data = readData();
      if (!data) return;
      var spec = BE.buildDetail(true);
      var html = BE.buildXls(spec.headers, [spec.buildRow(data)], [8, 22, 26, 18, 22, 16, 42, 10, 10, 38, 38]);
      downloadBlob(timestamp(data.id) + '.xls', new Blob([html], { type: 'application/vnd.ms-excel;charset=utf-8' }));
    });
  });
})();
