<?php
/**
 * Copyright (c) 2021-2025 Pedro Manuel Guillem-Gloria
 * Email: pedro_manuel.guillem_gloria@tu-dresden.de
 * University: Technische Universität Dresden 
 *
 * This file is part of the <DYME> project.
 * 
 ** This software is licensed under the **GNU General Public License v3 (GPLv3)**
 ** for academic and scientific purposes only**
 *
 * This software may NOT be used for commercial purposes without a **separate commercial license**  
 * 
 * License: See LICENSE file in the repository.
 * Repository: https://github.com/pisabarro-group/DYME
 */

//Load GUI configs
$ip_server = $_SERVER['SERVER_ADDR'];

//Include
require_once("include/config.php");

 //No cache please
 header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
 header("Cache-Control: post-check=0, pre-check=0", false);
 header("Pragma: no-cache");

session_start();
/*
if(!isset($_SESSION["uid"])){
    session_destroy();
    header("Location: login.php");
} else {
    //Session vars
    $uid      = $_SESSION["uid"];
    $username = $_SESSION["username"];
    //$name     = $_SESSION["person_name"];
}
*/

if(isset($_GET["s"])){
    //$db = new MongoDB\Driver\Manager("mongodb://localhost:27017");
}

$id_project = addslashes($_GET["id"]);

//Things to do when there the module is mainproject
if($_GET["s"] == "mainproject" || $_GET["s"] == "mainproject_rest"){
    $toggle = "";
} else {
    $toggle = "sidenav-toggled";
}


?>

