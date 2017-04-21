<?php
$file=fopen('db.txt','w');

$link='http://russian2015.ucoz.com/publ/podgotovka_k_ogeh_po_russkomu_jazyku/5-';
$str='/publ/podgotovka_k_ogeh_po_russkomu_jazyku/szhatoe_izlozhenie_po_tekstu';
$not='#comments';
$n=9;

for ($i=1; $i<=$n; $i++)
  {
  $f=fopen($link.$i, 'r');
  while (!feof($f))
    {
    $line=fgets($f);
    if (stripos($line, $str))
      {
      $line=substr($line, stripos($line, $str));
      $line=substr($line, 0, stripos($line, '"'));
      if (!stripos($line, $not)) fwrite($file, $line.'
');
      }
    }
  fclose($f);
  }

fclose($file);
?>