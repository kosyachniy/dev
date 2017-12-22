<?php
session_start();
$_SESSION['auth'] = 0;
$str = $_SERVER['HTTP_REFERER'];
header("location: " . $str);
?>