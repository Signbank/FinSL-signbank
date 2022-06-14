// Show video tooltip on hover
// Author: Henri Nieminen for FinSL-signbank
$( function() {
$( document ).tooltip({
  items: "[data-video-src]",
  content: function() {
    var element = $( this );
    if ( element.is( "[data-video-src]" ) ) {
      var src_video = element.attr("data-video-src");
      var src_poster = element.attr("data-thumbnail-src");
      var content_type = element.attr("data-content-type");


      if (!src_video) { return; }

      if (content_type.startsWith("video/")) {
        return "<video preload='none' autoplay muted poster='"+src_poster+"' width='250'><source src='"+src_video+"' type='"+content_type+"'>Your browser does not support the video tag.</video>";
      } else if (content_type.startsWith("image/")) {
        return "<img src='" + src_video + "' class='img-responsive' />";
      }
    }
  }
});
} );