(function ($) {

AjaxSolr.TagcloudWidget = AjaxSolr.AbstractFacetWidget.extend({
  afterRequest: function () {
    if (this.manager.response.facet_counts.facet_fields[this.field] === undefined) {
      $(this.target).html('no items found in current selection');
      return;
    }

    var maxCount = 0;
    var objectedItems = [];
    var facet_counts = this.manager.response.facet_counts.facet_fields[this.field];
    while (facet_counts.length > 1) {
      var count = parseInt(facet_counts.pop());
      var facet = facet_counts.pop();
      if (count > maxCount) {
        maxCount = count;
      }
      objectedItems.push({ facet: facet, count: count });
    }
    objectedItems.sort(function (a, b) {
      return a.facet < b.facet ? -1 : 1;
    });

    $(this.target).empty();
    for (var i = 0, l = objectedItems.length; i < l; i++) {
      var facet = objectedItems[i].facet;
      $(this.target).append(
        $('<a href="#" class="tagcloud_item"></a>')
        .text(facet)
        .addClass('tagcloud_size_' + parseInt(objectedItems[i].count / maxCount * 10))
        .click(this.clickHandler(facet))
      );
    }
  }
});

})(jQuery);
