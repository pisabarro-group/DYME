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
?>
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
                    <div class="page-header-subtitle">Job Control</div>
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
                <div class="card-header">Run Status</div>
                    <div class=" text-center card-body" id="infrastructure">
                        
                        
                    </div>
                <div class="card-footer small text-muted">Export XLS</div>
            </div>

                
        <!--FINISH Left Half-->
        </div>

        <!--Right Half-->
        <div class="col-lg-6">

                <!-- Area chart example-->
                <div class="card mb-4">
                    <div class="card-header">Project Deployment Control</div>
                    <div class="text-center card-body" id='deployment_table'>
                        
                    </div>
                    <div class="card-footer small text-muted">Export XLS</div>
                </div>
        <!--FINISH Right Half-->
        </div>
    </div>

    <div class="row center" >
        <div class="col-lg-12" >

            <!-- Area chart example-->
            <div class="card mb-12 min-vh-50">
                <div class="card-header text-left fs-3">Job Status Table</div>
                <div class="text-center card-body" id='job_status'>
                            <table id="datatablesjobs" class="text-center table display compact table-sm pageResize" style="width:100%">
                                <thead>
                                    <tr>
                                        <th></th>
                                        <th>Mutant ID</th>
                                        <th>Combination</th>
                                        <th>Status</th>
                                        <th>Start Date</th>
                                        <th>Elapsed</th>
                                        <th>Remaining</th>
                                        <th>Progress Complete</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                </tbody>
                            </table>
                </div>
                <div class="card-footer small text-muted">Export XLS</div>
            </div>
            <!--FINISH Right Half-->
        </div>             
    </div>
</div>



<!-- Modal -->
<div class="modal fade" id="staticBackdrop" tabindex="-1" role="dialog" aria-labelledby="staticBackdropLabel" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title justify-content-center" id="staticBackdropLabel">Warning!</h5>
      </div>
      <div class="modal-body">
            <div class="justify-content-center d-flex">
                Nothing to add. Mutations have to be different than wildtype
            </div>
      <div class="modal-footer"><button class="btn btn-secondary" type="button" data-bs-dismiss="modal">Close</button></div>
      </div>
    </div>
  </div>
</div>


<div class="modal fade" id="staticBackdrop2" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="staticBackdropLabel" aria-hidden="false">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title justify-content-center" id="staticBackdropLabel">Polling Job Status Data</h5>
      </div>
      <div class="modal-body">
            <div class="justify-content-center align-items-center d-flex">
                <div class="spinner-grow text-success" role="status"> 
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div class="spinner-grow text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div class="spinner-grow text-success" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>   
            </div>
            <br>

            <div class="justify-content-center d-flex">
                Please Wait
            </div>
      </div>
    </div>
  </div>
</div>
