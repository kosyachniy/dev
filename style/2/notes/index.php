<?php
include('../sys/func.php');
start('Статьи - ZODZU', 'notes', 'Статьи');
$db = db();

$i = $_GET['i'];
if ($i > 0) {
	print '<link rel="stylesheet" type="text/css" href="note.css"><div class="note">';

	$list = mysqli_query($db, "SELECT * FROM `notes` WHERE `id` = '$i'");
	while ($note = mysqli_fetch_array($list))
		print '<h1>' . $note['name'] . '</h1><img src="/load/img/' . $note['id'] . '.jpg"><div>' . $note['time'] . $note['cont'] . $note['tags'] . '</div>';

	print '</div>';
} else {
	print '<link rel="stylesheet" type="text/css" href="notes.css"><div class="notes">';

	$list = mysqli_query($db, "SELECT * FROM `notes` ORDER BY `priority` DESC");
	while ($note = mysqli_fetch_array($list))
		print '<a href="?i=' . $note['id'] . '"><div style="background-image: url(../load/img/' . $note['id'] . '.jpg);"><div>' . $note['name'] . '</div></div>';

	print '</div>';
}
?>

</body>
</html>