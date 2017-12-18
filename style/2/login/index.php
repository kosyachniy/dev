<?php
include('../sys/func.php');

$ser=$_SERVER['HTTP_REFERER'];
if (!stripos($ser, 'login')) {
	if (stripos($ser, 'zodzu')) $_SESSION['inp']=$ser;
	else $_SESSION['inp']='/';
	}
else
	$_SESSION['inp']='/';

start('Аккаунт - ZODZU', 'login', 'Логин, авторизация, пароль, аккаунт');
?>

<style>
.login {width: 40%; padding: 0 5% 0 5%;}
.login:last-child {padding: 0 0 0 5%;}
font {
	font-size: 1.7rem;
	font-weight: bold;
	width: 100%;
	text-align: center;
	display: block;
	padding: 20px 0 15px 0;
}

@media all and (max-width: 800px) {
	.login {
		width: 90%;
		padding: 0 0 0 7%;
	}
}
</style>

<div class="login">
	<font>Зарегистрироваться</font>
	<form action="form.php" method="post">
		<input type="text" name="name" placeholder="Имя" required>
		<input type="text" name="surname" placeholder="Фамилия" required>
		<input type="email" name="mail" placeholder="Почта" readonly onfocus="this.removeAttribute('readonly')" required>
		<input type="password" name="pas" placeholder="Пароль" readonly onfocus="this.removeAttribute('readonly')" required>
		<input type="submit" value="Зарегистрироваться">
	</form>
	<br><br>
	Нажимая кнопку "Зарегистрироваться", Вы автоматически соглашаетесь с <a href="privacy.php" style="color: blue;">условиями сайта</a>.
</div><div class="login">
	<font>Войти</font>
	<form action="login.php" method="post">
		<input placeholder="Почта" name="user" required>
		<input type="password" placeholder="Пароль" name="pas" required>
		<input type="submit" value="Войти">
	</form>
	<br><br>
	Регистр учитывается
	<br><br>
	<?php include ('error.php'); ?>
	</div>
</body>
</html>