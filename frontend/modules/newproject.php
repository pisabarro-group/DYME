
<main>
                    <header class="page-header page-header-dark bg-gradient-primary-to-secondary pb-10">
                        <div class="container-fluid px-4">
                            <div class="page-header-content pt-4">
                                <div class="row align-items-center justify-content-between">
                                    <div class="col-auto mt-4">
                                        <h1 class="page-header-title">
                                            <div class="page-header-icon"><i data-feather="arrow-right-circle"></i></div>
                                            New Project Wizzard
                                        </h1>
                                        <div class="page-header-subtitle">
                                        Welcome to the project wizard of the DYME platform. <br />
                                        Please complete all steps to generate a new project
                                          
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </header>
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    <!-- Main page content-->
                    <div class="container-fluid px-4 mt-n10">
                        <!-- Wizard card example with navigation-->
                        <div class="card">
                            <div class="card-header border-bottom">
                                <!-- Wizard navigation-->
                                <div class="nav nav-pills nav-justified flex-column flex-xl-row nav-wizard" id="cardTab" role="tablist">
                                    <!-- Wizard navigation item 1-->
                                    <a class="nav-item nav-link active" id="wizard1-tab" href="#wizard1" data-bs-toggle="tab" role="tab" aria-controls="wizard1" aria-selected="true">
                                        <div class="wizard-step-icon">1</div>
                                        <div class="wizard-step-text">
                                            <div class="wizard-step-text-name">Initial Preparation</div>
                                            <div class="wizard-step-text-details">System setup & PDB definition</div>
                                        </div>
                                    </a>
                                    <!-- Wizard navigation item 2-->
                                    <!--<a class="nav-item nav-link disabled" id="wizard2-tab" href="#wizard2" data-bs-toggle="tab" role="tab" aria-controls="wizard2" aria-selected="true">
                                        <div class="wizard-step-icon">2</div>
                                        <div class="wizard-step-text">
                                            <div class="wizard-step-text-name">Prepare/Sanitize Inputs</div>
                                            <div class="wizard-step-text-details">Verify System Integrity</div>
                                        </div>
                                    </a>-->
                                    <!-- Wizard navigation item 3-->
                                    <a class="nav-item nav-link" id="wizard3-tab" href="#wizard3" data-bs-toggle="tab" role="tab" aria-controls="wizard3" aria-selected="true">
                                        <div class="wizard-step-icon">2</div>
                                        <div class="wizard-step-text">
                                            <div class="wizard-step-text-name">Setup MD Simulation Parameters</div>
                                            <div class="wizard-step-text-details">MD-specific parameters</div>
                                        </div>
                                    </a>
                                    <!-- Wizard navigation item 4-->
                                    <a class="nav-item nav-link" id="wizard4-tab" href="#wizard4" data-bs-toggle="tab" role="tab" aria-controls="wizard4" aria-selected="true">
                                        <div class="wizard-step-icon">3</div>
                                        <div class="wizard-step-text">
                                            <div class="wizard-step-text-name">Setup Mutagenesis Pipeline</div>
                                            <div class="wizard-step-text-details">Adjust DYME specific settings</div>
                                        </div>
                                    </a>
                                </div>
                            </div>
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            

                            <!-- STEP 1-->
                            <div class="card-body">
                                <div class="tab-content" id="cardTabContent">
                                    <!-- Wizard tab pane item 1-->
                                    <div class="tab-pane py-7 py-xl-12 fade show active" id="wizard1" role="tabpanel" aria-labelledby="wizard1-tab">
                                        <div class="row justify-content-center">
                                            <div class="col-xxl-8 col-xl-8">
                                                <h3 class="text-primary">Step 1</h3>
                                                <h5 class="card-title mb-4">Setup project name and initial system</h5>
                                                <form  name="formStep1" id='formStep1' enctype="multipart/form-data">
                                                    <div class="mb-3">
                                                        <label class="small mb-1" for="projectName">Project name</label>
                                                        <input class="form-control" id="projectName" name="projectName" type="text" placeholder="Enter a name for your project" value="" />
                                                    </div>


                                                    <div class="row">
                                                        &nbsp;
                                                    </div>

                                                    <label class="small mb-1" for="projectName">Define how DYME will build your initial system</label>
                                                    <div class="card">
                                                        <div class="card-header">
                                                            <ul class="nav nav-pills card-header-pills" id="cardPill" role="tablist">
                                                               <!-- <li class="nav-item"><a class="nav-link disabled" id="fromPDB-pill" href="#fromPDB" data-bs-toggle="tab" role="tab" aria-controls="frompdb" aria-selected="false">Use OpenMM</a></li> -->
                                                                <li class="nav-item"><a class="nav-link active" id="fromAmber-pill" href="#fromAmber" data-bs-toggle="tab" role="tab" aria-controls="fromamber" aria-selected="false" onclick="fillLeapOptions()">Use Amber (TLeap)</a></li>
                                                            </ul>
                                                        </div>
                                                        
                                                        <div class="card-body">
                                                            <div class="tab-content" id="cardPillContent">

                                                                <!--PDB LOADER OPTIONS PILL-->
                                                                <div class="tab-pane fade" id="fromPDB" role="tabpanel" aria-labelledby="fromPDB-pill">
                                                                    <div class="row gx-3">
                                                                        <div class="mb-3 col-md-6">                                                            
                                                                            <!-- FORCEFIELD SELECTOR -->
                                                                                <label class="small mb-1" for="inputForcefield">Forcefield</label>
                                                                                    <select class="form-control" name="inputForcefield" id="inputForcefield" onchange="handleWater(this)">
                                                                                        <option value="0">Select a Forcefield...</option>
                                                                                        
                                                                                        <option value="absinth.xml">ABSINTH</option>
                                                                                        <option value="0"></option>
                                                                                        <option value="amoeba2009.xml">AMOEBA 2009</option>
                                                                                        <option value="amoeba2013.xml">AMOEBA 2013</option>
                                                                                        <option value="amoeba2018.xml">AMOEBA 2018</option>
                                                                                        <option value="0"></option>
                                                                                        <option value="amber03.xml">AMBER03</option>
                                                                                        <option value="amber10.xml">AMBER10</option>
                                                                                        <option value="amber96.xml">AMBER96</option>
                                                                                        <option value="amber99sb.xml">AMBER99SB</option>
                                                                                        <option value="amber14-all.xml">AMBER14</option>
                                                                                        <option value="amber14/DNA.bsc1.xml">AMBER14_DNA_BSC1</option>
                                                                                        <option value="amber14/DNA.OL15.xml">AMBER14_DNA_OL15</option>                                                                    
                                                                                        <option value="amber14/GLYCAM.xml">AMBER14_GLYCAM</option>                                                                    
                                                                                        <option value="amber14/lipid17.xml">AMBER14_LIPID17</option>
                                                                                        <option value="amber14/protein.ff14SB.xml">AMBER14_FF_PROTEIN_SB</option>
                                                                                        <option value="amber14/protein.ff15ipq.xml">AMBER14_FF_PROTEIN_15ipq</option>
                                                                                        <option value="amber14/RNA.OL3.xml">AMBER14_RNA_OL3</option>
                                                                                        <option value="amber14/spce.xml">AMBER14_SPCE</option>
                                                                                        <option value="0"></option>
                                                                                        <option value="charmm36.xml">CHARMM36</option>
                                                                                        <option value="charmm_polar_2013.xml">CHARMM_POLAR_2013</option>
                                                                                        <option value="charmm_polar_2019.xml">CHARMM_POLAR_2019</option>
                                                                                        <option value="0"></option>
                                                                                        <option value="opls-aam.xml">OPLS-AAM</option>
                                                                                    
                                                                                    </select>
                                                                        </div>
                                                                        <div class="mb-3 col-md-6" id="waterModelRow">
                                                                            <!-- WATER SELECTOR -->
                                                                                <label class="small mb-1" for="inputFWater">Solvation Model</label><i class="icon-users" data-feather="help-circle" data-bs-toggle="tooltip" data-bs-placement="top" title="Leave blank to run in-vacuo"></i>
                                                                                <select class="form-control" name="inputFWater" id="inputFWater" onchange="activateContinue(this)" disabled> 
                                                                                    <option value="0">Select a Water Model...</option>
                                                                                    
                                                                                    
                                                                                </select>
                                                                        </div>
                                                                    </div>
                                                                
                                                                                                                    
                                                                    <div class="mb-3">
                                                                            <!-- PDB Uploader-->
                                                                            <div class="card mb-4 mb-xl-0">
                                                                                <div class="card-header">Starting Topology/Structure</div>
                                                                                <div class="card-body text-center">
                                                                                    <div class="font-italic text-muted mb-4" id="pdbAlert">Accepted formats: PDB / PDBx / mmCIF
                                                                                        <br /> (All molecules in one file)
                                                                                    </div>
                                                                                    <div class="alert alert-primary" role="alert" id="pdbFileName" hidden></div>
                                                                                    <!-- Profile picture upload button-->
                                                                                    
                                                                                    <button class="btn btn-primary" type="button" onclick="$('#pdbFile').click()">Select File</button>
                                                                                    <input id="pdbFile" name="pdbFile" type="file" style="display: block;  height: 1px; width: 1px;" accept=".pdb, .pdbx, .mmcif"><br />
                                                                                    
                                                                                    
                                                                                </div>
                                                                            </div>
                                                                    </div>
                                                                </div>
                                                                



                                                                 <!--AMBERFILE LOADER OPTIONS PILL-->
                                                                <div class="tab-pane fade show active" id="fromAmber" role="tabpanel" aria-labelledby="fromAmber-pill">
                                                                
                                                                    <div class="container">
                                                                        <div class="row gx-6">

                                                                            <!--PRMTOP FILE-->
                                                                             <div class="mb-3 col-md-6"> 
                                                                                <div class="card mb-4 mb-xl-0">
                                                                                    <div class="card-header">TLeap sources</div>
                                                                                    <div class="card-body text-left">
                                                                                        <div class="font-italic text-left mb-4" id="leapLabel"><strong>Add TLeap libraries and forcefields:</strong> <br>- You must select at least 1 forcefield (i.e. protein.FF19SB). <br>- Make sure to add libraries (or atom definitions) contained in yout PDB. <br>- Remember to add libraries for your desired solvation method (i.e. water.tip3p)</div>
                                                                                        <select class="form-control" name="leapSources" id="leapSources" onchange="handleAddleapSource(this)">
                                                                                            <option value="0">Select to add...</option>
                                                                                            
                                                                                        </select>
                                                                                        <br />
                                                                                        <ul class="list-group" id="leapSourcesList">
                                                                                            
                                                                                        </ul>
                                                                                        <select name="leapSourcesContent" id="leapSourcesContent" multiple hidden>
                                                                                        </select>

                                                                                        <br />

                                                                                        <!-- Profile picture upload button-->
                                                                                        <div class="font-italic text-left mb-4" id="prmtopAlert"><strong>Upload custom parameters or force modifications (optional):</strong></div>
                                                                                        <ul class="list-group" id="leapSourcesListUploaded">
                                                                                            
                                                                                        </ul>
                                                                                        <br />
                                                                                        <button class="btn btn-primary" type="button" onclick="$('#leapFiles').click()" title="Accepts frcmod/off, and other Amber compliant formats">Select File(s)</button>
                                                                                        <input id="leapFiles" name="leapFiles" type="file" style="display: block; height: 1px; width: 1px;" accept=".off, .frcmod, .prep" multiple>

                                                                                        <br />
                                                                                        <div class="font-italic text-left mb-4" id="leapAtomTypesd" title="TLeap string to define special atom types (like Zinc). Leave blank otherwise"><strong>Define custom Amber AtomTypes (optional):</strong></div>
                                                                                        <input class="form-control" id="leapAtomTypes" name="leapAtomTypes" type="text" placeholder="Enter AtomType string { {} {} ... }" value='' />



                                                                                        <br />
                                                                                        <div class="font-italic text-left mb-4" id="leapBondingd"><strong>Define custom Bond Info (optional):</strong></div>
                                                                                        <textarea class="form-control" id="leapBonds" name="leapBonds" rows="8" placeholder="Enter Bond Info: (i.e: bond a.74.ZN a.11.SG) ..." ></textarea>
                                                                                        <br />

                                                                                    </div>
                                                                                </div>
                                                                             </div>        

                                                                             <!--Combined PDB file (no water)-->
                                                                             <div class="mb-3 col-md-6"> 
                                                                                <div class="card mb-4 mb-xl-0">
                                                                                    <div class="card-header">Starting Topology (receptor+ligand complex)</div>
                                                                                    <div class="card-body text-center">
                                                                                        <div class="font-italic text-muted mb-4" id="leadPdbFilenameAlert">Accepted formats: .pdb<br>(prepare with pdb4amber first!)</div>
                                                                                        <div class="alert alert-primary" role="alert" id="leadPdbFilename" hidden></div>
                                                                                        <!-- Profile picture upload button-->
                                                                                        
                                                                                        <button class="btn btn-primary" type="button" onclick="$('#leadPdbFile').click()" title="File must be prepared with pdb4amber before this step!!">Select File</button>
                                                                                        <input id="leadPdbFile" name="leadPdbFile" type="file" style="display: block;  height: 1px; width: 1px;" accept=".pdb"><br />
                                                                                    </div>
                                                                                </div>

                                                                                <br />

                                                                                <!--Hydrate-->
                                                                             
                                                                                <div class="card mb-4 mb-xl-0">
                                                                                    <div class="card-header">Solvation, Box Size and Neutralization</div>
                                                                                    <div class="card-body text-left">

                                                                                        <div class="mb-4 col-12">
                                                                                          <div class="row">
                                                                                            <div class="col">
                                                                                                <label for="shapeLeapWaterbox">Box Shape</label> 
                                                                                                <select name='shapeLeapWaterbox' id='shapeLeapWaterbox' class="form-control" title="Select box geometry">
                                                                                                    <option value="solvateoct" selected>T. Octahedron</option>
                                                                                                    <option value="solvatebox">Cubic</option>
                                                                                                    
                                                                                                </select>
                                                                                            </div>
                                                                                            <div class="col">
                                                                                                <label for="leapWaterbox">Solvation Method</label> 
                                                                                                <select class="form-control col-md-4" name="leapWaterbox" id="leapWaterbox" title="Select solvation model (as available in Amber24)">
                                                                                                    <option value="0">Select Model..</option>                                                                                            
                                                                                                    <option value="CHCL3BOX">CHCL3BOX</option>
                                                                                                    <option value="FB3BOX">FB3BOX</option>
                                                                                                    <option value="FB4BOX">FB4BOX</option>
                                                                                                    <option value="MEOHBOX">MEOHBOX</option>
                                                                                                    <option value="NMABOX">NMABOX</option>
                                                                                                    <option value="TIP3PBOX">TIP3PBOX</option>
                                                                                                    <option value="TIP3PFBOX">TIP3PFBOX</option>
                                                                                                    <option value="TIP4PBOX">TIP4PBOX</option>
                                                                                                    <option value="TIP4PEWBOX">TIP4PEWBOX</option>
                                                                                                    <option value="TIP5PBOX">TIP5PBOX</option>
                                                                                                    <option value="OPCBOX">OPCBOX</option>
                                                                                                    <option value="OPC3BOX">OPC3BOX</option>
                                                                                                    <option value="POL3BOX">POL3BOX</option>
                                                                                                    <option value="QSPCFWBOX">QSPCFWBOX</option>
                                                                                                    <option value="SPCBOX">SPCBOX</option>
                                                                                                    <option value="SPCFWBOX">SPCFWBOX</option>
                                                                                                </select> 
                                                                                            </div>
                                                                                            <div class="col">
                                                                                                <label for="leapWaterboxSize">Box Size or Buffer (Å)</label>
                                                                                                <input type="text" name="leapWaterboxSize" id="leapWaterboxSize" value="10" class="form-control"  title="Distance to edge of the box. Tipically 8 to 15 angstroms, depends on the size of your system. Note this setting will also adjust the cuttoff distance in the next step">
                                                                                            </div>    
                                                                                          </div>
                                                                                          <br />
                                                                                          
                                                                                          <div class="row">
                                                                                             <div class="col-4">
                                                                                                <label for="leapPositiveIon">Positive Ion</label> 
                                                                                                <select name='leapPositiveIon' id='leapPositiveIon' class="form-control w-75" >
                                                                                                    <option value="Na+" selected>Na+</option>
                                                                                                    <option value="K+">K+</option>
                                                                                                </select>

                                                                                                <label for="LeapNegativeIon">Negative Ion</label> 
                                                                                                <select name='LeapNegativeIon' id='LeapNegativeIon' class="form-control w-75" >
                                                                                                    <option value="Cl-" selected>Cl-</option>
                                                                                                </select>
                                                                                             </div>
                                                                                             <div class="col-8">
                                                                                               <label for="leapmolarStrength">Target Ionic Strength (mmol)</label>
                                                                                               <input type="text" name="leapmolarStrength" id="leapmolarStrength" value="0" class="form-control w-25" title="Target neutralization value">
                                                                                             </div>
                                                                                          </div>
                                                                                          
                                                                                        </div>
                                                                                        
                                                                                    </div>

                                                                                </div>

                                                                             </div> 

                                                                             
                                                                             

                                                                        </div>
                                                                    </div>
                                                                

                                                                <!--END AMBERPILL CONTENT-->
                                                                </div>
                                                             <!--END PILL CONTENT-->
                                                            </div>
                                                        <!--END CARD BODY-->
                                                        </div>
                                                    <!--END CARD CONTENT-->
                                                    </div>



                                                                                                        
                                                    <!-- PORSIACA
                                                    <div class="row gx-3">
                                                        <div class="mb-3 col-md-6">
                                                            <label class="small mb-1" for="inputOrgName">Mutagenesis</label>
                                                            <input class="form-control" id="inputOrgName" type="text" placeholder="Enter your organization name" value="Start Bootstrap" />
                                                        </div>
                                                        <div class="mb-3 col-md-6">
                                                            <label class="small mb-1" for="inputLocation">Location</label>
                                                            <input class="form-control" id="inputLocation" type="text" placeholder="Enter your location" value="San Francisco, CA" />
                                                        </div>
                                                    </div>
                                                    <div class="mb-3">
                                                        <label class="small mb-1" for="inputEmailAddress">Email address</label>
                                                        <input class="form-control" id="inputEmailAddress" type="email" placeholder="Enter your email address" value="name@example.com" />
                                                    </div>
                                                    <div class="row gx-3">
                                                        <div class="col-md-6 mb-md-0">
                                                            <label class="small mb-1" for="inputPhone">Phone number</label>
                                                            <input class="form-control" id="inputPhone" type="tel" placeholder="Enter your phone number" value="555-123-4567" />
                                                        </div>
                                                        <div class="col-md-6 mb-0">
                                                            <label class="small mb-1" for="inputBirthday">Birthday</label>
                                                            <input class="form-control" id="inputBirthday" type="text" name="birthday" placeholder="Enter your birthday" value="06/10/1988" />
                                                        </div>
                                                    </div>
                                                    -->
                                                    
                                                    <hr class="my-4" />
                                                    <div class="d-flex justify-content-right">
                                                        <!--
                                                        <button class="btn btn-light disabled" type="button" disabled>Previous</button>
                                                        -->
                                                        <button class="btn btn-primary" type="button" id="btnNextStep1" onClick="validateStep1()" disabled>Next Step</button>
                                                    </div>

                                                    <input type="hidden" name="sourcetype" id="sourcetype" value="amber">
                                                </form>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    
                                  
                                  
                                    
                    
                    




















                           
                            <!-- STEP 2-->                
                                            
                            <!-- Wizard tab pane item 2-->
                            <div class="tab-pane py-5 py-xl-12 fade" id="wizard2" role="tabpanel" aria-labelledby="wizard2-tab">
                                <div class="row justify-content-center">
                                    <div class="col-xxl-12 col-xl-12">
                                        <h3 class="text-primary">Step 2</h3>
                                        <h5 class="card-title mb-4">Prepare PDB Input for MD operations</h5>
                                                        
                                                        
                                                        
                                                        
                                                        
                                    <!--Leftmost Pane -->                    
                                    <div class="row">
                                        <div class="col-xl-4">
                                            <!-- Profile picture card-->
                                            <div class="card mb-4 mb-xl-0">
                                                <div class="card-header">System Viewer</div>
                                                <div id="viewport" style="width:100%; height:500px; z-index: 100">
                                                    <!-- PDB FILE IN HERE -->
            
                                                </div>
                                            </div>
                                        </div>
                                    


                                    <!--Rightmost pane-->
                                    <div class="col-xl-8">
                                    <div class="accordion" id="accordionExample">

                                        
                                        <!-- CHAIN SELECTOR -->
                                        <div class="card card-collapsable mb-4">
                                            <a class="card-header" href="#collapseTwo" data-bs-toggle="collapse" role="button" aria-expanded="true" aria-controls="collapseTwo">Filter Chains & Manage Heteroatoms
                                                <div class="card-collapsable-arrow">
                                                    <i class="fas fa-chevron-down"></i>
                                                </div>
                                            </a>
                                            <div id="collapseTwo" class="collapse show" aria-labelledby="headingOne" data-parent="#accordionExample">
                                              <div class="card-body">
                                                <form name="chainSelect" id="chainSelect">
                                                    <h5>The system contains X chains, select the ones you'd like to keep</h5>
                                                    <div class="row">
                                                    <div class="col-md-6">
                                                        <table id="chainSelectorTable" class="dataTable-table">
                                                            <thead>
                                                                <tr>
                                                                    <th data-sortable="" style="width: 33%;">Chain</th>
                                                                    <th data-sortable="" style="width: 33%;"># Residues</th>
                                                                    <th data-sortable="" style="width: 33%;">Content</th>
                                                                    <th data-sortable="" style="width: 33%;">Include?</th>
                                                            </thead>
                                                            
                                                            <tbody id="selectedChains">
                                                                <tr>
                                                                    <td>A</td>
                                                                    <td>244</td>
                                                                    <td>Protein</td>
                                                                    <td>
                                                                        <div class="form-check">
                                                                            <input class="form-check-input" id="chain[A]" type="checkbox" value="checked" checked>
                                                                        </div>
                                                                    </td>
                                                                </tr>
                                                         </table>
                                                    </div>
                                                    
                                                    <div class="col-md-6">
                                                      <div class="mb-3 col-md-6">
                                                        <label for="heteroatoms"><strong>Heteroatom Management</strong></label>
                                                        <select class="form-control form-control-solid" id="heteroatoms" onchange="">
                                                            
                                                            <option value="all">Keep all Heteroatoms</option>    
                                                            <option value="water">Remove all Heteroatoms, including water</option>
                                                            <option value="none">Remove all Heteroatoms, except water</option>
                                                            
                                                            
                                                        </select>
                                                    </div>  
                                                    </div>
                                                    </div>
                                                    <!-- Save changes button-->
                                                    <div class="row"><div class="col-md-12">
                                                        <button id="continueChainsBtn" class="btn btn-secondary float-end" type="button">Include Selected & Continue</button>
                                                    </div></div>
                                                </form>
                                              </div>
                                            </div>
                                        </div>






                                        <!-- ADD RESIDUES -->
                                        <div class="card card-collapsable mb-4">
                                            <a class="card-header" href="#collapseThree" data-bs-toggle="collapse" role="button" aria-expanded="true" aria-controls="collapseThree">Check for Missing Residues
                                                <div class="card-collapsable-arrow">
                                                    <i class="fas fa-chevron-down"></i>
                                                </div>
                                            </a>
                                            <div id="collapseThree" class="collapse " aria-labelledby="headingThree" data-parent="#accordionExample">
                                              <div class="card-body">
                                                 <form name="addResidues" id="addResidues">
                                                    <h5>The system sequence contains missing residues. Would you like to add them?</h5>
                                                    
                                                    <div>
                                                        <table id="datatablesSimple" class="dataTable-table">
                                                            <thead>
                                                                <tr>
                                                                    <th data-sortable="" style="width: 33%;">Chain</th>
                                                                    <th data-sortable="" style="width: 33%;">Residue Positions</th>
                                                                    <th data-sortable="" style="width: 33%;">Sequence</th>
                                                                    <th data-sortable="" style="width: 33%;">Add?</th>
                                                                </tr>
                                                            </thead>
                                                            
                                                            <tbody>
                                                              <tr>
                                                                <td>A</td>
                                                                <td>4 to 17</td>
                                                                <td>KLADGDLYAAYTI</td>
                                                                <td><input type="checkbox" name="add" value="chunk1[]"></td>
                                                              </tr>
                                                         </table>
                                                         <div class="form-group">
                                                            <button type="button" id="selectAllMissing" class="btn btn-primary">Select All</button>
                                                            <button type="button" id="deselectAllMissing" class="btn btn-primary" >Select None</button>
                                                            <button id="btnCheckMissingResidues" class="btn btn-secondary float-end" type="button">Continue & Fix Selected</button>
                                                        </div>
                                                    </div>
                                                    
                                                    
                                                 </form>
                                              </div>
                                            </div>
                                        </div>







                                        <!-- CONVERT NON STANDARD -->
                                        <div class="card card-collapsable mb-4">
                                            <a class="card-header" href="#collapseFour" data-bs-toggle="collapse" role="button" aria-expanded="true" aria-controls="collapseFour">Check for Non-standard Residues
                                                <div class="card-collapsable-arrow">
                                                    <i class="fas fa-chevron-down"></i>
                                                </div>
                                            </a>
                                            <div id="collapseFour" class="collapse " aria-labelledby="headingFour" data-parent="#accordionExample">
                                              <div class="card-body">

                                                <div class="container">
                                                     <div class="row">
                                                        <h4 class="text-center">Your system contains Non-Standard residues!!</h4>
                                                        <p>&nbsp;</p>
                                                     </div>
                                                     <div class="row">
                                                        <div class="col col-md-6">

                                                            <form name="addNonStandard" id="addNonStandard">
                                                                <h5>The following non-standard residues can be converted</h5>
                                                                
                                                                <div>
                                                                    <table id="datatablesSimple" class="dataTable-table">
                                                                        <thead>
                                                                            <tr>
                                                                                <th>Chain</th>
                                                                                <th>Residue</th>
                                                                                <th>Convert To</th>
                                                                                <th>Convert?</th>
                                                                            </tr>
                                                                        </thead>
                                                                        <tbody>
                                                                        <tr>
                                                                            <td>A</td>
                                                                            <td>SEC</td>
                                                                            <td><select name="res1">
                                                                                    <option value="CYS" {{ 'selected' if option == residue[4] else '' }}>CYS</option>
                                                                                </select>
                                                                            </td>
                                                                            <td><input type="checkbox" name="convert" value="res1" checked></td>
                                                                        </tr>
                                                                    </table>
                                                                    <div class="form-group">
                                                                        <button type="button" id="nstSelectAll" class="btn btn-primary">Select All</button>
                                                                        <button type="button" id="nstDeselectAll" class="btn btn-primary">Select None</button>
                                                                        <button id="btnFixSelectedNonstandard" class="btn btn-secondary float-end" type="button">Continue & Fix Selected</button>
                                                                    </div>
                                                                </div>
                                                                
                                                                
                                                            </form>
                                                        </div>
                                                        <div class="col col-md-1">
                                                            <div class="d-flex text-center" style="height: 100%;">
                                                                <div class="vr text-center"></div>
                                                            </div>
                                                        </div>
                                                        <div class="col col-md-5">
                                                              <h5>Load custom parameter definitions into the Forcefield</h5>
                                                              <form name="addDefinitions" id="addDefinitions" enctype="multipart/form-data"> 
                                                                <div class="card mb-4 mb-xl-0">
                                                                    <div class="card-header text-center">Upload your Definitions</div>
                                                                    <div class="card-body text-center">
                                                                        <div class="font-italic text-muted mb-4">Accepted formats: AMBER .off / .frcmod
                                                                            
                                                                        </div>
                                                                        <div class="alert alert-primary" role="alert" id="definitionFileName" hidden></div>
                                                                        <!-- Profile picture upload button-->
                                                                        
                                                                        <button class="btn btn-primary" type="button" onclick="$('#definitionFile').click()">Select Files</button>
                                                                        <input id="definitionFile" name="definitionFile" type="file" style="display: block;  height: 1px; width: 1px;" accept=".off, .frcmod"><br />
                                                                    </div>
                                                                </div>
                                                                <div class="form-group">
                                                                    <button id="btnApplyCustomDefinitions" class="btn btn-secondary float-end" type="button">Upload and Apply</button>
                                                                </div>
                                                              </form> 
                                                        </div>
                                                      </div>
                                                    </div>

                                              </div>
                                            </div>
                                        </div>



                                         <!-- ATOM FIXER-->
                                         <div class="card card-collapsable mb-4">
                                           
                                           <a class="card-header" href="#collapseOne" data-bs-toggle="collapse" role="button" aria-expanded="true" aria-controls="collapseOne">Atom Fixer 
                                               <div class="card-collapsable-arrow">
                                                   <i class="fas fa-chevron-down"></i>
                                               </div>
                                           </a>

                                           <div id="collapseOne" class="collapse " aria-labelledby="headingOne" data-parent="#accordionExample">
                                             <div class="card-body">
                                               <form name="atomFixer" id="atomFixer">
                                                       <h5>The following elements are missing heavy atoms. They will be added</h5>
                                                       <table id="datatablesSimple" class="dataTable-table">
                                                           <thead>
                                                               <tr>
                                                                   <th data-sortable="" style="width: 33%;">Chain</th>
                                                                   <th data-sortable="" style="width: 33%;">Residue</th>
                                                                   <th data-sortable="" style="width: 33%;">Missing Atoms</th>
                                                           </thead>
                                                           
                                                           <tbody>
                                                               <tr>
                                                                   <td>A</td>
                                                                   <td>ARG 4</td>
                                                                   <td>CG, CD, NE, CZ, NH1, NH2</td>
                                                               </tr>
                                                           </tbody>       
                                                        </table>
                                                   
                                                   <!-- Save changes button-->
                                                   <div class="row"><div class="col-md-12">
                                                      <button class="btn btn-secondary float-end" type="button" id="btnFixAtoms">Click to Fix</button>
                                                   </div></div>
                                               </form>
                                             </div>
                                           </div>
                                       </div>





                                         <!-- SOLVENT & NEUTRALIZATION-->
                                         <div class="card card-collapsable mb-4">
                                           
                                           <a class="card-header" href="#collapseFive" data-bs-toggle="collapse" role="button" aria-expanded="true" aria-controls="collapseFive">Solvent, Charge & Hydrogen Management
                                               <div class="card-collapsable-arrow">
                                                   <i class="fas fa-chevron-down"></i>
                                               </div>
                                           </a>

                                           <div id="collapseFive" class="collapse " aria-labelledby="headingFive" data-parent="#accordionExample">
                                             <div class="card-body">
                                               <form name="atomFixer" id="atomFixer">
                                                      

                                                       <div class="row">
                                                            <div class="col-md-3">
                                                                <ul class="nav nav-pills flex-column" id="cardPillVertical" role="tablist">
                                                                    <li class="nav-item"><a class="nav-link active" id="overview-pill-vertical" href="#setPh" data-bs-toggle="tab" role="tab" aria-controls="overview" aria-selected="true">Set System pH</a></li>
                                                                    <li class="nav-item"><a class="nav-link" id="example-pill-vertical" href="#setWaterBox" data-bs-toggle="tab" role="tab" aria-controls="example" aria-selected="false">Build Solvent Box</a></li>
                                                                    <li class="nav-item"><a class="nav-link" id="example-pill-vertical" href="#setNeutral" data-bs-toggle="tab" role="tab" aria-controls="example" aria-selected="false">Neutralization</a></li>
                                                                </ul>
                                                            </div>
                                                            <div class="col-md-9">
                                                                <div class="tab-content" id="optionCardsSolventHydroNeutra">
                                                                    <div class="tab-pane fade show active" id="setPh" role="tabpanel" aria-labelledby="overview-pill-vertical">
                                                                        <h5 class="card-title">Define pH of the system (This will add hydrogens accordingly)</h5>
                                                                        <p class="card-text"></p>
                                                                        <input name='ph' id='ph' class="form-control w-25" type="text" placeholder="Enter the pH of your system" value="7.0" />
                                                                    </div>

                                                                    <div class="tab-pane fade" id="setWaterBox" role="tabpanel" aria-labelledby="example-pill-vertical">
                                                                        <h5 class="card-title">Set dimentions of the WaterBox</h5>
                                                                        <div class=" mb-6 col-md-6">
                                                                        
                                                                            <label for="paddingWaterbox">Padding Distance (nm)</label>
                                                                            <input name='paddingWaterbox' id='paddingWaterbox' class="form-control w-25" type="text" placeholder="Enter the pH of your system" value="1.0" />
                                                                        
                                                                        </div>
                                                                        <div class=" mb-6 col-md-6">
                                                                        
                                                                            <label for="shapeWaterbox">Box Shape</label> 
                                                                            <select name='shapeWaterbox' id='shapeWaterbox' class="form-control w-50" >
                                                                                <option value="cube" selected>Cube</option>
                                                                                <option value="truncatedOctahedron">Truncated octahedron</option>
                                                                                <option value="rhombicDodecahedron">Rhombic dodecahedron</option>
                                                                            </select>
                                                                        
                                                                        </div>

                                                                    </div>

                                                                    <div class="tab-pane fade" id="setNeutral" role="tabpanel" aria-labelledby="example-pill-vertical">
                                                                        <h5 class="card-title">Ions will be added to neutralize the model.</h5>
                                                                        
                                                                        <div class="container">
                                                                         <div class="row">
                                                                            <div class="col">
                                                                                <label for="ionicS">Ionic Strength (molar)</label>
                                                                                <input name='ionicstrength' id='ionicstrength' class="form-control w-25" type="text" placeholder="Enter the pH of your system" value="0.0" />
                                                                            </div>
                                                                            <div class="col">
                                                                                <label for="positiveIon">Positive Ion</label> 
                                                                                <select name='positiveIon' id='positiveIon' class="form-control w-50" >
                                                                                    <option value="Cs">Cs+</option>
                                                                                    <option value="K">K+</option>
                                                                                    <option value="Li">Li+</option>
                                                                                    <option value="Na" selected="">Na+</option>
                                                                                    <option value="Rb">Rb+</option>
                                                                                </select>
                                                                            
                                                                                <label for="negativeIon">Negative Ion</label> 
                                                                                <select name='negativeIon' id='negativeIon' class="form-control w-50" >
                                                                                    <option value="Cl" selected="">Cl-</option>
                                                                                    <option value="Br">Br-</option>
                                                                                    <option value="F">F-</option>
                                                                                    <option value="I">I-</option>
                                                                                </select>
                                                                            </div>
                                                                         </div>
                                                                        </div>



                                                                    </div>

                                                                </div>
                                                            </div>
                                                        </div>
                                                   <!-- Save changes button-->
                                                   <div class="row"><div class="col-md-12">
                                                    <button class="btn btn-secondary float-end" type="button" id="btnSetWaterBox" >Click to Apply</button>
                                                   </div></div>

                                               </form>
                                             </div>
                                           </div>
                                       </div>


                                    </div>
                                    </div>
                                </div>
                                </div>
                                </div>
                                </div>
                                    
                                    
                                    




















                                
                            <!-- Wizard tab pane item 3-->
                            <div class="tab-pane py-5 py-xl-12 fade" id="wizard3" role="tabpanel" aria-labelledby="wizard3-tab">
                                <div class="row justify-content-center">
                                    <div class="col-xxl-12 col-xl-12">
                                        <h3 class="text-primary">Step 2</h3>
                                        <h5 class="card-title mb-4">Configure the MD simulation parameters. These will be the same for every mutant decoy.</h5>
                                        <form name="simulationOptions" id="simulationOptions" enctype="multipart/form-data">
                                            <div class="row">
                                                    <!--Leftmost Card-->
                                                    <div class="col-xl-4 mb-4">
                                                        <div class="card mb-4 mb-xl-0">
                                                            <div class="card-header">MD Parameters</div>
                                                            <div class="card-body">
                                                                
                                                                <!--Row splitter for System Parameters-->
                                                                <div class="row">
                                                                    <!--Col1-->
                                                                    <div class="col-xl-6 mb-6">
                                                                        <div class="mb-3">
                                                                            <label for="nonbondedmethod">Nonbonded Method</label>
                                                                            <select class="form-control" id="nonbondedmethod" title="Select how to compute long range nonbonded interactions">
                                                                                <option value="NoCutoff" title="The system is not periodic, and no cutoff is applied to nonbonded interactions.">No cutoff</option>
                                                                                <option value="CutoffNonPeriodic" title="The system is not periodic.  Long range interactions are cut off with the reaction field method.">Cutoff, non-periodic</option>
                                                                                <option value="CutoffPeriodic" title="Periodic boundary conditions are used.  Long range interactions are cut off with the reaction field method.">Cutoff, periodic</option>
                                                                                <option value="PME" title="Periodic boundary conditions are used.  Long range interactions are computed with Particle Mesh Ewald." selected>PME</option>
                                                                            </select>
                                                                        </div>

                                                                        <div id="cutoffRow" class="mb-3">
                                                                            <label for="cutoff">Cutoff Distance (nm)</label>
                                                                            <input type="text" name="cutoff" id="cutoff" value="1.0" class="form-control" title="Nonbonded interactions beyond this distance will be ignored.">
                                                                        </div>

                                                                        <div id="constraintsRow" class="mb-3">
                                                                            <label for="constraints">Bond Flexibility Constraints</label>
                                                                            
                                                                            <select name="constraints" id="constraints" title="Select which bonds to replace with rigid constraints." class="form-control">
                                                                                <option value="none" title="No degrees of freedom are constrained.">None</option>
                                                                                <option value="water" title="Water molecules are kept rigid, but no other degrees of freedom are constrained.">Water only</option>
                                                                                <option value="hbonds" title="The lengths of bonds involving a hydrogen atom are kept fixed.  Water molecules are kept rigid." selected>Bonds involving hydrogen</option>
                                                                                <option value="allbonds" title="All bond lengths are kept fixed.  Water molecules are kept rigid.">All bonds</option>
                                                                            </select>
                                                                        </div>

                                                                        <div class="mb-3" id="constraintTolRow">
                                                                            <label for="constraintTol">Constraint Error Tolerance</label>
                                                                            <input type="text" name="constraintTol" id="constraintTol" value="0.000001" class="form-control" title="The maximum allowed relative error in constrained distance.">
                                                                        </div>


                                                                    </div>
                                                                    <!--Col2-->
                                                                    <div class="col-xl-6 mb-6">
                                                                        <div class="form-group mb-3" id="ewaldTolRow">
                                                                            <label for="ewaldTol">Ewald Error Tolerance</label>
                                                                            <input type="text" name="ewaldTol" id="ewaldTol" value="0.0005" class="form-control" title="This determines the accuracy of interactions computed with PME.">
                                                                        </div>   
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>





                                                    <!--Center Card-->
                                                    <div class="col-xl-4 mb-4">
                                                        <div class="card mb-4 mb-xl-0">
                                                            <div class="card-header">Integrator Parameters</div>
                                                            <div class="card-body">

                                                            <!--Row splitter for System Parameters-->
                                                            <div class="row">
                                                                    <!--Col1-->
                                                                    <div class="col-xl-6 mb-6">
                                                                       <div class="mb-3">
                                                                          <label for="dt">Step Size (femtoseconds)</label>
                                                                          <input type="text" name="dt" id="dt" value="2" class="form-control"  title="The size of the timesteps used by the integrator.">
                                                                        </div>


                                                                        <div class="mb-3">
                                                                            <label for="ensemble">Statistical Ensemble</label>
                                                                            <select name="ensemble" id="ensemble" title="Select the statistical ensemble to simulate.  This describes how the system interacts with the surrounding environment." class="form-control" onchange="optionChanged()">
                                                                                    <option value="npt" title="The simulation includes a thermostat and barostat to sample a constant pressure, constant temperature (NPT) ensemble." selected="">Constant pressure, temperature (NPT)</option>
                                                                                    <option value="nvt" title="The simulation includes a thermostat so it samples a constant volume, constant temperature (NVT) ensemble.">Constant volume, temperature (NVT)</option>
                                                                            </select>
                                                                        </div>


                                                                        <div class="mb-3" id="temperatureRow">
                                                                            <label for="temperature">Temperature (K)</label>
                                                                            <input type="text" name="temperature" id="temperature" value="300" class="form-control" oninput="optionChanged()" title="The temperature at which the system is simulated.">

                                                                        </div>


                                                                        <div class="mb-3" id="frictionRow">
                                                                            <label for="friction">Friction Coefficient (ps<sup>-1</sup>)</label>
                                                                            <input type="text" name="friction" id="friction" value="1.0" class="form-control" oninput="optionChanged()" title="The friction coefficient coupling the system to the thermostat.">
                                                                        </div>


                                                                    </div>

                                                                    <!--Col2-->
                                                                    <div class="col-xl-6 mb-6">
                                                                        <div class="mb-3" id="pressureRow">
                                                                            <label for="pressure">Pressure (atm)</label>
                                                                            <input type="text" name="pressure" id="pressure" value="1.0" class="form-control" oninput="optionChanged()" title="The pressure at which the system is simulated.">
                                                                        </div>

                                                                        <div class="mb-3" id="barostatIntervalRow">
                                                                            <label for="barostatInterval">Barostat Interval (steps)</label>
                                                                            <input type="text" name="barostatInterval" id="barostatInterval" value="25" class="form-control" oninput="optionChanged()" title="The interval at which the barostat attempts to change the box volume, measured in time steps.">
                                                                        </div>
                                                                    </div>
                                                            
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>





                                                    <!--Right Card-->
                                                    <div class="col-xl-4 mb-4">
                                                        <div class="card mb-4 mb-xl-0">
                                                            <div class="card-header">Simulation Parameters (for all mutant decoys)</div>
                                                            <div class="card-body">
                                                                <!--Row splitter for System Parameters-->
                                                                <div class="row">
                                                                    <!--Col1-->
                                                                    <div class="col-xl-6 mb-6">
                                                                       
                                                                
                                                                       <div class="mb-3">
                                                                         <label for="steps">Simulation Length (steps)</label>
                                                                         <input type="text" name="steps" id="steps" value="10000000" class="form-control"  title="The total length of the simulation, measured in time steps.">
                                                                        </div>

                                                                        <div class="mb-3">
                                                                         <label for="equilibrationSteps">Equilibration Length (steps)</label>
                                                                         <input type="text" name="equilibrationSteps" id="equilibrationSteps" value="10000" class="form-control" title="The number of time steps of equilibration to run before starting the main simulation.">
                                                                        </div>

                                                                        <div class="mb-3">
                                                                         <label for="platform">Platform</label>
                                                                          <select name="platform" id="platform" title="Select the platform to use.  This must match the hardware you plan to run the simulation on" class="form-control" onchange="optionChanged()">
                                                                             <!--<option value="Reference" title="The Reference platform is useful for testing, but not recommended for production simulations.">Reference</option>-->
                                                                             <!--<option value="CPU" title="Run the simulation on a conventional CPU">CPU</option>-->
                                                                             <option value="CUDA" title="Run the simulation on NVIDIA GPUs" selected="">CUDA</option>
                                                                             <!--<option value="OpenCL" title="The OpenCL platform on various kinds of hardware, including NVIDIA, AMD, and Intel GPUs">OpenCL</option>-->
                                                                          </select>
                                                                        </div>

                                                                        <div class="mb-3" id="precisionRow">
                                                                          <label for="precision">Precision</label>
                                                                          <select name="precision" id="precision" title="Select the level of numerical precision to use." class="form-control" onchange="optionChanged()">                                                                        
                                                                             <option value="single" title="Calculations are done in single precision" selected="">Single</option>
                                                                             <option value="mixed" title="Use a mix of single and double precision">Mixed</option>
                                                                             <option value="double" title="Calculations are done in double precision">Double</option>
                                                                          </select>
                                                                        </div>
                                                                        <p></p>
                                                                    </div>

                                                                    <div class="col-xl-6 mb-6 align-middle ">
                                                                        <div class="card">
                                                                            <div class="card-body">
                                                                                
                                                                                <div class="ms-3">
                                                                                    <div class="text-dark d-flex justify-content-left ">Simulation Time</div>
                                                                                    <div class="d-flex justify-content-left "><h3 id="simulationtime">20 ns</h3></div>
                                                                                </div>
                                                                                <p></p>
                                                                                <div class="ms-3">
                                                                                    <div class="text-dark d-flex justify-content-left">Equilibration Time</div>
                                                                                    <div class="d-flex justify-content-left"><h3 id="equilibrationtime">20 ps</h3></div>
                                                                                </div>        
                                                                                <p></p>
                                                                                <div class="ms-3">
                                                                                    <div class="text-dark d-flex justify-content-left">Frame duration</div>
                                                                                    <div class="d-flex justify-content-left"><h3 id="frameSize">20ps</h3></div>
                                                                                </div>                                                                        
                                                                            </div>
                                                                        </div>
                                                                        <div class="mb-3" id="totalFramesRow">
                                                                          <label for="precision">Total Samples (MD frames)</label>
                                                                          <select name="totalframes" id="totalframes" title="Select how many frames to capture on each simulation. This affects your file size!" class="form-control" onchange="optionChanged()">                                                                        
                                                                             <option value="1000" title="Capture 1000 frames (default setting)" selected="">1000</option>
                                                                             <option value="5000" title="Capture 5000 frames (High resolution)">5000</option>
                                                                             <option value="10000" title="Capture 10000 frames (Ultra-high resolution)">10000</option>
                                                                          </select>
                                                                        </div>
                                                                        <br />
                                                                       
                                                                    </div>

                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>                                                




                                                    
                                            </div>
                                            <hr class="my-4" />
                                            <div class="d-flex justify-content-right">
                                            <button class="btn btn-primary" type="button" id="btnNextStep4" onclick="validateStep3()">Next Step</button>
                                            </div>
                                        </form>

                                    </div>
                                </div>
                            </div>


















                                    
                                    
                                    
                            






                            <!-- Wizard tab pane item 4-->
                            <div class="tab-pane py-5 py-xl-12 fade" id="wizard4" role="tabpanel" aria-labelledby="wizard4-tab">
                                <div class="row justify-content-center">
                                    <div class="col-xxl-12 col-xl-12">
                                        <h3 class="text-primary">Step 3</h3>
                                        <h5 class="card-title mb-4">Setup Anchor Points and DYME Pipeline</h5>
             
                                        <!--Leftmost Pane -->                    
                                        <div class="row">

                                                <div class="col-xl-6">
                                                    <!-- Profile picture card-->
                                                    <div class="card mb-4 mb-xl-0">
                                                        <div class="card-header">System Viewer</div>
                                                        <div id="step4viewport" style="width:100%; min-height: 300px;">
                                                            <!-- PDB FILE IN HERE -->
                                                            <div><br /></div>
                                                            <div></div>
                                                            <div id="step4loading">
                                                                <div class="d-flex justify-content-center align-middle">
                                                                    <div class="spinner-border" role="status"> </div> &nbsp;<br /><br />
                                                                    
                                                                </div>
                                                                <div class="d-flex justify-content-center align-middle"><h5>Loading Structure</h5></div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                        


                                                <!--DYME OPTIONS pane-->
                                                <div class="col-xl-6">                                                
                                                 <div class="accordion" id="accordionDYME">

                                                    <!-- NAMING MOLECULES-->
                                                    <div class="card card-collapsable mb-4">
                                                        <a class="card-header" href="#collapseDyme1" data-bs-toggle="collapse" role="button" aria-expanded="true" aria-controls="collapseDyme1">1. Group Chains into Molecular Objects
                                                            <div class="card-collapsable-arrow">
                                                                <i class="fas fa-chevron-down"></i>
                                                            </div>
                                                        </a>
                                                        <div id="collapseDyme1" class="collapse show" aria-labelledby="heading1" data-parent="#accordionDyme">
                                                         <div class="card-body">
                                                            <form name="DYMEnames" id="DYMEnames">
                                                                <label class="small">
                                                                    - Create and name each molecular object in your complex. Use the button to add objects.<br />
                                                                    - Assign chains to its corresponding Molecular Object. Use the dropdown under the Chain Selector column.<br />
                                                                    - Use the Offset field of each chain to dfine its proper indexing. Leave at 0 to keep the original indexing.<br />
                                                                    - Set at least one Molecular Object as "Mutable". 
                                                                    
                                                                </label>
                                                                <br />
                                                                <br />
                                                                
                                                                <div>
                                                                    <button id="addMolecule" class="btn btn-primary" type="button">+Add Molecular Object</button>
                                                                    <button id="resetAddMolecule" class="btn btn-warning" type="button">Reset Object List</button>
                                                                </div>
                                                                
                                                                <div class="col-xl-12">
                                                                    <table class="table table-m">
                                                                        <thead>
                                                                            <th width="5%"></th>
                                                                            <th width="25%">Object Name</th>
                                                                            <th width="20%">Chain Selector</th>
                                                                            <th width="30%">Chain:First Res | Index</th>
                                                                            <th width="20%">Mark as Mutable</th>
                                                                        </thead>
                                                                        
                                                                        <tbody id="tablanames">
                                                                            <tr>
                                                                                <td><div class="colorPickSelector" id="mol1"></div></td>

                                                                                <td><input type="text" name="molname[1]" id="molname[1]" value="" placeholder="Desired Name" class="form-control"></td>
                                                                                
                                                                                <td id="chainselectortd1">
                                                                                    <select id="chainselector[1]" class="form-control" onselect="addChainToObject(this)">
                                                                                        <option>Add Chain...</option>
                                                                                        <option>ChainA</option>
                                                                                        <option>ChainB</option>
                                                                                    </select>
                                                                                </td>
                                                                                <td>
                                                                                    <ul id="resindextd1" class="list-unstyled" style="overflow: auto; white-space: nowrap;">
                                                                                        <li class="float-start align-middle" hidden>
                                                                                            <div class="w-5 d-inline-flex"></div>
                                                                                            <div class="w-25 d-inline-flex"><input type="text" name="A" id="A" value="0"  maxlength="4" placeholder="Real Position" class="form-control"></div>
                                                                                        </li>
                                                                                    </ul>
                                                                                </td>
                                                                                <td>
                                                                                    <div class="form-check align-left">
                                                                                        <input class="form-check-input float-start" type="checkbox" id="mutable[1]">
                                                                                        <label class="form-check-label float-start" for="flexCheckDefault">
                                                                                           Mutable?
                                                                                        </label>
                                                                                    </div>
                                                                                </td>

                                                                            </tr>




                                                                        </tbody>
                                                                    </table>
                                                                </div>
                                                                
                                                                
                                                                <!-- Save changes button-->
                                                                <div class="row">
                                                                    <div id='nextDiv1'class="col-md-12" hidden>
                                                                    <hr class="my-4" />
                                                                    <button id="nextDYME1" class="btn btn-secondary float-end" type="button">Next</button>
                                                                </div>
                                                                </div>

                                                            </form>
                                                         </div>
                                                        </div>
                                                    </div>


                                                    <!-- ANCHOR POINT SELECTOR -->
                                                    <div class="card card-collapsable mb-4">
                                                        <a class="card-header" href="#collapseDyme2" data-bs-toggle="collapse" role="button" aria-expanded="false" aria-controls="collapseDyme2">2. Set Anchor Points
                                                            <div class="card-collapsable-arrow">
                                                                <i class="fas fa-chevron-down"></i>
                                                            </div>
                                                        </a>
                                                        <div id="collapseDyme2" class="collapse" aria-labelledby="heading2" data-parent="#accordionDyme">
                                                         <div class="card-body">
                                                            <form name="DYMEanchors" id="DYMEanchors">
                                                                    <div class="row" id="anchorpointgrids">

                                                                        <!-- Save changes button -->
                                                                        <div class="d-flex justify-content-center align-middle">
                                                                            <div class="spinner-border" role="status"> </div> &nbsp;<br /><br />

                                                                            </div>
                                                                            <div class="d-flex justify-content-center align-middle"><h5>Generating Residue Table</h5>
                                                                        </div>
                                                                    
                                                                    
                                                                    <!-- Save changes button-->
                                                                    </div>
                                                                    <div class="row">
                                                                        <div class="col-md-12">
                                                                            <hr class="my-4" />
                                                                            <button id="nextDYME2" class="btn btn-secondary float-end" type="button">Next</button>
                                                                        </div>
                                                                    </div>
                                                            </form>
                                                         </div>
                                                        </div>
                                                    </div>  












                                                    <!-- DYME SETTINGS SELECTOR -->
                                                    <div class="card card-collapsable mb-4">
                                                        <a class="card-header" href="#collapseDyme3" data-bs-toggle="collapse" role="button" aria-expanded="false" aria-controls="collapseDyme3">3. DYME Analysis Settings
                                                            <div class="card-collapsable-arrow">
                                                                <i class="fas fa-chevron-down"></i>
                                                            </div>
                                                        </a>
                                                        <div id="collapseDyme3" class="collapse" aria-labelledby="heading3" data-parent="#accordionDyme">
                                                         <div class="card-body">
                                                            <form name="DYMEsettings" id="DYMEsettings">
                                                                    <div class="row" id="settingsgrid">

                                                                    <table class="table table-m">
                                                                                                                                                
                                                                        <tbody id="analysis_table">
                                                                            <tr>
                                                                                <td><label class="fw-bold">Energetics Analysis</label></td>
                                                                                <td class="justify-content-evenly">
                                                                                    <div class="form-check form-check-inline">
                                                                                        <input class="form-check-input" id="energy_gbsa" type="radio" name="energy_type" value="gbsa" onchange="togglePB('pb')" checked>
                                                                                        <label class="form-check-label" for="energy_gbsa">MM-GBSA</label>
                                                                                        <i class="icon-users" data-feather="help-circle" data-bs-toggle="tooltip" data-bs-placement="top" title="Much faster, but not as accurate"></i>
                                                                                    </div>
                                                                                    <div class="form-check form-check-inline">
                                                                                        <input class="form-check-input" id="energy_pbsa" type="radio" name="energy_type" value="pbsa" onchange="togglePB('gb')">
                                                                                        <label class="form-check-label" for="energy_pbsa">MM-PBSA</label>
                                                                                        <i class="icon-users" data-feather="help-circle" data-bs-toggle="tooltip" data-bs-placement="top" title="Slower, but reliable. May fail with 'exotic' systems. Use with care"></i>
                                                                                    </div>
                                                                                    <div class="form-check">
                                                                                        <input class="form-check-input justify-content-evenly" type="checkbox" id="energy_pairwise" checked>
                                                                                        <label class="form-check-label justify-content-evenly" for="energy_pairwise">Pairwise</label>
                                                                                        </div>
                                                                                    <div class="form-check">
                                                                                        <input class="form-check-input justify-content-evenly" type="checkbox" id="energy_perresidue" checked>
                                                                                        <label class="form-check-label justify-content-evenly" for="energy_perresidue">Per-Residue</label>
                                                                                        </div>
                                                                                    <div class="form-check">
                                                                                        <input class="form-check-input justify-content-evenly" type="checkbox" id="energy_total" checked>
                                                                                        <label class="form-check-label justify-content-evenly" for="energy_total">Total</label><br>
                                                                                    </div>    
                                                                                    <div class="form-check" id="igbcheck">
                                                                                        <label class="form-check-label justify-content-evenly" for="igb">GBSA Method (igb)</label>
                                                                                        <select class="justify-content-evenly" id="igb"><option value="2" selected>2 (Case, et al 2004)</option><option value="8">8 (GBn 2015) + mbondi3</option></select>
                                                                                    </div>

                                                                                    <div class="form-check" id="inpcheck" style="display: none;">    
                                                                                        <label class="form-check-label justify-content-evenly" for="inp">Non-polar Method (inp)</label>
                                                                                        <select class="justify-content-evenly" id="inp"><option value="0">0 (Don't compute)</option><option value="1" selected>1 (Single Term Linear)</option><option value="2">2 (Dual Term)</option></select>
                                                                                        <i class="icon-users" data-feather="help-circle" data-bs-toggle="tooltip" data-bs-placement="top" title="Defines how to compute non-polar solvation. Default is 2, but 1 works better for large interfaces. Read the Amber manual"></i>
                                                                                    </div>
                                                                                </td>
                                                                            </tr>

                                                                            <tr>
                                                                            <td><label class="fw-bold">RMSD Type</label></td>
                                                                                <td class="justify-content-evenly">
                                                                                    <div>
                                                                                    <input class="form-check-input " type="checkbox" id="rmsd_averaged"  checked>
                                                                                    <label class="form-check-label " for="energy_pairwise">Averaged (whole molecule)</label>
                                                                                    </div><div>
                                                                                    <input class="form-check-input " type="checkbox" id="rmsd_percarbon"  checked>
                                                                                    <label class="form-check-label " for="energy_perresidue">One RMSD per alpha Carbon</label>
                                                                                    </div>
                                                                                </td>
                                                                            </tr>

                                                                            <tr>
                                                                            <td><label class="fw-bold">Contact Counting</label></td>
                                                                                <td class="justify-content-evenly">
                                                                                    <div>
                                                                                    <input class="form-check-input " type="checkbox" id="bonds_hbonds"  checked>
                                                                                    <label class="form-check-label " for="energy_pairwise">H-bonding</label>
                                                                                    </div><div>
                                                                                    <input class="form-check-input " type="checkbox" id="bonds_vdv"  checked>
                                                                                    <label class="form-check-label " for="energy_perresidue">VdW </label>
                                                                                    <br />
                                                                                    </div>

                                                                                    <div>
                                                                                    
                                                                                    <label class="inline-flex" for="bonds_threshold">Contact Frecuency Threshold (%)</label>
                                                                                    <input type="number" name="bonds_threshold" id="bonds_threshold" value="10" placeholder="Threshold" class="form-control w-25 inline-flex" min="1" max="100"> 
                                                                                    
                                                                                    </div>

                                                                                </td>
                                                                            </tr>

                                                                            <tr>
                                                                            <td><label class="fw-bold">Aditionals </label></td>
                                                                                <td class="justify-content-evenly">
                                                                                    <div>
                                                                                    <input class="form-check-input " type="checkbox" id="principal_component" checked>            
                                                                                    <label class="form-check-label " for="principal_component">Principal Component Analysis</label>   
                                                                                    </div>                                                                                
                                                                                </td>
                                                                            </tr>
                                                                            <tr>
                                                                            <td><label class="fw-bold">Water Processing</label></td>
                                                                                <td class="justify-content-evenly">
                                                                                    <div>
                                                                                        <input class="form-check-input " type="checkbox" id="water_track_interface"  checked>
                                                                                        <label class="form-check-label " for="water_track_interface">Track waters inside the PPI</label> 
                                                                                    </div>
                                                                                    <div>
                                                                                        <input class="form-check-input " type="checkbox" id="water_track_all" disabled>
                                                                                        <label class="form-check-label " for="energy_pairwise">Track every water (for future use)</label> 
                                                                                    </div>

                                                                                </td>
                                                                            </tr>

                                                                            <tr>
                                                                            <td><label class="fw-bold">Pharmacophore Configs</label></td>
                                                                                <td class="justify-content-evenly">
                                                                                    <div>
                                                                                        <input class="form-check-input " type="checkbox" id="pharmacophores_autogen" disabled>
                                                                                        <label class="form-check-label " for="water_track_interface">Generate Dynamic Pharmacophores</label> 
                                                                                    </div>
                                                                                    <div>
                                                                                    
                                                                                    </div>

                                                                                </td>
                                                                            </tr>
                                                                            <tr>
                                                                            <td><label class="fw-bold">AI/ML Configs</label></td>
                                                                                <td class="justify-content-evenly">
                                                                                    <div>
                                                                                        <input class="form-check-input " type="checkbox" id="aiml_activate" disabled>
                                                                                        <label class="form-check-label " for="aiml_activate">Activate AI-guided mutagenesis</label> 
                                                                                    </div>
                                                                                </td>
                                                                            </tr>


                                                                        </tbody>
                                                                    </table>




                                                                    
                                                                    <!-- Save changes button-->
                                                                    </div>
                                                                    <div class="row">
                                                                        <div class="col-md-12">
                                                                            <hr class="my-4" />
                                                                            <button id="nextDYME3" class="btn btn-secondary float-end" type="button">Next</button>
                                                                        </div>
                                                                    </div>
                                                            </form>
                                                         </div>
                                                        </div>
                                                    </div>  








                                                    <!-- DYME SETTINGS SELECTOR -->
                                                    <div class="card card-collapsable mb-4">
                                                        <a class="card-header" href="#collapseDyme4" data-bs-toggle="collapse" role="button" aria-expanded="false" aria-controls="collapseDyme4">4. Pipeline Mutagenesis Settings
                                                            <div class="card-collapsable-arrow">
                                                                <i class="fas fa-chevron-down"></i>
                                                            </div>
                                                        </a>
                                                        <div id="collapseDyme4" class="collapse" aria-labelledby="heading4" data-parent="#accordionDyme">
                                                         <div class="card-body">
                                                            <form name="DYMEmutagenesis" id="DYMEmutagenesis">
                                                                    <div class="row" id="mutagenesis">
                                                                        <div>
                                                                            <h5>Mutagenesis Matrix</h5><br />
                                                                            <input class="form-check-input justify-content-evenly" type="radio" name="inlineradio_mutagenesis" id="inlineradio_mutagenesis" value="mutagenesis_useall" checked>
                                                                            <label class="form-check-label justify-content-evenly" for="mutagenesis_useall">All standard residues for all Anchor points</label>
                                                                            </div><div>
                                                                            <input class="form-check-input justify-content-evenly" type="radio" name="inlineradio_mutagenesis" id="inlineradio_mutagenesis" value="mutagenesis_choose" onclick="">
                                                                            <label class="form-check-label justify-content-evenly" for="mutagenesis_choose">Restrict residues per Anchor point</label>
                                                                        </div>


                                                                        <table class="table table-m" id="tablemutagenesis" hidden>     
                                                                            <thead>
                                                                                    <th>Anchor</th>
                                                                                    <th>A</th>
                                                                                    <th>V</th>
                                                                                    <th>L</th>
                                                                                    <th>I</th>
                                                                                    <th>P</th>
                                                                                    <th>M</th>
                                                                                    <th>F</th>
                                                                                    <th>W</th>
                                                                                    <th>G</th>
                                                                                    <th>D</th>
                                                                                    <th>E</th>
                                                                                    <th>K</th>
                                                                                    <th>R</th>
                                                                                    <th>H</th>
                                                                                    <th>T</th>
                                                                                    <th>S</th>
                                                                                    <th>Q</th>
                                                                                    <th>C</th>
                                                                                    <th>Y</th>
                                                                                    <th>N</th>
                                                                                    <th>Presets</th>
                                                                            </thead>                                                               
                                                                            <tbody id="mutagenesis_table">
                                                                                
                                                                            </tbody>
                                                                        </table>

                                                                    </div>
                                                                    
                                                                    <!-- Save changes button-->
                                                                    <div class="row"><div class="col-md-12">                                                                    
                                                                            <hr class="my-4" />
                                                                            <button id="nextDYME4" class="btn btn-secondary float-end" type="button">Next</button>
                                                                        </div>
                                                                    </div>
                                                            </form>
                                                         </div>
                                                        </div>
                                                    </div>  


                                                








                                                    <!-- DYME VLUSTERING SELECTOR -->
                                                    <div class="card card-collapsable mb-4">
                                                        <a class="card-header" href="#collapseDyme5" data-bs-toggle="collapse" role="button" aria-expanded="false" aria-controls="collapseDyme5">5. Clustering Logic
                                                            <div class="card-collapsable-arrow">
                                                                <i class="fas fa-chevron-down"></i>
                                                            </div>
                                                        </a>
                                                        <div id="collapseDyme5" class="collapse" aria-labelledby="heading5" data-parent="#accordionDyme">
                                                         <div class="card-body">
                                                            <form name="DYMEclustering" id="DYMEclustering">
                                                                    <div class="row" id="clustering">
                                                                        <div>
                                                                            <h5>Anchor Point Clustering</h5><br />
                                                                        </div>
                                                                        <!--Buttons -->
                                                                        <div class="col-xl-12"> 
                                                                            <button id="addCluster" class="btn btn-primary" type="button">+ Add new Cluster</button>
                                                                            <button id="resetAddCluster" class="btn btn-info" type="button">Reset Clustering</button><br />
                                                                            <label class="small">
                                                                                - Drag and drop anchorpoints into their clusters<br />
                                                                            </label>
                                                                        </div>
                                                                        
                                                                       
                                                                        <div class="col-xl-12">&nbsp;</div>

                                                                        <!--Anchor point divs -->
                                                                        <div class="col-xl-12">
                                                                            <fieldset id="anchordivs">

                                                                            </fieldset>
                                                                        </div>
                                                                        <div class="col-xl-12">&nbsp;</div>
                                                                        
                                                                        
                                                                        <!--Cluster DIVs -->
                                                                        <div class="col-xl-5">
                                                                            <div id="clusters" class="form-group">
                                                                                <label for="selectcluster1">Cluster 1</label><br />
                                                                                <select class="form-control droppable w-50 me-3 p-2" id="selectcluster1" multiple=""></select> 
                                                                                <button type="button" id="dropfromcluster1" name="dropfromcluster1" onclick="dropfromcluster(1, this)" class="btn btn-xs btn-danger">Drop Selected</button>
                                                                            </div>
                                                                        </div>
                                                                        <div class="col-xl-2 vr"></div>
                                                                        <div class="col-xl-5">
                                                                            <div class="row">
                                                                            <h5>Estimated Computational Complexity</h5><br />
                                                                            <div class="col-xl-12 justify-content-center">
                                                                                <table class="dataTable-table">
                                                                                    <thead>
                                                                                        <th>Mux. Mode</th>
                                                                                        <th>Total Mutants</th>
                                                                                        <th>Estimated Runtime</th>
                                                                                    </thead>
                                                                                    <tbody>
                                                                                        <tr class="text-center">
                                                                                            <td class="fw-bold">Singlets</td>
                                                                                            <td id="singlets"></td>
                                                                                            <td id="singlets_time"></td>

                                                                                        </tr>

                                                                                        <tr class="text-center">
                                                                                            <td class="fw-bold">Duplets</td>
                                                                                            <td id="duplets"></td>
                                                                                            <td id="duplets_time"></td>
                                                                                        </tr>

                                                                                        <tr class="text-center">
                                                                                            <td class="fw-bold">Triplets</td>
                                                                                            <td id="triplets"></td>
                                                                                            <td id="triplets_time"></td>
                                                                                        </tr>

                                                                                        <tr class="text-center">
                                                                                            <td class="fw-bold">TOTAL</td>
                                                                                            <td class="fw-bold" id="total_mutants"></td>
                                                                                            <td class="fw-bold" id="total_tuntime"></td>
                                                                                        </tr>

                                                                                    </tbody>
                                                                                </table>

                                                                            </div>
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                    
                                                                    <!-- Save changes button-->
                                                                    <div class="row"><div class="col-md-12">                                                                    
                                                                            <hr class="my-4" />
                                                                            <button id="nextDYME5" class="btn btn-secondary float-end" type="button">Next</button>
                                                                        </div>
                                                                    </div>
                                                            </form>
                                                         </div>
                                                        </div>
                                                    </div>  











                                                    <!-- DYME SETTINGS SELECTOR 
                                                    <div class="card card-collapsable mb-4">
                                                        <a class="card-header" href="#collapseDyme6" data-bs-toggle="collapse" role="button" aria-expanded="false" aria-controls="collapseDyme6">6. Review & Save Configuration
                                                            <div class="card-collapsable-arrow">
                                                                <i class="fas fa-chevron-down"></i>
                                                            </div>
                                                        </a>
                                                        <div id="collapseDyme6" class="collapse" aria-labelledby="heading6" data-parent="#accordionDyme">
                                                         <div class="card-body">
                                                            <form name="DYMEreview" id="DYMEreview">
                                                                    <div class="row" id="datareview">
                                                                        <div>
                                                                            <h5>Configuration Summary </h5><br />
                                                                        </div>


                                                                    </div>
                                                                    
                                                                   
                                                                    <div class="row"><div class="col-md-12">                                                                    
                                                                            <hr class="my-4" />
                                                                            <button id="nextDYME7" class="btn btn-secondary float-end" type="button">Finish Wizzard and Launch</button>
                                                                        </div>
                                                                    </div>
                                                            </form>
                                                         </div>
                                                        </div>
                                                    </div> 
                                                    -->

                                                 </div>
                                                </div>
                                        </div>

                                    </div>
                                </div>
                            </div>



                        </div>
                    </div>
                </main>











<!-- MODAL WINDOWS OF THE WIZZARD-->
<!-- Modal Step1-->
<div class="modal fade" id="wizzardModal" tabindex="-1" role="dialog" aria-labelledby="errorTitle" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="errorTitle">MESSAGE</h5>
                <button class="btn-close" type="button" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body" id="errorMessage">ERROR</div>
            <div class="modal-footer">
                <button class="btn btn-secondary" type="button" data-bs-dismiss="modal">Close</button>
                
        </div>
    </div>
</div>