// Scrolls to the specified element
jQuery.fn.extend({
  scrollTo : function(speed, offset) {
  	var offset = offset || 250;
	var scrollElement = 'html, body';
	$('html, body').each(function () {
	    var initScrollTop = $(this).attr('scrollTop');
	    $(this).attr('scrollTop', initScrollTop + 1);
	    if ($(this).attr('scrollTop') == initScrollTop + 1) {
	        scrollElement = this.nodeName.toLowerCase();
	        $(this).attr('scrollTop', initScrollTop);
	        return false;
	    }    
	});
	
    return this.each(function() {
      var targetOffset = $(this).offset().top - offset;
      $(scrollElement).animate({scrollTop: targetOffset}, speed);
    });
  }
});
