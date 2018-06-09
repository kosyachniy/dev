// Вызов при изменении размеров экрана

$(function() {
	$(window).resize(hideHeader);
});

// Менять отображение хедера

var x = document.body.clientWidth;

function hideHeader() {
	var y = document.body.clientWidth;

	if (x <= 700 && y > 700) {
		$('.u-expand').css('display', 'inline-block');
	} else if (y <= 700 && x > 700) {
		$('.u-expand').css('display', 'none');
	}

	x = y;
}

// Хедер при нажатии

function change(min_width=700) {
	if (document.body.clientWidth <= min_width) {
		if ($('.u-expand').css('display') == 'block')
			$('.u-expand').css('display', 'none');
		else
			$('.u-expand').css('display', 'inline-block');
	} else {
		document.location.href = '/';
	}
}

// Сетка статей

function place(elem, count=4, percent=100, margin=0, padding=0, max_width=1500, min_width=590) {
	var head = document.head || document.getElementsByTagName('head')[0];
	var style = document.createElement('style');

	var ots = margin * 2; /* + padding * 2*/
	var re = (max_width - min_width) / (count - 1);
	var obl = max_width * percent / 100;

	var css = elem + " {width: " + percent + "%;}\n" + elem + " a > div {width: 100%;}\n" + elem + " > a {margin: " + margin + "px;}\n" + elem + " a > div {padding: " + padding + "px;}\n@media all and (max-width: " + min_width + "px) {" + elem + " {width: 100%;} " + elem + " > a {width: calc(100% - " + ots + "px);}}\n";

	for (var i = 0; i < count-1; i++) {
		css += "@media all and (min-width: " + ~~(min_width + re * i) + "px) {" + elem + " {width: " + percent + "%; margin-left: " + (100 - percent) / 2 + "%;} " + elem + " > a {width: calc(" + 100 / (i + 2) + "% - " + ots + "px);}}\n";
	}

	css += "@media all and (min-width: " + max_width + "px) {" + elem + " {width: " + obl + "px;} " + elem + " > a {width: " + (obl / count - ots) + "px;}}";

	style.appendChild(document.createTextNode(css));

	head.appendChild(style);
}

// Отображение контента без перезагрузки

function showContent(link) {  
	var cont = document.getElementById('contentBody');
	var loading = document.getElementById('loading');

	cont.innerHTML = loading.innerHTML;

	var http = createRequestObject();
	if (http) {
		http.open('get', link);
		http.onreadystatechange = function () {  
			if(http.readyState == 4) {
				cont.innerHTML = http.responseText;
			}
		}

	http.send(null);
	} else {
		document.location = link;
	}
}
 
function createRequestObject() {
	try {
		return new XMLHttpRequest()
	} catch(e) {
		try {
			return new ActiveXObject('Msxml2.XMLHTTP')
		} catch(e) {
			try {
				return new ActiveXObject('Microsoft.XMLHTTP')
			} catch(e) {
				return null;
			}
		}
	}
}

function ahref(url) {
	history.pushState(null, null, url);
	showContent(url);
}