<?php
error_reporting(E_ALL);
$file=file_get_contents('https://www.google.com/');
die($file);
?>