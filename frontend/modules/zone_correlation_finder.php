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
                        <div id="titlepage">Loading...</div>
                    </h1>
                    <div class="page-header-subtitle">Correlation Explorer / A.I Driven modelling</div>
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
                <div class="card-header">Ligand-Ligand Correlation Matrix</div>
                    <div class=" text-center card-body" id="correlationmatrix">
                        <div><br /> </div>
                        <div><br /></div>
                        <div class="spinner-border" role="status"> </div> 

                        &nbsp;
                        <br /><br />
                        <div class="d-flex justify-content-center align-middle"><h5>Generating Correlation Matrix</h5></div>
                    </div>
                <div class="card-footer small text-muted">Export to Excel</div>
            </div>

                
        <!--FINISH Left Half-->
        </div>







        <!--Right Half-->
        <div class="col-lg-6">

                <!-- Area chart example-->
                <div class="card mb-4">
                    <div class="card-header">A.I Based Energy Predictor</div>
                    <div class="text-center card-body" id='neuralcontainer'>
                        <div><br /> </div>
                        <div><br /></div>
                        <div class="spinner-border" role="status"> </div> 

                        &nbsp;
                        <br /><br />
                        <div class="d-flex justify-content-center align-middle"><h5>Recalibrating Neural Network. Please be patient</h5></div>
                        <div class="log-box" id="neuralprogress"></div>
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
                <div class="card-header">Mutant Predictor</div>
                <div class="card-body">
                    
                    <div class="row">
                        <div class="col-3">
                            <div class="text-left fs-3">Mutant Builder</div>
                            <label class="small">
                               Test a arbitraty mutant by assigning a residues to each anchorpoint. Then click "Add to Queue". You can add as many as desired.
                            </label> <p></p>
                            <div class="row">
                                <div class="col-8" id="anchorpointlist"> 
                                                        
                                </div>  
                                <div class="col-4 d-flex align-items-center justify-content-center"> 
                                    <button class="btn btn-primary btn" onclick="getAnchorSelects()">Add to Queue</button>
                                </div>
                            </div>
                        </div>
                        <div class="vr"></div>
                        <div class="col-5">
                        <div>
                            <div class="text-left fs-3">Mutant Queue Table</div>
                                <label class="small">
                                    When you are ready, click the "Predict" button to estimate the ΔG of the enqueued mutants.<br />
                                </label> 
                                <table id="datatablesmutants" width="40%" class="text-center table display compact table-sm">
                                    <thead>
                                        
                                        <th>Mutations</th>
                                        <th>Predicted ΔG (kcal/mol)</th>
                                        <th>Actions</th>
                                    </thead>
                                    <tbody id="mutant-table">
                                        <tr>
                                            
                                            <td class='text-left'></td> 
                                            <td></td> 
                                            <td></td> 
                                        </tr>
                                    </tbody>

                                </table>
                                <div class="d-flex align-items-center justify-content-center"> 
                                    <button id='predict' class="btn btn-primary btn" onclick="testMutants()" disabled>Predict ΔG</button>
                                </div>
                            </div>

                        </div>

                </div>
                <div class="card-footer small text-muted">Test</div>
            </div>
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

   

   