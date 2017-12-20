<!Doctype html>
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no">
	<meta name="apple-mobile-web-app-capable" content="yes">
	<link rel="stylesheet" type="text/css" href="/sys/main.css">

	<title><?=$title?></title>
	<link rel ="shortcut icon" type="images/png" href="/sys/favicon.png">
	<meta name="author" content="Poloz Alexey">
	<meta name="keywords" content="<?=$descript?>">
	<meta name="description" content="<?=$descript?>">
</head>
<!--
	<script src="/sys/main.js"></script>
!-->
<body>
	<script type="text/javascript">
function change() {
	if (document.getElementById('menu').style.display == 'block') document.getElementById('menu').style.display = 'none';
	else document.getElementById('menu').style.display = 'block';
}
	</script>

	<div class="header" onclick="change(this);">
		<img src="/sys/logo.png" >
		<a href="/"><div>Главная</div></a>
		<a href="/notes"><div>Статьи</div></a>
		<a href="/services"><div>Услуги</div></a>

	</div>

	<div class="expand" id="menu">
		<form action="/sys/search.php" method="post">
			<input placeholder="Поиск" name="search">
		</form>
		<div>
<?php
if ($_SESSION['auth']==2) print '<a href="/cabinet">'.$_SESSION['user'].'</a> &nbsp;<a href="/sys/out.php" class="del">Выйти</a>';
else print '<a class="del">Гость &nbsp;</a><a href="/login">Войти</a>';
?>
		</div>
		<a href="/"><div>Главная</div></a>
		<a href="/notes"><div>Статьи</div></a>
		<a href="/services"><div>Услуги</div></a>
	</div>