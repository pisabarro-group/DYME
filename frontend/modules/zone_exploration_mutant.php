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
 * Repository: https://github.com/pisabarro-group/DYME
 */

#Missing obvious secutiry features (like preventing unauthorized lab members to open this)

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
                    <div class="page-header-subtitle">Mutant Explorer</div>
                    <div class="page-header-subtitle"><a class="btn btn-success" href="javascript:window.location.href='index?s=listprojects';">Back to project list</a></div>
                    
                </div>
            </div>
        </div>
    </div>
</header>


<div class="container-fluid px-4 mt-n10">
    <div class="row">

        <!--Left Half-->
        <div class="col-lg-3">
            <!-- Area chart example-->
            <div class="card mb-3 min-vh-100 ">
                <div class="card-header">Mutant Simulation Results</div>
                <div class="col-lg-12 card">
                    <div class="card-body">
                        <div class="text-center">
                            <h6>Binding Energy Thresholds</h6>
                        </div>
                        <div id="slider-outer-div text-center">
                            <div id="slider-div"  class="card">
                                <div class="col-3 text-center" data-bs-toggle="tooltip" data-bs-placement="top" title="Worst" id="worse"></div>
                                <div class="col-6">
                                    <input width="100%" type="range" data-bs-toggle="tooltip" data-bs-placement="top" title="WT ()" class="form-range" value="83" min="28" max="114" id="disabledRange">
                                </div>
                                <div class="col-3 text-center" data-bs-toggle="tooltip" data-bs-placement="top" title="Best" id="best"></div>
                            </div>
                        </div>
                        <p>
                        <div class="text-center">
                            <h6>Statistical Summary Data</h6>
                            <label class="small">(All values are in kcal/mol)</h6>
                            <table id="datatableswildtype" width="100%" class="text-center table equidistant-cols  table-sm display nowrap compact">
                                <thead>
                                    <th>Mutants</th>
                                    <th>Mean</th>
                                    <th>STD</th>
                                    <th>Baseline</th>
                                    <th>Worst</th>
                                    <th>Best</th>
                                    <th>Gain</th>

                                </thead>
                                <tbody>
                                    <tr>
                                        <td id="series-count"><span class="spinner-border spinner-border-sm"></span></td> 
                                        <td id="series-mean"><span class="spinner-border spinner-border-sm"></td> 
                                        <td id="series-std"><span class="spinner-border spinner-border-sm"></td> 
                                        <td id="series-base" class="text-primary fw-bold"><span class="spinner-border spinner-border-sm"></td> 
                                        <td id="series-worst"><span class="spinner-border spinner-border-sm"></td> 
                                        <td id="series-best"><span class="spinner-border spinner-border-sm"></td> 
                                        <td id="series-gain" class="text-success fw-bold"><span class="spinner-border spinner-border-sm"></td>
                                    </tr>
                                </tbody>
                                <thead>
                                    <th colspan="8">ΔG Percentiles</th>
                                </thead>
                                <thead>
                                    <th>99.9%</th>
                                    <th>99%</th>
                                    <th>95%</th>
                                    <th>90%</th>
                                    <th>80%</th>
                                    <th>50%</th>
                                    <th>20%</th>
                                    <th>10%</th>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td id="series-001"><span class="spinner-border spinner-border-sm"></td> 
                                        <td id="series-01"><span class="spinner-border spinner-border-sm"></td> 
                                        <td id="series-5"><span class="spinner-border spinner-border-sm"></td> 
                                        <td id="series-10"><span class="spinner-border spinner-border-sm"></td> 
                                        <td id="series-20"><span class="spinner-border spinner-border-sm"></td> 
                                        <td id="series-50"><span class="spinner-border spinner-border-sm"></td> 
                                        <td id="series-80"><span class="spinner-border spinner-border-sm"></td> 
                                        <td id="series-90"><span class="spinner-border spinner-border-sm"></td> 
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <p>
                        <div>
                            <div class="text-left fs-3">Mutant Summary </div>
                            <div class="d-flex align-items-center justify-content-evenly">
                                <h6 class="card-title position-relative">(double click a mutant to add to the session)</h6>
                                <button class="btn btn-success position-relative" type="button" data-bs-toggle="modal" data-bs-target="#filterModal" onclick="renderFilterOptions()">Advanced Filter</button>
                                <button class="btn btn-secondary position-relative" type="button" onclick="clearSearch()">Clear Search</button>
                                
                            </div>
                            <table id="datatablesmutants" width="100%" class="text-center table display compact table-sm">
                                <thead>
                                    <th>ID</th>
                                    <th>Cluster</th>
                                    <th>Type</th>
                                    <th>Mutations</th>
                                    <th>ΔG (kcal/mol)</th>
                                    <th>Diff</th>
                                    <th></th>
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
                        </div>
                        </p>

                    </div>
                </div>

                

                <div class="col-lg-12 card" id="contactPNG">                    
                    <div class="card-body">
                            <h5 class="card-title">Interface Contact Explorer</h5>
                            <div>
                                <p>&nbsp;<button class="btn btn btn-outline-dark" onclick="reverseContactTable()">Reverse Matrix</button>
                                <button class="btn btn btn-outline-dark" onclick="changeThreshold(10)">10%</button>
                                <button class="btn btn btn-outline-dark" onclick="changeThreshold(20)">20%</button>
                                <button class="btn btn btn-outline-dark" onclick="changeThreshold(50)">50%</button></p>
                                <table class="tableMutants" id="tableMutantsContacts">
                                    <thead id="header-row">
                                        
                                    </thead>

                                    <tbody id="table-body">
                                        
                                    </tbody>
                                </table>    
                                <p>&nbsp;</p>
                                <button class="btn btn-sm btn-outline-dark" onclick="exportPNG('contact')">Export PNG</button>
                                <!--<button class="btn btn-sm btn-outline-dark" onclick="exportXLS('contact')">Export XLS</button>-->
                            </div>
                    </div>
                </div>

                <div class="col-lg-12 card">                    
                    <div class="card-body">
                            <h5 class="card-title">Water Site Explorer</h5>
                            <div>
                                <table id="datatablesWaters-general" width="100%" class="text-center table display compact table-sm">
                                    <thead>
                                        <th>MutantID</th>
                                        <th>Sites</th>
                                        <!--<th>HeavyAtoms</th>-->
                                        <th>Interfacial waters</th>
                                        <th></th>
                                    </thead>
                                    <tbody id="table-waters-body-front">
                                       <tr><td colspan="4">Loading water sites</td></tr>
                                    </tbody>
                                </table>    
                                <p>&nbsp;</p>
                            </div>
                    </div>
                </div>


                
            </div>    
        <!--FINISH Left Half-->
        </div>




        <!--Right Half-->
        <div class="col-lg-9">
                <!-- Area chart example-->
                <div class="card mb-4 min-vh-100 w-100">
                    <div class="card-header">Data Viewer</div>
                    <div class="card-body overflow-auto">
                        <div class="row vh-50">

                            <div class="col-lg-2 card" >
                                <div class="card-body">
                                    <h6 class="card-title">Scene Control</h6>
                                    <button class="btn btn-sm btn-outline-dark w-100" onclick="ngl_reset_view()">Reset View</button>
                                    <button class="btn btn-sm btn-outline-dark w-100" onclick="ngl_toggle_spin()">Spin on/off</button>
                                    <!--<button class="btn btn-sm btn-outline-dark w-100">Toggle Lines</button>-->
                                    <!--<button class="btn btn-sm btn-outline-dark w-100">Toggle Surface</button>-->
                                    <!--<button class="btn btn-sm btn-outline-dark w-100">Toggle Contacts</button>-->
                                    <br />
                                    <br />
                                    <h6 class="card-title">Display Control</h6>
                                        <div id="mutantbuttonsNGL">
                                                        <div class="d-inline">
                                                        <button onclick="launchOnVMD(1)" id="mutant_1" class="btn  btn-outline-dark btn-icon"><i data-feather="download-cloud"></i></button>
                                                        <button onclick="toggleStruct(this, 1)" id="mutant_1_struc" class="btn  btn-green btn-icon">STR</button>
                                                        <button onclick="toggleWater(this, 1)" id="mutant_1_water" class="btn  btn-blue btn-icon">WAT</button>
                                                            <div class='minibox' style='background-color: #cccccc'></div>Wildtype
                                                        </div>
                                        </div>
                                    <br />

                                    <h6 class="card-title">Tools</h6>
                                    <!--<button type="button" class="btn btn btn-outline-primary w-100" onclick="exportPDB()">Export to PDB</button>-->
                                    <button type="button" class="btn btn btn-outline-primary w-100" onclick="exportPNG('3D')">Export PNG</button>
                                    <button type="button" class="btn btn btn-outline-primary w-100" onclick="open_directory()">Open Project Directory</button>
                                    <br />
                                    <br />
                                </div>
                            </div>

                            <div class="col-lg-10 card" id="explorerPNG">
                                <div class="card-body">
                                    <h5 class="card-title">3D Explorer</h5>
                                    <div id="mutantviewer" class="w-100" style="max-height: 500px !important; min-width: 100% !important;">
                                        <!-- PDB FILE IN HERE -->
                                        <div id="viewer4loading" class="align-top">
                                            <div class="d-flex justify-content-center align-middle">
                                                <div><br /> </div>
                                                <div><br /></div>
                                                <div class="spinner-border" role="status"> </div> 

                                                &nbsp;
                                                <br /><br />
                                            </div>
                                            <div class="d-flex justify-content-center align-middle"><h5>Loading WT Strcucture</h5></div>
                                        </div>
                                    </div>
                                    
                                </div>
                                <!--Anchorpoint Buttons-->
                                <div class="card">
                                    <div class="card-body">
                                        
                                        <div class="text-center" id="anchorpointlist"> 
                                            
                                        </div>
                                        
                                    </div>
                                </div>

                            </div>


                        </div>    
                        
                        

                        <div class="row">
                            <div class="col-lg-6 card" id="rmsdPNG">  
                                <div class="card-body">
                                    <h5 class="card-title">RMSD Explorer</h5>
                                    <div>
                                        <canvas id="RMSD_chart" class="w-100"></canvas>
                                        <button class="btn btn-sm btn-outline-dark" onclick="resetZoom('rmsd')">Reset Zoom</button>
                                        <button class="btn btn-sm btn-outline-dark" onclick="exportPNG('rmsd')">Export PNG</button>
                                        <button class="btn btn-sm btn-outline-dark" onclick="exportXLS('rmsd')">Export CSV</button>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-6 card" id="perresiduePNG">
                                <div class="card-body">
                                    <h5 class="card-title">Per-residue Energy at Anchor points</h5>
                                    <div>
                                        <canvas id="Energy_chart" class="w-100"></canvas>
                                        <button class="btn btn-sm btn-outline-dark" onclick="resetZoom('energy')">Reset Zoom</button>
                                        <button class="btn btn-sm btn-outline-dark" onclick="exportPNG('perresidue')">Export PNG</button>
                                        <button class="btn btn-sm btn-outline-dark" onclick="exportXLS('perresidue')">Export CSV</button>
                                        <button class="btn btn-sm btn-outline-dark" onclick="toggleNumbering()">Toggle Residue Numbering</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                           

                        <!--<div class="row">-->
                            
                        <!--</div>-->

                        <div class="row"  id="sequenceHolderAll">
                        <div class="col-lg-12 card">
                                <div class="card-body">
                                    <h5 class="card-title">Interactive Energy Explorer</h5>
                                    
                                    <div class="row">
                                        <div class="form-floating col-lg-3">
                                           
                                            <select class="form-select h5" id="seqCompareMethod" name="seqCompareMethod" onchange="changeSeqCompare(this)">
                                                <option value="selfMutant">ENERGY DISTRIBUTION (WITHIN EACH MUTANT)</option>
                                                <option value="gainLoss">ENERGY GAIN/LOSS (RESPECT TO WT)</option>
                                                <option value="stdDev">STD DEV OF ENERGY</option>
                                            </select>
                                            <label for="seqCompareMethod">Display Perspective</label>
                                       </div>
                                       <div class="form-floating col-lg-3">
                                            
                                            <select class="form-select h5" id="seqorder" name="seqorder" onchange="reOrderSeqs(this)">
                                                <option value="mutantID">MUTANT ID</option>
                                                <option value="energyASC">ENERGY ASCENDING</option>
                                                <option value="energyDESC">ENERGY DESCENDING</option>
                                            </select>     
                                            <label for="seqorder">Order</label>
                                        </div>
                                        <div class="form-floating col-lg-3">
                                            
                                            <select class="form-select h5" id="seqsegment" name="seqsegment" onchange="setSegment(this)">
                                                <option value="L">MUTABLE OBJECT</option>
                                                <option value="R">NON-MUTABLE OBJECT</option>
                                            </select>     
                                            <label for="seqsegment">Display Complex Component</label>
                                        </div>
                                    </div><br />
                                    
                                    <div class="col-lg-12" id="sequenceHolder" style="overflow-y: auto; overflow-x: scroll; padding-top: 12px">

                                    </div>
                                    <p>&nbsp;</p>
                                      <button class="btn btn-sm btn-outline-dark" onclick="exportPNG('energy')">Export PNG</button>
                                </div>
                            </div>

                        </div>
                        

                        <div class="row">
                            <div class="col-lg-12 card" id="pairwisePNG">
                                <div class="card-body">
                                    <h5 class="card-title">Pairwise Contact & Energy</h5>
                                    <div class="d-flex align-items-center flex-grow-1">
                                        <label for="thresholdSlider" class="form-label mb-0 me-2" style="white-space: nowrap;">ΔG threshold</label>
                                        <input type="range" class="form-range w-80" id="thresholdSlider" min="0.4" max="10" step="0.1" value="0.4"></input>
                                        <button id="thresholdValueLabel" class="btn btn-lg btn-outline-primary" type="button">-0.4 kcal/mol</button>
                                    </div>
                                    <canvas id="Pairwise_chart" class="w-100"></canvas>
                                    <button class="btn btn-sm btn-outline-dark" onclick="resetZoom('pairwise')">Reset Zoom</button>
                                    <button class="btn btn-sm btn-outline-dark" onclick="exportPNG('pairwise')">Export PNG</button>
                                    <button class="btn btn-sm btn-outline-dark" onclick="exportXLS('pairwise')">Export CSV</button>
                                    <button class="btn btn-sm btn-outline-dark" onclick="toggleNumbering()">Toggle Residue Numbering</button>
                                </div>
                            </div>
                        </div>


                    </div>
                    
                </div>
        <!--FINISH Right Half-->
        </div> 
    </div>
