$(function() {

  // enabled tooltip
  $('[data-toggle="tooltip"]').tooltip()

  // toggle all checkbox
  $('[data-toggle="checkbox"]').change(function () {
    $('input[type=checkbox]').prop('checked', this.checked);
  });



});