<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        <meta name="description" content="" />
        <meta name="author" content="" />
        <title>DYME - Dynamic Mutagenesis Engine</title>
        <link href="css/styles.css" rel="stylesheet" />
        <link href="css/jquery-ui.min.css" rel="stylesheet" />
        <link href="css/colorPick.css" rel="stylesheet" />
        <link href="css/datatables.min.css" rel="stylesheet" />
        <link href="css/comparisonTable.css" rel="stylesheet" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-slider/11.0.2/css/bootstrap-slider.css" integrity="sha512-SZgE3m1he0aEF3tIxxnz/3mXu/u/wlMNxQSnE0Cni9j/O8Gs+TjM9tm1NX34nRQ7GiLwUEzwuE3Wv2FLz2667w==" crossorigin="anonymous" />
        <link rel="icon" type="image/x-icon" href="assets/img/favicon.png" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery-contextmenu/2.7.1/jquery.contextMenu.min.css">
        <link rel="stylesheet" href="css/SwipeableMultiselect.css">
        

        <style>
            .minibox {
                height: 15px;
                width: 15px;
                
                display: inline-block;                
            }
            .custom-seqwidth {
                width: 16px !important;
                font-family: 'Courier New', Courier, monospace !important;
                font-size: 15px !important;
            }

            .custom-seqmut {
               color: red !important; 
               font-weight: bold !important;
            }

            #slider-div {
            display: flex;
            flex-direction: row;
            margin-top: 30px;
            }

            #slider-div>div {
            margin: 8px;
            }

            .slider-label {
            position: absolute;
            background-color: #eee;
            padding: 4px;
            font-size: 0.75rem;
            }

            .equidistant-cols {
                table-layout: fixed;
            }

            /* Custom CSS for the log box */
            .log-box {
            border: 0px solid #ccc;
            padding: 10px;
            height: 200px;
            overflow: auto;
            font-size: 15px;
            text-align: left;
            flex-direction: column-reverse;
            }

            .rowTagged{
                background-color: #fffec8 !important; 
            }

            .lightBlue {
                background-color: #add8e6 !important;
                height: 15px;
            }

            .details-control {
                background: url('img/details_open.png') no-repeat center center;
                cursor: pointer;
            }
            tr.shown .details-control {
                background: url('img/details_close.png') no-repeat center center;
            }

        </style>

        <script data-search-pseudo-elements defer src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/js/all.min.js" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/feather-icons/4.28.0/feather.min.js" crossorigin="anonymous"></script>

    </head>
    <body class="nav-fixed <?=$toggle?> d-flex flex-column min-vh-100">
        <nav class="topnav navbar navbar-expand shadow justify-content-between justify-content-sm-start navbar-light bg-white" id="sidenavAccordion">
            <!-- Sidenav Toggle Button - SHOW ONLY ON MAINPROJECT AREA FOR NOW-->
            <?php
            if($_GET["s"] == "mainproject" || $_GET["s"] == "mainproject_rest"){
            ?>
                <button class="btn btn-icon btn-transparent-dark order-1 order-lg-0 me-2 ms-lg-2 me-lg-0" id="sidebarToggle"><i data-feather="menu"></i></button>
            <?php
            }
            ?>
            <a class="navbar-brand pe-3 ps-4 ps-lg-2" href="index">DYME - Dynamic Mutagenesis Engine</a>
            <!-- Navbar Search Input-->
            <!-- * * Note: * * Visible only on and above the lg breakpoint-->
            
            <!-- Navbar Items-->
            <ul class="navbar-nav align-items-center ms-auto">
                
                <!-- Alerts Dropdown-->
                <li class="nav-item dropdown no-caret d-none d-sm-block me-3 dropdown-notifications">
                    <a class="btn btn-icon btn-transparent-dark dropdown-toggle" id="navbarDropdownAlerts" href="javascript:void(0);" role="button" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><i data-feather="bell"></i></a>
                    <div class="dropdown-menu dropdown-menu-end border-0 shadow animated--fade-in-up" aria-labelledby="navbarDropdownAlerts">
                        <h6 class="dropdown-header dropdown-notifications-header">
                            <i class="me-2" data-feather="bell"></i>
                            Alerts Center
                        </h6>
                        <!-- Example Alert 1-->
                        <a class="dropdown-item dropdown-notifications-item" href="#!">
                            <div class="dropdown-notifications-item-icon bg-warning"><i data-feather="activity"></i></div>
                            <div class="dropdown-notifications-item-content">
                                <div class="dropdown-notifications-item-content-details">December 29, 2021</div>
                                <div class="dropdown-notifications-item-content-text">This is an alert message. It's nothing serious, but it requires your attention.</div>
                            </div>
                        </a>
                        <!-- Example Alert 2-->
                        <a class="dropdown-item dropdown-notifications-item" href="#!">
                            <div class="dropdown-notifications-item-icon bg-info"><i data-feather="bar-chart"></i></div>
                            <div class="dropdown-notifications-item-content">
                                <div class="dropdown-notifications-item-content-details">December 22, 2021</div>
                                <div class="dropdown-notifications-item-content-text">A new monthly report is ready. Click here to view!</div>
                            </div>
                        </a>
                        <!-- Example Alert 3-->
                        <a class="dropdown-item dropdown-notifications-item" href="#!">
                            <div class="dropdown-notifications-item-icon bg-danger"><i class="fas fa-exclamation-triangle"></i></div>
                            <div class="dropdown-notifications-item-content">
                                <div class="dropdown-notifications-item-content-details">December 8, 2021</div>
                                <div class="dropdown-notifications-item-content-text">Critical system failure, systems shutting down.</div>
                            </div>
                        </a>
                        <!-- Example Alert 4-->
                        <a class="dropdown-item dropdown-notifications-item" href="#!">
                            <div class="dropdown-notifications-item-icon bg-success"><i data-feather="user-plus"></i></div>
                            <div class="dropdown-notifications-item-content">
                                <div class="dropdown-notifications-item-content-details">December 2, 2021</div>
                                <div class="dropdown-notifications-item-content-text">New user request. Woody has requested access to the organization.</div>
                            </div>
                        </a>
                        <a class="dropdown-item dropdown-notifications-footer" href="#!">View All Alerts</a>
                    </div>
                </li>
               
                <!-- User Dropdown-->
                <li class="nav-item dropdown no-caret dropdown-user me-3 me-lg-4">
                    <a class="btn btn-icon btn-transparent-dark dropdown-toggle" id="navbarDropdownUserImage" href="javascript:void(0);" role="button" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><img class="img-fluid" src="assets/img/illustrations/profiles/profile-1.png" /></a>
                    <div class="dropdown-menu dropdown-menu-end border-0 shadow animated--fade-in-up" aria-labelledby="navbarDropdownUserImage">
                        <h6 class="dropdown-header d-flex align-items-center">
                            <img class="dropdown-user-img" src="assets/img/illustrations/profiles/profile-1.png" />
                            <div class="dropdown-user-details">
                                <div class="dropdown-user-details-name">Pedro Guillem</div>
                                <div class="dropdown-user-details-email">pedro_manuel.guillem_gloria@tu-dresden.de</div>
                            </div>
                        </h6>
                        <div class="dropdown-divider"></div>
                        <a class="dropdown-item" href="#!">
                            <div class="dropdown-item-icon"><i data-feather="settings"></i></div>
                            Account
                        </a>
                        <a class="dropdown-item" href="login.php?log=logout">
                            <div class="dropdown-item-icon"><i data-feather="log-out"></i></div>
                            Logout
                        </a>
                    </div>
                </li>
            </ul>
        </nav>

		
        <div id="layoutSidenav">
            <div id="layoutSidenav_nav">
                <nav class="sidenav shadow-right sidenav-light">
                <?php
                    if($_GET["s"] == "mainproject" || $_GET["s"] == "mainproject_rest"){
                
                ?>    
                    <div class="sidenav-menu">
                            <div class="nav accordion" id="accordionSidenav">

                                <!--PIPELINE CONTROL-->
                                <div class="sidenav-menu-heading">DYME CONTROL</div>
                                <a class="nav-link" href="javascript:void(0);" data-bs-toggle="collapse" data-bs-target="#collapseProcess" aria-expanded="true" aria-controls="collapseProcess">
                                    <div class="nav-link-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-repeat"><polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path></svg></div>
                                    Project Explorer
                                    <div class="sidenav-collapse-arrow"><svg class="svg-inline--fa fa-angle-down" aria-hidden="true" focusable="false" data-prefix="fas" data-icon="angle-down" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" data-fa-i2svg=""><path fill="currentColor" d="M192 384c-8.188 0-16.38-3.125-22.62-9.375l-160-160c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L192 306.8l137.4-137.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-160 160C208.4 380.9 200.2 384 192 384z"></path></svg><!-- <i class="fas fa-angle-down"></i> Font Awesome fontawesome.com --></div>
                                </a>
                                <div class="collapse show" id="collapseProcess" data-bs-parent="#accordionSidenav" style="">
                                    <nav class="sidenav-menu-nested nav accordion" id="accordionSidenavPages">
                                        <a class="nav-link" href="index.php?s=mainproject_rest&id=<?=$id_project?>&zone=dashboard" onclick="loadDashboard()">Dashboard</a>
                                        <a class="nav-link" href="index.php?s=mainproject_rest&id=<?=$id_project?>&zone=jobcontrol" onclick="loadJobManager()">Job Manager</a>
                                    </nav>
                                </div>



                                <!--DYME EXPLORATION -->
                                <div class="sidenav-menu-heading">PROJECT WORKSPACE</div>
                                <a class="nav-link" href="javascript:void(0);" data-bs-toggle="collapse" data-bs-target="#collapseDashboards" aria-expanded="true" aria-controls="collapseDashboards">
                                    <div class="nav-link-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-bar-chart"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg></div>
                                    Assessment Tools
                                    <div class="sidenav-collapse-arrow"><svg class="svg-inline--fa fa-angle-down" aria-hidden="true" focusable="false" data-prefix="fas" data-icon="angle-down" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" data-fa-i2svg=""><path fill="currentColor" d="M192 384c-8.188 0-16.38-3.125-22.62-9.375l-160-160c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L192 306.8l137.4-137.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-160 160C208.4 380.9 200.2 384 192 384z"></path></svg><!-- <i class="fas fa-angle-down"></i> Font Awesome fontawesome.com --></div>
                                </a>
                                <div class="collapse show" id="collapseDashboards" data-bs-parent="#accordionSidenav" style="">
                                    <nav class="sidenav-menu-nested nav accordion" id="accordionSidenavPages">
                                        <a class="nav-link <?php if ($_GET['zone']=='exploration_mutant') echo 'active'?>" href="index.php?s=mainproject&id=<?=$id_project?>&zone=exploration_mutant">Mutant Explorer</a>
                                        <!--<a class="nav-link <?php if ($_GET['zone']=='refinement_mutant') echo 'active'?>" href="index.php?s=mainproject&id=<?=$id_project?>&zone=refinement_mutant">Mutant Refinery</a>-->
                                        <a class="nav-link <?php if ($_GET['zone']=='specificity_finder') echo 'active'?>" href="index.php?s=mainproject&id=<?=$id_project?>&zone=specificity_finder">Specificity Finder</a>
                                        
                                        <!--<a class="nav-link <?php if ($_GET['zone']=='cluster_factory') echo 'active'?>" href="index.php?s=mainproject&id=<?=$id_project?>&zone=cluster_factory">Re-clustering</a>-->
                                    </nav>
                                </div>
                                

                                <!--DYME EXPLORATION 
                                <div class="sidenav-menu-heading">MOLECULAR DESIGN </div>
                                <a class="nav-link " href="charts.html">
                                    <div class="nav-link-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-grid"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg></div>
                                    Pharmacophore Builder
                                </a>

                                <a class="nav-link" href="javascript:void(0);" data-bs-toggle="collapse" data-bs-target="#collapsePharmacophore" aria-expanded="true" aria-controls="collapsePharmacophore">
                                    <div class="nav-link-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-globe"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg></div>
                                    Virtual Screening
                                    <div class="sidenav-collapse-arrow"><svg class="svg-inline--fa fa-angle-down" aria-hidden="true" focusable="false" data-prefix="fas" data-icon="angle-down" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" data-fa-i2svg=""><path fill="currentColor" d="M192 384c-8.188 0-16.38-3.125-22.62-9.375l-160-160c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L192 306.8l137.4-137.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-160 160C208.4 380.9 200.2 384 192 384z"></path></svg></div>
                                </a>

                                <div class="collapse show" id="collapsePharmacophore" data-bs-parent="#accordionSidenav" style="">
                                    <nav class="sidenav-menu-nested nav accordion" id="accordionSidenavPages">
                                        <a class="nav-link" href="#" onclick="loadMutantExplorer()">Import Libraries</a>
                                        <a class="nav-link" href="#"  onclick="loadAnchorExplorerr()">Deploy Screening</a>
                                        <a class="nav-link" href="#"  onclick="loadAnchorExplorerr()">Monitor Jobs</a>
                                    </nav>
                                </div>
                                -->                                




                            </div>
                    </div>
                <?php
                }
                ?>

                </nav>
            </div>
			

			<div id="layoutSidenav_content">


                <main>
                    <?php
                    if($_GET["s"] == ""){
                        include_once("modules/init_screen.php");
                    } else {
                        $s = addslashes($_GET["s"]).".php";
                        include_once("modules/".$s);
                    }

                    //If the zone is defined - Load the zone template in the layout
                    if(isset($_GET['zone'])){
                        if($_GET['zone'] != ""){
                            $z = addslashes($_GET['zone']);
                            include_once("modules/zone_".$z.".php");
                        }
                    }
                    ?>
                </main>


                <footer class="footer-admin mt-auto footer-light">
                    <div class="container-xl px-4">
                        <div class="row ">
                            <div class="col-md-6 small ">Copyright &copy; Structural Bioinformatics Laboratory - BIOTEC, TU-Dresden, 2021-2025</div>
                            <div class="col-md-6 text-md-end small">
                            </div>
                        </div>
                    </div>
                </footer>



            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" crossorigin="anonymous"></script>
        <script src="https://code.jquery.com/jquery-3.6.1.min.js" integrity="sha256-o88AwQnZB+VDvE9tvIXrMQaPlFFSUTR+nldQm1LuPXQ=" crossorigin="anonymous"></script>
        <script src="js/jquery/jquery-ui.min.js" crossorigin="anonymous"></script>
        <!--<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.min.js" crossorigin="anonymous"></script>-->
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/hammerjs@2.0.8"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-zoom/2.0.1/chartjs-plugin-zoom.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-contextmenu/2.7.1/jquery.contextMenu.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-contextmenu/2.7.1/jquery.ui.position.js"></script>
        

        <script src="js/scripts.js"></script>

        <script src="js/colorpicker/colorPick.min.js"></script>
        <script src="js/ngl2.js?<?=rand(1,10000000)?>"></script>
        <!--This is your general GUI functions -->
        <script src="js/dyme.js?<?=rand(1,10000000)?>"></script>
        <script src="js/combinatorials.js"></script>
        <script src="js/datatables/datatables.min.js"></script>
        <script src="js/charts-js-error.js"></script>
        <script src="js/chartjs-plugin-datalabels.js"></script>
        <script src="js/chartjs-chart-matrix@1.js"></script>
        <script src="js/logojs.js" type="text/javascript"></script>
        <script src="js/SwipeableMultiselect.js?<?=rand(1,10000000)?>" type="text/javascript"></script>
        <script src="js/html2canvas.js?<?=rand(1,10000000)?>" type="text/javascript"></script>

        <script>
        
        apiUrl = "<?php echo $api_url ?>";
        
        <?php
        //Load Additional Script helpers for each module (if file exists)
        if($_GET["s"] == ""){
            //include_once("modules/init_screen.php");
        } else {
                $s = addslashes($_GET["s"]).".js";
                $z = addslashes($_GET["zone"]).".js";
                include_once("js/modules/".$s);
                include_once("js/modules/zone_".$z);
        }
        ?>

        </script>


    </body>
</html>