</div>





   

<!-- Modal -->
<div class="modal fade" id="staticBackdrop" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="staticBackdropLabel" aria-hidden="false">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title justify-content-center" id="staticBackdropLabel">Loading Data</h5>
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
                Please Wait. This can take up to 30 seconds
            </div>
      </div>
    </div>
  </div>
</div>


<!-- Modal Loading VMD-->
<div class="modal fade" id="modalVMD" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="modalVMDLabel" aria-hidden="false">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title justify-content-center" id="modalVMDLabel">Launching VMD</h5>
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
                Generating input files. Please Wait.
            </div>
      </div>
    </div>
  </div>
</div>



<!-- Modal Loading Replicas-->
<div class="modal fade" id="replicaBackdrop" data-bs-backdrop="static" data-bs-keyboard="true" tabindex="-1" aria-labelledby="replicaBackdropLabel" aria-hidden="false">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
        <div class="modal-header">
            <h5 class="modal-title justify-content-center" id="replicaBackdropLabel">Confirmation replicas mutant# </h5>
        </div>
        <div class="modal-body">    
            <div id="replica-tablediv">

            </div>
            <div class="justify-content-center d-flex">
                <button class="btn btn-info position-relative" type="button" onclick="closeReplica()">Close</button> 
            </div>
        </div>
    </div>
  </div>
