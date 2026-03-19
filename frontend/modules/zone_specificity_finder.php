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
                    <div class="page-header-subtitle">Specificity Finder</div>
                    <div class="page-header-subtitle"><a class="btn btn-success" href="javascript:window.location.href='index?s=listprojects';">Back to project list</a></div>
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
                <div class="card-header">Cross-Search Definition</div>
                    <div class="text-left card-body" id="correlationmatrix">
                        <label class="small">
                            This tool compares energiy values of the current project with those of other projects with the same ligand.<br /><br />
                            - The dropdown only shows projects with the same protein ligand.<br />
                            - Some mutants should already be processed in both projects. Else the list is empty.<br /><br />

                                    </label> 
                        <div class="dropdown">
                            <button class="btn btn-primary dropdown-toggle" id="dropdownMenuButton" type="button" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Select Project...</button>
                            <div class="dropdown-menu" aria-labelledby="dropdownMenuButton" id="projectoptions">
                                <a class="dropdown-item" href="#!">please wait...</a>
                            </div>
                        </div>
                    </div>
            </div>                
        <!--FINISH Left Half-->
        </div>


        <!--Right Half-->
        <div class="col-lg-6">

                <!-- Area chart example-->
                <div class="card mb-4">
                    <div class="card-header">Query Results</div>
                    <div id="containerTable_hide" class="text-center card-body">Result table will be displayed here</div>
                    <div id="containerTable" class="text-center card-body invisible">
                        
                        <div class="text-left fs-3">Mutant Binding Energy Comparison</div>
                            <h6 class="card-title">(best mutants of current project vs. same mutants in compared project)</h6>
                            <table id="projectmatchtable" width="90%" class="text-center table display compact table-sm">
                                <thead>
                                    <th id="targetname"></th>
                                    <th>Mutations</th>
                                    <th>ΔG</th>
                                    <th>Difference</th>
                                    <th>ΔG</th>
                                    <th>Mutations</th>
                                    <th id="comparname"></th>
                                </thead>
                                <tbody id="mutant-table">
                                    <tr>
                                        <td></td> 
                                        <td></td> 
                                        <td></td> 
                                        <td></td> 
                                        <td></td> 
                                        <td></td> 
                                        <td></td> 
                                    </tr>
                                </tbody>
                            </table>
                            <br><br>
                            <table id="projectmatchtable2" width="90%" class="text-center table display compact table-sm">
                               <thead>
                                  <th>Wildtype ΔG (Current Project)</th>
                                  <th>Wildtype ΔG (Compared Project)</th>
                                </thead>
                                <tbody id="wildtype-table">
                                    <tr>
                                        <td id="t_wtenergy"></td> 
                                        <td id="c_wtenergy"></td> 
                                    </tr>
                                </tbody>
                            </table>
                    </div>
                    
                    
                </div>
                <div class="row">
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

   

<!-- MODAL WINDOWS OF THE SPECIFICITY FINDER-->
<!-- Modal Error-->
<div class="modal fade" id="wizzardModal" tabindex="-1" role="dialog" aria-labelledby="errorTitle" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="errorTitle">Warning!</h5>
                <button class="btn-close" type="button" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body" id="errorMessage">ERROR</div>
            <div class="modal-footer">
                <button class="btn btn-secondary" type="button" data-bs-dismiss="modal">Close</button>
                
        </div>
    </div>
</div>