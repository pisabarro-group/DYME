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
 * Repository: https://github.com/pguillem/DYME
 */

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
                        <div id="titlepage">Loading...</div>
                    </h1>
                    <div class="page-header-subtitle">Mutant Refinement Tool - Build your consensus mutants here</div>
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
            <div class="card mb-4 vh-100">
                <div class="card-header">Consensus Explorer</div>
                    <div class="card-body">
                    <label class="small">
                            Mutants marked as "Tagged" will appear here. <br> You can "tag/untag" a mutant from rhe Mutant explorer table

                            </label> 
                        
                    </div>
                <div class="card-footer small text-muted">Export to Excel</div>
            </div>

                
        <!--FINISH Left Half-->
        </div>







        <!--Right Half-->
        <div class="col-lg-6">

                <!-- Area chart example-->
                <div class="card mb-4">
                    <div class="card-header">Mutant Builder</div>
                    <div class="card-body">
                        <div class="chart-area"><div class="chartjs-size-monitor"><div class="chartjs-size-monitor-expand"><div class=""></div></div><div class="chartjs-size-monitor-shrink"><div class=""></div></div></div><canvas id="myAreaChart" width="885" height="240" style="display: block; width: 885px; height: 240px;" class="chartjs-render-monitor"></canvas></div>
                    </div>
                    <div class="card-footer small text-muted">Download to XLSX</div>
                </div>
                


        <!--FINISH Right Half-->
        </div>
    </div>
</div>





   

   