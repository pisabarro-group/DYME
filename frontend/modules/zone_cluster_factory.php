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

#Sets Projectid Value for this template
#Missing obvious secutiry features... quick n dirty
$id_project = addslashes($_GET["id"]);
echo "<input type='hidden' value='$id_project' name='idproject' id='idproject'>";
?>

<header class="page-header page-header-dark bg-gradient-primary-to-secondary pb-10">
    <div class="container-fluid px-4">
        <div class="page-header-content pt-4">
            <div class="row align-items-center justify-content-between">
                <div class="col-auto mt-4">
                    <h1 class="page-header-title">
                        <div class="page-header-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-layout"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg></div>
                        Project RBX1/GLMN
                    </h1>
                    <div class="page-header-subtitle">Regardless of screen size, this layout style will keep expanding to take up the whole width of the screen</div>
                </div>
            </div>
        </div>
    </div>
</header>


<div class="container-fluid px-4 mt-n10">
    <div class="row">

        <!--Left Half-->
        <div class="col-lg-6">

            <!-- Area chart example-->
            <div class="card mb-4 vh-75">
                <div class="card-header">Anchorpoint Adjustments</div>
                    <div class="card">
                                        <div class="card-body">
                                            
                                            <div class="text-center" id="anchorpointlist"> 
                                                
                                            </div>
                                            
                                        </div>
                    </div>
                <div class="card-footer small text-muted"></div>
            </div>

                
        <!--FINISH Left Half-->
        </div>







        <!--Right Half-->
        <div class="col-lg-6">

                <!-- Area chart example-->
                <div class="card mb-4">
                    <div class="card-header">Clustering</div>
                    <div class="card-body">
                        
                    </div>
                    <div class="card-footer small text-muted">Export PNG</div>
                </div>
                <div class="row">
        <!--FINISH Right Half-->
        </div>
    </div>
    <div class="row">
        <div class="col-lg-12">
            <!-- Bar chart example-->
            <div class="card mb-4">
                <div class="card-header">Review & Launch Jobs</div>
                <div class="card-body">
                    <div class="chart-bar"><div class="chartjs-size-monitor"><div class="chartjs-size-monitor-expand"><div class=""></div></div><div class="chartjs-size-monitor-shrink"><div class=""></div></div></div><canvas id="myBarChart" width="408" height="240" class="chartjs-render-monitor" style="display: block; width: 408px; height: 240px;"></canvas></div>
                </div>
                <div class="card-footer small text-muted">Updated yesterday at 11:59 PM</div>
            </div>
        </div>
    </div>

</div>
