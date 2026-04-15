<?php
/**
 * Copyright (c) 2021-2025 Pedro Manuel Guillem-Gloria
 * Email: pedro_manuel.guillem_gloria@tu-dresden.de
 * University: Technische Universität Dresden 
 *
 * This file is part of the <DYME> project.
 * 
 ** This software is licensed under the **GNU General Public License v3 (GPLv3)**
 * 
 * License: See LICENSE file in the repository.
 * Repository: https://github.com/pguillem/DYME
 */

 //CHECK USER POST
	$notlogged = false;
	if(isset($_POST['uname'])){
		$uname = $_POST['uname'];
		$pswd  = $_POST['pass'];

		if (pam_auth($uname, $pswd, $error)){
			session_start();
			$_SESSION['username'] = addslashes($uname);
			$_SESSION['profile']  = "bioinfp";
			$_SESSION["uid"] = uniqid();
			header("Location: index.php");
		} else {
			session_destroy();
			$notlogged = true;
			$msg = "Invalid Auth: (".$error.")";
		}
	}
	
	//CHECK IF LOGOUT
	if(isset($_GET["log"])){
		if($_GET["log"] == "logout"){
			session_destroy();
		}
	}
 ?>
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!--Font Awesome -->
<link rel="stylesheet" href="./css/fontawesome/css/all.min.css" />

<!--DYME Style -->
<link rel="stylesheet" href="./css/style.css" />

<!-- Bootstrap -->
<link rel="stylesheet" href="./css/bootstrap/css/bootstrap.min.css" />

<title>Login | Dynamic Mutagenesis Engine</title>
</head>


<body onload="ifnotlogged(<?php echo $notlogged ?>)">

<!--DYME Login-->
<header>
	<script>
		function ifnotlogged(action){
			if(action){
				alert("Error: ".<?php=$msg?>)
			}
		}
	</script>
	<div class="view video-container">
		<video src="./img/bglogin.mp4" autoplay muted loop></video>
	</div>

	<div class="container">
		<div class="row pt-5">
			<div class="mx-auto col-xl-5 mb-4 mt-5 pt-5">
				<div class="card">
					<form action="login.php" method="POST">
						<div class="card-body">
						  <div class="text-center">
							<h3 class="text-white">DYME - Login</h3>
							<hr />
						  </div>

						  <div class="form-group">
							<i class="fas fa-user text-white"> </i>
							<label class="text-white" for="name">Username</label>
                                                        <input
type="text"
id="name"
name="name"
class="form-control"
required 
							/>


						  </div>

						 <div class="form-group">
							<i class="fas fa-user text-white"> </i>
							<label class="text-white" for="pass">password</label>
                                                        <input
type="password"
id="pass"
name="pass"
class="form-control"
required 
							/>
						  </div>

						  <div class="text-center mt-5">
						  <button name="login_now" type="submit" class="myButton"> Login </button>
						  </div>
						</div>
					</form>
				</div>
			</div>
		</div>
	</div>

</header>



<!--DYME Login-->


<!--Script-->
<script src="./js/jquery/jquery-3.6.0.min.js">
<script src="./js/popper/popper.min.js">
<script src="./js/bootstrap/bootstrap.min.js">

</body>


</html>
