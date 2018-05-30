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
      var video_ext = element.attr("data-video-ext");
      if ( src_video != "") {
        return "<video preload='none' autoplay muted poster='"+src_poster+"' width='250'><source src='"+src_video+"' type='video/"+video_ext+"'>Your browser does not support the video tag.</video>";
      }
    }
  }
});
} );