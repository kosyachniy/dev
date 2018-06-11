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