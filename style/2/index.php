<?php
include('sys/func.php');
start('ZODZU', '/', 'Полоз Алексей - Разработчик и энтузиаст')
?>

<style type="text/css">
.info {
	width: 100vw;
	color: #505050;
	font-size: 15px;
	text-align: center;
	margin: 10px 0 -10px 0;
}

.left, .center, .right {width: 100vw;}

.center {overflow: hidden;}

.left div, .right div {
	 margin: 25px 0 0 0;
	 font: bold 23px Arial;
}

.left a, .right a {
	padding: 5px 0 0 25px;
	display: block;
}

@media all and (min-width: 480px) {
	.left, .center, .right {width: 31vw;}
	.left {text-align: right; margin-left: 	2vw;}
	.info {display: none;}
}
</style>

<div class="info" onclick="change(this);">↑ Нажми на лого ↑</div>

<div class="left" id="width">
	<div>Основная информация</div>
	<a>Полоз Алексей Евгеньевич</a>
	<a>19 лет</a>
	<a href="https://www.google.ru/maps/place/Санкт-Петербург/">Санкт-Петербург, Россия</a>
	<hr>

	<div>Контакты</div>
	<a href="https://vk.com/freakiller">vk.com/freakiller</a>
	<a href="http://mail.ru/">polozhev@mail.ru</a>
	<a>+7 (981) 163-55-78</a>
	<hr>

	<div>Конкурсы</div><!-- Достижения !-->
	<a>Первое место на региональном уровне Всероссийской Олимпиады Школьников</a>
	<a href="http://abitu.net/conference/1315">Диплом III степени МФТИ</a>
	<a>Первые места в региональных IT конкурсах</a>
	<hr>
</div>

<img src="photo.jpg" class="center" id="set">

<!--
<script type="text/javascript">
	if (document.body.clientWidth >= 480) {
		height = document.getElementById('width').offsetHeight;
		element = document.getElementById('set');

		alert(document.body.clientWidth / 3 - (height * element.offsetWidth / element.offsetHeight));
		delta = document.body.clientWidth / 3 - (height * element.offsetWidth / element.offsetHeight);
		if (delta > 0) {
			margin1 = (delta / 2) + 'px';
			margin2 = 0;

			document.getElementById('set').style.height = height + 'px';
			document.getElementById('set').style.width = (height * element.offsetWidth / element.offsetHeight) + 'px';
		} else {
			margin1 = 0
			margin2 = ((height - element.offsetHeight) / 2) + 'px';

			document.getElementById('set').style.height = '100%';
		}

		document.getElementById('set').style.margin = margin2 + ' ' + margin1 + ' ' + margin2 + ' ' + margin1;
	}
</script>
!-->

<div class="right">
	<div>Обучение</div>
	<a href="http://spbu.ru/">СПбГУ Прикладная Математика - Процессы Управления</a>
	<a href="http://www.fml31.ru/">31 лицей г. Челябинск</a>
	<hr>

	<div>Область деятельности</div>
	<a href="https://ru.wikipedia.org/wiki/Python">Python BackEnd</a>
	<a href="https://ru.wikipedia.org/wiki/Веб-программирование">Web Full-Stack</a>
	<a>Микроконтроллеры: Raspberry Pi, Arduino</a>
	<hr>

	<div>Интересы</div>
	<a href="https://ru.wikipedia.org/wiki/Искусственный_интеллект">Artificial Intelligence, Machine Vision, Machine Learning</a>
	<a href="https://ru.wikipedia.org/wiki/Автоматизированная_система">Роботизированные / автоматизированные системы</a>
	<a href="https://ru.wikipedia.org/wiki/Бот_(программа)">Боты Телеграмм, ВКонтакте</a>
	<a>Биржа</a>
	<hr>
</div>

<!-- Проекты !-->
<div class="notes">
<?php

$list = [
	['Телеграм бот «Дневник криптотрейдеров»', 'Параллельный анализ нескольких бирж, ведение канала, парсер синтаксиса и выделение событий, распознания текста на сложных изображениях, прогнозирование', 'https://t.me/cryptotraders100ru'], 
	['Парсер синтаксиса «Lacuna»', '', ''], 
	['Система умного дома', 'Интернет вещей, Big Data, взаимосвязь различных средств, работающих в едином комплексе и подстраивающегося под конкретные ситуации', 'http://abitu.net/conference/1315'], 
	['Twitter бот', 'Имитация поведения человека в социальной сети, постинг, лайки, репосты, анализ взаимности, анализ популярности, автонакрутка', ''], 
	['Универсальный сайт', 'Социальная сеть с множеством других сервисов, тесно связанных и взаимодействующих между собой', ''], 
	['Категайзер текстов', 'Используя технологию Google Word2Vec и собственноручно прописанная модель нейронной сети', ''], 
	['Прогноз биржи Газпром', '', ''], 
	['СПбГУ газета «Source»', '', 'http://sourceme.ru/'], 
	['Сайт рекламного агентства «PR-Light»', 'Тонко подстраиваемый кабинет администратора', 'http://pr-light.ru/'],
	['Корпус слов', '', ''],
	['Умная кнопка жизни для людей с ограниченными возможностями', 'Управление специальными средствами, системой умного дома и экстренная помощь', '']
];

for ($i=0; $i<count($list); $i++) {
	/*
	if ($list[$i][2])
		$href = $list[$i][2];
	else
		$href = '?i=' . $i
	*/
	print '<a href="' . $list[$i][2] . '"><div style="background-image: url(../load/projects/' . ($i + 1) . '.jpg);"><div class="back"><div class="title">' . $list[$i][0] . '<div>' . $list[$i][1] . '</div></div></div></div></a>';
}

?>
</div>

</body>
</html>