//Navbar Toggle

$('.navbar-toggle').click(function () {
	if ($(this).hasClass('collapsed')) {
		$(this).removeClass('collapsed');
	} else {
		$(this).addClass('collapsed');
	}
})


// Back to top Arrow

jQuery(document).ready(function ($) {
	// browser window scroll (in pixels) after which the "back to top" link is shown
	var offset = 300,
		//browser window scroll (in pixels) after which the "back to top" link opacity is reduced
		offset_opacity = 1200,
		//duration of the top scrolling animation (in ms)
		scroll_top_duration = 700,
		//grab the "back to top" link
		$back_to_top = $('.cd-top, .top'),
		//
		$nav_logo = $('#nav-logo');

	//hide or show the "back to top" link
	$(window).scroll(function () {
		($(this).scrollTop() > offset) ? $back_to_top.addClass('cd-is-visible') : $back_to_top.removeClass('cd-is-visible cd-fade-out');
		if ($(this).scrollTop() > offset_opacity) {
			$back_to_top.addClass('cd-fade-out');
		}
	});

	//smooth scroll to top
	$back_to_top.on('click', function (event) {
		event.preventDefault();
		$('body,html').animate({
			scrollTop: 0,
		}, scroll_top_duration
		);
	});

	//
	$nav_logo.on('click', function () {
		window.location.href = "index.html";
	});
});

//articles
function getArticles(res) {
	strHtml_art = ""
	strHtml_all_art = ""
	$.each(res, function (index, data) {
		strHtml_all_art += "<a href='" + data['url']
		strHtml_all_art += "' target='_blank'><div class='article-item row'><div class='col-md-3'><br><img src='" + data['poster']
		strHtml_all_art += "'></div><div class='col-md-9'><h3>" + data['title']
		strHtml_all_art += "</h3><h5>" + data['subheading']
		strHtml_all_art += "</h5><br><h6>" + data['original'] + ' ' + data['author'] + ' ' + data['date']
		strHtml_all_art += "</h6></div></div></a>"
		if (index <= 2) {
			strHtml_art = strHtml_all_art
		}
	})
	$('#articles').html(strHtml_art)
	$('#allArticles').html(strHtml_all_art)
}

// handle links with @href started with '#' only
// $(document).on('click', 'a[href^="#"]', function (e) {
// 	// target element id
// 	var id = $(this).attr('href');

// 	// target element
// 	var $id = $(id);
// 	if ($id.length === 0) {
// 		return;
// 	}

// 	// prevent standard hash navigation (avoid blinking in IE)
// 	e.preventDefault();

// 	// top position relative to the document
// 	var pos = $(id).offset().top;

// 	// animated top scrolling
// 	$('body, html').animate({ scrollTop: pos });
// });
