// Автоматическое изменение ширины в зависимости от контента

var d = {};

$('textarea').each(function() {
	if (!(this.className in d)) {
		d[this.className] = this.clientHeight + 2;
	}

	this.setAttribute('style', 'height:' + (Math.max(this.scrollHeight, d[this.className])) + 'px; overflow-y:hidden;');
	}).on('input', function() {
		//this.style.height = 'auto';
		this.style.height = (Math.max(this.scrollHeight, d[this.className])) + 'px';
});

// Анимация поисковой строки

$(function() {
	$(window).resize(changeSearch);
});

function getTextWidth(text, font) {
	var canvas = getTextWidth.canvas || (getTextWidth.canvas = document.createElement("canvas"));
	var context = canvas.getContext("2d");
	context.font = font;
	var metrics = context.measureText(text);
	return metrics.width;
}

function changeSearch() {
	var y = document.body.clientWidth;

	var text = $('.u-search input').val();
	if (!text) {
		text = $('.u-search input').attr('placeholder');
	}

	var width = getTextWidth(text, $('body').css('font'));

	if (y >= 1100) {
		var z = 300 - width / 2;
	} else if (y > 700) {
		var z = (y - 500 - width) / 2;
	} else {
		var z = y;
	}

	$('.u-search input').css('padding-left', z);
}