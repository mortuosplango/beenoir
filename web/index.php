<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xml:lang="de" lang="de">
    <head>
        <title>alj</title>
    </head>
    <body>
   <form action="index.php" method="post">
   <fieldset>
   <legend>Eingeben:</legend>
  <p>
   <table>
   <tr>
   <?php
   for ($i=0; $i<8; $i++) {
     if( $i == 4) {
       echo '</tr><tr>';
     };
    echo '<td><select name="code'.$i.'" size="5">
      <option value="0" selected>wait</option>
      <option value="1">move</option>
      <option value="2">turn right</option>
      <option value="3">turn left</option>
      <option value="4">action</option>
    </select></td>';
   }
   ?>
   </tr></table>
  </p>

   <label>ID: <input type="text" name="playerID" /></label>
   <input type="submit" name="formaction" value="update" />
   </fieldset>
</form>

    </body>
</html>
<?php
include 'OSC.php';
if ($_POST['playerID']) {
  echo '<h2>updated '.$_POST['playerID'].'!</h2>';
  $c = new OSCClient();
  $c->set_destination("127.0.0.1", 57120);
  $c->send(new OSCMessage("/alj/code", array(1,2,3)));
			  /* array($_POST['playerID'],
				$_POST['code0'],$_POST['code1'],
				$_POST['code2'],$_POST['code3'],
				$_POST['code4'],$_POST['code5'],
				$_POST['code6'],$_POST['code7'])));*/   
};
?>

</html>


