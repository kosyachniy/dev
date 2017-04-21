<?php
require_once "twitter/twitteroauth.php";

$CONSUMER_KEY = "8Y2o5PjasQkVmvoxVQBLyVs4F";
$CONSUMER_SECRET = "2r4KPBm8kCcKsNrwkzSQRH4IkDqbxhVrgVcAmvfoyfXbZUNm1L";
$OAUTH_TOKEN = "3110781773-4I27iEchYIxqZmIQOgt18b2ehZUHkdEpWKRPuRO";
$OAUTH_SECRET = "OZj9w6TRUQoeVCgk3pShYOTFWasvSx3ebgOXn6lJQyngy";

/*
$CONSUMER_KEY = "jARMeUTgjWhDSWOSbs0pfQYz4";
$CONSUMER_SECRET = "stRnOnA3KRpaCI3hjyJyo0eLedQNflQ4FuvudvXj37mSLX7tPa";
$OAUTH_TOKEN = "4100776272-4VpvJNSkyhG9kWXfhRHyI3eTEeBRYRABiIqzusU";
$OAUTH_SECRET = "RHcdHHf0TyHBxtfxHyRCgmB41r7c6gnVgUHH7SEf1Uqi9";
*/

$tag=$_GET['t'];
if (!$tag)
	{
	$str=file_get_contents("http://t30p.ru/");
	$nom=strpos($str,'Тренды твиттера');
	$str=substr($str,$nom);
	$str=substr($str,strpos($str,"\">")+3,150);
	$tag=substr($str, 0, strpos($str,'</a>'));
	}

$connection = new TwitterOAuth($CONSUMER_KEY, $CONSUMER_SECRET, $OAUTH_TOKEN, $OAUTH_SECRET);
$content = $connection->get('account/verify_credentials');

do {$quote=file_get_contents("http://api.forismatic.com/api/1.0/?method=getQuote&format=text&language=ru");} while (mb_strlen($quote,'utf8')>(138-mb_strlen($tag,'utf8')));
//if(strlen($quote)>170) $quote = substr($quote, 0, 164)."...";
$quote.='
#'.$tag;

$connection->post('statuses/update', array('status' => $quote));
echo 'Размещена запись: "'.$quote.'"';
?>