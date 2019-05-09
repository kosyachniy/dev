<?php
require_once '../../library/php/twitter/twitteroauth.php;

$CONSUMER_KEY = "8Y2o5PjasQkVmvoxVQBLyVs4F";
$CONSUMER_SECRET = "2r4KPBm8kCcKsNrwkzSQRH4IkDqbxhVrgVcAmvfoyfXbZUNm1L";
$OAUTH_TOKEN = "3110781773-4I27iEchYIxqZmIQOgt18b2ehZUHkdEpWKRPuRO";
$OAUTH_SECRET = "OZj9w6TRUQoeVCgk3pShYOTFWasvSx3ebgOXn6lJQyngy";

$url='http://t30p.ru/';
$contain='Тренды твиттера';
$start='">';
$stop='</a>';
$indent1=3;
$indent2=150;


$tag=$_GET['t'];
if (!$tag)
	{
	$str=file_get_contents($url);
	$str=substr($str,strpos($str,$contain));
	$str=substr($str,strpos($str,$start)+$indent1,$indent2);
	$tag=substr($str,0,strpos($str,$stop));
	}

$connection = new TwitterOAuth($CONSUMER_KEY,$CONSUMER_SECRET,$OAUTH_TOKEN,$OAUTH_SECRET);
$content=$connection->get('account/verify_credentials');

do
	{$quote=file_get_contents("http://api.forismatic.com/api/1.0/?method=getQuote&format=text&language=ru");}
while (mb_strlen($quote,'utf8')>(138-mb_strlen($tag,'utf8')));
//if(strlen($quote)>170) $quote = substr($quote, 0, 164)."...";
$quote.='
#'.$tag;

$connection->post('statuses/update', array('status' => $quote));
echo 'Размещена запись: "'.$quote.'"';
?>