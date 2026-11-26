/* The site menu's drop-downs (tools/site_nav.py): one open at a time; close on a click outside, on Escape, or on a link. */
(function () {
  var dds = [].slice.call(document.querySelectorAll('.top nav details.dd'));
  if (!dds.length) return;
  function closeAll(keep) { dds.forEach(function (d) { if (d !== keep) d.open = false; }); }
  dds.forEach(function (d) {
    d.addEventListener('toggle', function () { if (d.open) closeAll(d); });
    [].forEach.call(d.querySelectorAll('a'), function (a) { a.addEventListener('click', function () { d.open = false; }); });
  });
  document.addEventListener('click', function (e) { if (!e.target.closest || !e.target.closest('.top nav details.dd')) closeAll(); });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var open = dds.filter(function (d) { return d.open; })[0];
    if (open) { closeAll(); open.querySelector('summary').focus(); }
  });
})();
