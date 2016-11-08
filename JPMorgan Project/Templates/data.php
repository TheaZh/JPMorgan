<?
$dbhost = 'localhost';
$dbuser = 'root';
$dbpass = '';
$dbname = 'user_info';

$conn = mysql_connect($dbhost, $dbuser, $dbpass);
mysql_select_db($dbname);

?>

<table width="300" border="1">
	<tr>
		<td><b>TimeStamp</b></td>
		<td><b>Username</b></td>
		<td><b>Qty</b></td>
	</tr>
	<?

	$sql = "
		SELECT timestamp,username,qty
		FROM trade_history
		";
	$result = mysql_query($sql);
	while($row = mysql_fetch_array($result))
	{

	?>
	<tr>
		<td><? echo $row['timestamp']; ?></td>
		<td><? echo $row['username']; ?></td>
		<td><? echo $row['qty']; ?></td>
	</tr>
	<?
	}
	?>
</table>