</div>





<!--Modal Already-->
<div class="modal fade" id="modalVMD" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="modalVMDLabel" aria-hidden="false">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title justify-content-center" id="modalVMDLabel">Launching VMD</h5>
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
                Generating input files. Please Wait.
            </div>
      </div>
    </div>
  </div>
</div>


 <!-- FIlter Modal-->
<div class="modal fade" id="filterModal" data-bs-backdrop="static" data-bs-keyboard="true" tabindex="-1" aria-labelledby="modalFilterLabel" aria-hidden="false">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title justify-content-center" id="modalFilterLabel">Advanced Filter</h5>
      </div>
      <div class="modal-body">
            <div class="justify-content-center d-flex">
                Use the dropdowns to add mutations to the filter criteria:
            </div>
            <br>
            <div class="justify-content-center  d-flex align-top">
                <div class="card flex-start">
                    <div class="card-body">
                        <div class="text-center" id="anchorpointlist_filter"> 
                            
                        </div>
                    </div>
                </div>
                <div class="card flex-end">
                    <div class="card-body">    
                        Filter Criteria    
                        <div class="text-center" id="anchorpointlist_criterias"> 
                            
                        </div>
                    </div>
                </div>
                
            </div>

            <div class="justify-content-center d-flex">
                <button class="btn btn-success position-relative" type="button" onclick="filterTable()">Filter Table</button>  
                <button class="btn btn-secondary position-relative" type="button" onclick="clearCriteria()">Clear Criteria</button>  
                <button class="btn btn-info position-relative" type="button" onclick="closeCriteria()">Close</button> 
            </div>

      </div>
    </div>
  </div>
</div>



<!-- Display Watersites for a mutant-->
<div class="modal fade" id="waterBackdrop" data-bs-backdrop="static" data-bs-keyboard="true" tabindex="-1" aria-labelledby="waterBackdropLabel" aria-hidden="false">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
        <div class="modal-header">
            <h5 class="modal-title justify-content-center" id="waterBackdropLabel">Water-contacts Summary Panel </h5>
        </div>
        <div class="modal-body">    
            <div id="watersite-tablediv">
                                <table id="datatablesWaters" width="100%" class="text-center table display compact table-sm">
                                    <thead>
                                        <th>Heavy-Atom</th>
                                        <th>WaterID</th>
                                        <th>Residence</th>
                                    </thead>
                                    <tbody id="table-waters-body">
                                       <tr><td colspan="4">No water data</td></tr>
                                    </tbody>
                                </table>  

            </div>
            <div class="justify-content-center d-flex">
                <button class="btn btn-info position-relative" type="button" onclick="closeWatersites()">Close</button> 
            </div>
        </div>
    </div>
  </div>
</div>
