//Variable list
var mutantList = {}
var dataTable1 = ""
var dataTable2 = ""
var dataTable3 = ""
var reference  = 0
var weblogo1 = ""
let residuemap = ""
let path_to_project = ""
var mutanth = ""
var mutantd = { }
var filterCriteria = []
var displayNGLinsteadOfPDB = true
var contactThreshold = ""
var energy = {}
var seqvalues = []
var origsequence = []
var seqMethod = "selfMutant"
var currentOrder = "mutantID"
var selectSegment = "L"

//Control simulation replicas
var replica_elements = {}
var processed_mutants

//Component Objects
let charts = [];
let rmsd_chart;
let energy_chart;
let heatmap_chart;
let pairwise_chart;

//NGL Component Objects
let viewer;
let trajectories;
let structure;
let stage;
let setspin = true;
let molStructure;
let wildtype;
let receptorresidues;
let seleres;
// Object to store groups by numeric index
var groupsNGL = {};
var waterdisplay = {};

// Pairwise mini-plugin to add rightward offets to points
var pairwise_offset = 0;
var isthresholdchange = false
var thresholdMap = 0.4
var maxenergyofseries = 0


//Detect when the user releases the mouse button after sliding energy threshold
slider = document.getElementById('thresholdSlider');
slider.addEventListener('pointerdown', () => {
    const pointerUpHandler = () => {
        console.log('Pointer released, value =', slider.value);
        setTimeout(() => {
            resetZoom('pairwise');
        }, 1000);
        document.removeEventListener('pointerup', pointerUpHandler);
    };
    document.addEventListener('pointerup', pointerUpHandler);
});

//
document.getElementById('thresholdSlider').addEventListener('input', function () {
  thresholdMap = -parseFloat(this.value);
  document.getElementById('thresholdValueLabel').textContent = thresholdMap.toFixed(1)+" kcal/mol";

    isthresholdchange = true
    pairwise_chart.update();
});

//Siple tool to order two sets of labels ascending
const sortResidueLabels = arr =>
  [...new Set(arr)].sort((a, b) =>
    (parseInt(a?.slice(1)) - parseInt(b?.slice(1))) || a.localeCompare(b)
  );

const shiftPlugin = {
    id: 'shiftPlugin',
    afterUpdate: function(chart) {
        if(!isthresholdchange){
            //console.log("im hereeeeeeee")
            var offset = 0;
            chart.config.data.datasets.forEach((dataset, datasetIndex) => {
                const meta = chart.getDatasetMeta(datasetIndex); // Correct way to get metadata
                meta.data.forEach((element) => {
                    if (element.x !== undefined) {
                        element.x += offset; // Shift each dataset by offset
                    }
                });
                offset += 5;          
            })
        } else {
            console.log("is threshold change");
            isthresholdchange = false;
        }
    }
}

var stats

//Mutant Colors - stores colors of mutants being displayed
let mutantColors = []


//Hbonds Table
var mutantObjects = []

var allcppcontacts = []

var positionElement = `
<ul class="tree">
    <li>
        <details open>
        <summary>||pos||</summary>
        <ul>
            ||aminos||
        </ul>
        </details>
    </li>
</ul>`;

var aminoElement = `
<li>
<details>
    <summary>||amino1||</summary>
        <ul>
            ||atoms||
        </ul>
</details>
</li>`;

var atomElement = `<li>
<details>
    <summary>||atomOrig1||</summary>
        <ul>
            ||atoms_desti||
        </ul>
</details>
</li>`;


var sidechainstring = "Sidechain"
var dna = ['DA','DT','DC','DG']
//Controls which source to use
var dict_cpptraj_index = "cpptraj_forward"
var filterByName = "_"
var current_wildtype = 1


/////////////////////////////////////////////////////////////////////////////////////////////
// A $( document ).ready() block.
$( document ).ready(function() {
    $('#staticBackdrop').modal('show');
    getProjectData()
    getMutantTable()
    
    //dataTable1 = new DataTable("#datatableswildtype", {sortable: false, pageLength: 1, paging: false, scrollY: false, scrollX: false, lengthChange: false, bFilter: false, bInfo: false}) // This is old code for a redundant table that used to display wildtype baseline
    dataTable2 = new DataTable("#datatablesmutants", {sortable: true, scrollCollapse: true, pageLength: 100, select: {style: 'os'},paging: true, scrollY: '60vh', lengthChange: false, bFilter: true, bInfo: false, order: [4, 'asc']})
    $('#datatablesmutants_filter').hide()
    //Datatable for Hbond data
    dataTable3 = new DataTable("#datatableshbonds", {sortable: true, scrollCollapse: false, pageLength: 10, paging: false,  bFilter: false, bInfo: false,   order: [[1, 'asc']],
    columns: [
        {
            className: 'dt-control',
            orderable: false,
            data: null,
            defaultContent: ''
        },
        {  },
        {  },
        {  },
        {  }
    ], pageResize: true
    })



    //Handle Double click on Mutant table
    $('#datatablesmutants').on('dblclick','tr',function(e){
        let rowID = dataTable2.row(this).data()[0]
        dataTable2.rows(this).select()
        //alert("clicked row "+rowID)
        loadMutantDetail(rowID) //Fills Right panel with single mutant info
    })

    // Add event listener for opening and closing details in hbond data
     $("#datatableshbonds").on('click', 'td.dt-control', function (e) {
        let tr = e.target.closest('tr');
        let row = dataTable3.row(tr);
       
        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
        }
        else {
            // Open this row
            row.child(format(row.data()[1])).show();
        }
    });

    //Handle rigPAht click on Mutant table
    $("#datatablesmutants").contextMenu({
        selector: 'tr',
        zIndex: 100000,
        trigger: 'right',
        callback: function(key, options) {         
          var mutant = dataTable2.row(options.$trigger).data()
          
          switch (key) {
            case 'show' :
                //loadMutantDetail(mutant[0]) //This simply shows the mutant
                toggleTag(mutant[0])
            break;
            case 'triplicate' :
                if (confirm('Are you sure you want to simulate mutant '+mutant[0]+' in triplicate?. Simulations will be queued immediately')) {
                    //action confirmed
                    idm = mutant[0]
                    verifyInTriplicate(idm)
                    // 
                  } 
            break;
            case 'replicas' :
                subtable(mutant[0]);
            break;
            case 'addmore':
                var howmany = prompt("Enter how many more simulations to run")
                howmany = +howmany
                if(howmany > 0){
                    if(confirm("Are you sure you'd like to simulate this mutant "+howmany+" more times?")){
                        idm = mutant[0]
                        simulateAgain(idm, howmany) 
                    }
                } else {
                    return 
                }

            break;
            default :
            break
          }  
        },
        items: {
          "show": {name: "Tag/Untag +", icon: "edit"},
          "triplicate": {name: "Confirm in triplicate", icon: "add"},
          "addmore": {name: "Run more simulations", icon: "loading"},
          "replicas": {name: "Show all replicas", icon: "paste"},
          

        }
      }) 
      

})


//SHOW MUTANT DETAIL (SINGLE MUTANT)
function loadMutantDetail(mutantID){
    var isset = mutantColors.find(obj => {
        return obj.mutantID === mutantID
    })

    if(isset == undefined){
        //Call API to create info for individual mutants
        getRMSDSingle(mutantID) //Generate RMSD Table

        setTimeout(function(){
            getENERGYSingle(mutantID) //Generate Energy Table
            //getHEATMAPSingle(mutantID)
            getPAIRWISESingle(mutantID)
            getNGLViewer(mutantID)
            addMutantButtons(mutantID)
            //console.log("adding mutant "+mutantID)
            countHbonds(mutantID)
        },1000)
    } else {
        alert("This mutant is already on-screen")
    }

    
}

//Process Async response from callApi - All API responses are asynchronously sent here
function processResult(res){
    console.log("Got response from server API for "+res['action'])

    switch(res['action']) {
        //Render the current table of mutants   
        
        case 'render_project':
            //Change page
            $("#titlepage").html(res["response"][0]["name"])
            path_to_project = res["response"][0]["project_folder"]
        break;



        case 'fillMutantTable_initial':
            //Change Modal
            component = res['component']
            //do stuff with the modal

            //Render Table
            mutantList = res['response']
            renderMutantTable()
        break;
        


        //Render RMSD Table for Single Mutant
        case 'render_RMSD_graph':
          // code block
          component  = res['component']
          response   = res['response']
          paintRMSD_single(component, response)
        break;


        //Render ENERGY Table for Single Mutant
        case 'render_ENERGY_graph':
          // code block
          component  = res['component']
          response   = res['response']
          paintENERGY_single(component, response)
          paintSequenceExplorer(component, response, false)

        break;


        //Render pairwise Matrix
        case 'render_ENERGY_pairwise':
          component  = res['component']
          response   = res['response']
          paintENERGY_pairwise(component, response)
        break;

        //Render Mutant into 3D Viewer
        case 'render_NGLmodel':
          component  = res['component']
          response   = res['response']
          loadNGLViewer($(component), response)
        break;

        //Render Mutant into 3D Viewer
        case 'renderWebLogo':
          component  = res['component']
          response   = res['response']
          calculateMutantWebLogos($(component), response)
        break;

        case 'launch_vmd_external':
            component = res['component']
            response  = res['response']
            file = res['content']
            mutidv = res['mutantidvmd']
            launchVMD(component, response, file, mutidv)
        break;
        
        case "render_hbonds_table":
            component = res['component']
            response  = res['response']
            renderHbondsTable(component, response)
        break;

        case "filter_table":
            ids = res["response"]
            filterByMutations(ids)
        break;

        case "toggle_tag":
            ids = res["response"]
            alert("Mutant has been tagged/untagged")
        break;

        case "returnTriplicateQueue": // Added support for triplicate validation PEDRO AUG 2024
            alert(res["response"])
        break;

        case "returnSimulateAgain": // Added support for launching an arbitrary number of mutants
            alert(res["response"])
        break;

        case "queued_simulation":
            ids = res["response"]
            console.log("New mutantID is: "+ids)
        break;
        default:
          // code block
          alert("Couldn't find an API response handler for "+res['action']+". I've dumped the json response to the log console")
          console.log(res["response"])
        break;
    }
}

//Handle Modal WdataTable2arnings
function showLoading(){
    
}

//////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////

//Tag a mutant for refinement
function toggleTag(mutid){
    var id = { idproject: $("#idproject").val(), mutantid: mutid}
    callApi("toggleTagMutant","",id, true)
}

//Gets a list of all mutants for project (these exist in mongodb db.mutants)
function getMutantTable(){
    var id = { idproject: $("#idproject").val()}
    callApi("getMutantStatusTable","",id, true)
}

//Gets Project Title and Path.. maybe later we can get more things if we need to
function getProjectData(){
    var id = { idproject: $("#idproject").val()}
    callApi("getProjectData","",id, true)
}

//GETS THE RMSD DATA OF A SINGLE MUTANT
function getRMSDSingle(mutantID = 0){
    if(mutantID != 0){
        var id = { idproject: $("#idproject").val(), mutantID: mutantID}
        callApi("getMutantRMSD","",id,true)
    }
}

function getENERGYSingle(mutantID = 0){
    if(mutantID != 0){
        var id = { idproject: $("#idproject").val(), mutantID: mutantID}
        callApi("getMutantEnergy","",id,true)
    }
}

function getPAIRWISESingle(mutantID = 0){
    if(mutantID != 0){
        var id = { idproject: $("#idproject").val(), mutantID: mutantID}
        callApi("getPairwiseMap","",id,true)
    } 
}

function getNGLViewer(mutantID = 0){
    if(mutantID != 0){
        var id = { idproject: $("#idproject").val(), mutantID: mutantID}
        callApi("getBestMutantPose","",id,true)
    } 
}

function getWebLogoSingle(){
    var id = { idproject: $("#idproject").val()} 
    //callApi("getMutantWebLogo","",id,true)
}

//VMD launcher buttons
function launchOnVMD(mutantID = 0){
    var id = { idproject: $("#idproject").val(), mutantID: mutantID}
    $('#modalVMD').modal('show');
    callApi("launchVMD","",id, true)
}


//HBOND counter For mutant
function countHbonds(mutantID = 0){
    var id = { idproject: $("#idproject").val(), mutantID: parseInt(mutantID)}
    //$('#modalVMD').modal('show');
    callApi("getHbondTable","",id, true)
}

//Ask server to return list of filtered ids  counter For mutant
function filterTable(){
    $("#filterModal").modal('toggle');
    $("#staticBackdrop").modal('toggle');
    var id = {idproject: $("#idproject").val(), criteria: filterCriteria}
    callApi("getFilterTable","",id, true)
}

//Adds a new mutant to the queue
function enqueueNewMutant(){
    var id = {idproject: $("#idproject").val(), criteria: filterCriteria}
    callApi("addMutantFromFilter","",id, true)
    alert("Mutant was queued for simulation")
}

function verifyInTriplicate(mid){
    var id = { idproject: $("#idproject").val(), mutantid: mid}
    callApi("verifyInTriplicate","",id, true)
}

function simulateAgain(mid, howmany){
    var id = { idproject: $("#idproject").val(), mutantid: mid, iterations: howmany}
    callApi("simulateAgain","",id, true)
}


//Renders the initial Mutant table and wildtype table ///////////////////////////////////////////////////// YOU ARE CALLING THE WILDTYPE LOAD FUNCTIONS HERE!!! AT THE END
function renderMutantTable(){

     
    //wildtype
    mutants     = mutantList["muts"] //Contains all mutants from the project that are already DONE
    replicas    = mutantList["replicas"] // Contains the records of mutants verified in triplicate
    processed   = mutantList["proc"]
    residuemap  = mutantList["proj"][0]["residuemap"]
    clusters    = mutantList["proj"][0]["clusters"]
    stats       = mutantList["descriptive"]
    maxgain     = 0
    percentgain = 0
    totalmutants = 0
    svgup = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-up" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 15a.5.5 0 0 0 .5-.5V2.707l3.146 3.147a.5.5 0 0 0 .708-.708l-4-4a.5.5 0 0 0-.708 0l-4 4a.5.5 0 1 0 .708.708L7.5 2.707V14.5a.5.5 0 0 0 .5.5z"></path></svg>'
    svgdown = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-down" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 1a.5.5 0 0 1 .5.5v11.793l3.146-3.147a.5.5 0 0 1 .708.708l-4 4a.5.5 0 0 1-.708 0l-4-4a.5.5 0 0 1 .708-.708L7.5 13.293V1.5A.5.5 0 0 1 8 1z"></path></svg>'
    //Fill
    //dataTable1.clear() // This is old code for a redundant table that used to display wildtype baseline
    dataTable2.clear()


    //TODO:
    //PENDING - MAYBE YOU'LL WANT TO SIMULATE THE WILDTYPE IN TRIPLICATE FROM SCRATCH.
    //YOU'D HAVE TO MODIFY THIS PART TO AVERAGE THE WILDTYPE.
    //AUG 2040

    //Extract wildtype - ID 1
    mutants.forEach(function(mutant){
        if(mutant['mutantID'] == 1){
            a  = processed.find(o => o.mutantID === 1);
            //console.log(processed)
            wt = [a.status, Math.round(a.deltag_total * 10)/10]
            reference = Math.round(a.deltag_total * 10)/10
            //dataTable1.row.add(wt).draw(false) // This is old code for a redundant table that used to display wildtype baseline
        }
    })

   
    //Extract rest of mutants.
    //console.log(mutants)
    mutants.forEach(function(mutant){

        //Check if this element has been simulated in triplicate
        hasreplica = false
        replica_items = replicas.filter(item => item.parentID === mutant['mutantID']);

        if(replica_items.length > 0) { //if so, set to true
            hasreplica = true
            //console.log(replica_items)
            replica_elements[mutant['mutantID']] = replica_items;
            buttonreplica = "<img src='img/checked.png' width='20px' height='20px'>"
        } else {
            buttonreplica = ""
        }


        if(mutant['mutantID'] > 1 && mutant['type'] != "wildtype") {
        
            //If regular mutant
            a = processed.find(o => o.mutantID === mutant['mutantID']);
            
            if(mutant.status === "done"){
                    
                if(typeof(a) != "undefined") {
                    //Manage array or object
                    if(Array.isArray(a.mutations)){
                        mlist = a.mutations[0]
                    } else {
                        mlist = a.mutations
                    }
                    
                    //If it is wildtype replica
                    if(typeof(mlist) == 'undefined'){
                        text = ""
                            Object.keys(residuemap).forEach(chain => {
                                Object.keys(residuemap[chain]).forEach(resid => {
                                    elem = residuemap[chain][resid]
                                    if(elem !== null) {
                                        if(elem.isanchor){
                                            orig = to1[elem.name]
                                            pdbElem = elem.resno_NGL
                                            text += '<div class="badge bg-primary text-white rounded-pill">'+orig+":"+pdbElem+'</div>'
                                        }
                                    }
                                })
                            })
                    } else {
                        //Translate position to PDB 
                        text = ""
                        Object.keys(mlist).forEach(key => {
                            chain   = key.split(":")[0]
                            pos     = key.split(":")[1]
                            mutated = mlist[key]
                            pdbElem = residuemap[chain][pos-1]["resno_NGL"] //Change to PDB  numbering
                            origRes = to1[residuemap[chain][pos-1]["name"]]
                            text += '<div class="badge bg-primary text-white rounded-pill">'+origRes+":"+pdbElem+":"+mutated+'</div>'
                        });
                    }

                    if(a.deltag_total < reference){
                        svg = svgup
                    } else {
                        svg = svgdown
                    }


                    perc = Math.round(a.deltag_total-reference)+svg

                    mt = [a.mutantID, a.cluster, mutant.combination, text, Math.round(a.deltag_total * 10)/10, perc,buttonreplica]
                    dataTable2.row.add(mt)

                    //Store maximum perdicted gain
                    gain = Math.round(a.deltag_total-reference)
                    if (gain < maxgain){
                        maxgain = gain
                        percentgain = Math.round((gain/a.deltag_total)*100, 1)
                    }
                } else {
                    //THIS CONDITION SHOULD NEVER HAPPEN UNLESS THERE IS NO INFO OF THIS
                    //MUTANT IN THE processed_data TABLE. The likely cause for this
                    //is that the Scavenger tried to convert the HDF5 trajectory to
                    //a NC trajectory, to start the scavenging, and it failed to do so.

                    //I designed this chunk of code to cope with it, and to show available info
                    //on the table, but there will be no delta g or gain colums.. so they'll be 0.

                    //I suggest to manually re-queue the entire process of whatever mutant gets here.

                    //console.log(mutant)
                    //Manage array or object
                    if(Array.isArray(mutant.mutant)){
                        mlist = mutant.mutant[0]
                    } else {
                        mlist = mutant.mutant
                    }
                    text = ""
                    Object.keys(mlist).forEach(key => {
                        chain   = key.split(":")[0]
                        pos     = key.split(":")[1]
                        mutated = mlist[key]
                        pdbElem = residuemap[chain][pos-1]["resno_NGL"] //Change to resno_PDB to use PDB numbering instead of amber
                        origRes = to1[residuemap[chain][pos-1]["name"]]
                        text += '<div class="badge bg-primary text-white rounded-pill">'+origRes+":"+pdbElem+":"+mutated+'</div>'
                    });
                    //container = '<div class="badge bg-primary text-white rounded-pill">'+text+'</div>'
                    mt = ["",mutant.mutantID, mutant.cluster,mutant.combination,text,"0","0", buttonreplica]
                    dataTable2.row.add(mt)
                }            
            
               

            } // if the status of the mutant is different... then fill table with something different?
            else {
                
            }

        } else {
            //Wildtype mutant into table

            //Extract original wildtype residues from residuemap
            text = ""
            Object.keys(residuemap).forEach(chain => {
                Object.keys(residuemap[chain]).forEach(resid => {
                    elem = residuemap[chain][resid]
                    if(elem !== null) {
                        if(elem.isanchor){
                            orig = to1[elem.name]
                            pdbElem = elem.resno_NGL //Change to PDB to toggle numbering
                            text += '<div class="badge bg-primary text-white rounded-pill">'+orig+":"+pdbElem+'</div>'
                        }
                    }
                })
            })

            a = processed.find(o => o.mutantID === mutant['mutantID']);
            perc = Math.round(a.deltag_total-reference)            

            //Add mutant to table
            mt = [mutant.mutantID, mutant.cluster,mutant.combination,text,Math.round(a.deltag_total * 10)/10 , perc,buttonreplica]
            dataTable2.row.add(mt)
        }

        


        last_row_index = dataTable2.data().length -1;
        if(typeof mutant.tagged !== 'undefined') {
            if(mutant.tagged == "yes"){
                //dataTable2.row(last_row_index).addClass('rowTagged');
            } 
        }         

        totalmutants = totalmutants+1
    })
    //Get minimim and maximum references.. equal at this point
    min = reference
    max = reference


   

    //Get min and max from table, from reference
    dataTable2.rows().every( function ( rowIdx, tableLoop, rowLoop ) {
        var data = this.data();
        delta = data[4]
        //Get min (ebergy closest to 0 or above)
        if(delta >= reference){
            if(delta >= min){ 
                min = delta
            }
        } 
        //Get max (minimum energy value)
        if(delta <= reference){
            if(delta <= max){ 
                max = delta
            }
        }
    });

        //Fix stats for Null std
    for (const k in stats) {
        let v = stats[k];
        if (v && typeof v === 'object' && ('$numberDouble' in v)) v = v.$numberDouble;
        if (typeof v === 'string') v = Number(v.replace(/,/g, ''));
        if (!Number.isFinite(v)) v = 0;
        stats[k] = v;
    }   
    //Fill descriptive statistics table
    $("#series-count").html(totalmutants)
    $("#series-mean").html(parseFloat(stats['mean'].toFixed(1)))
    $("#series-std").html(parseFloat(stats['std'].toFixed(1)))
    $("#series-base").html(parseFloat(reference.toFixed(1)))
    $("#series-best").html(max)
    $("#series-worst").html(min)
    $("#series-gain").html(maxgain)

    $("#series-001").html(parseFloat(stats['0.1%'].toFixed(1)))
    $("#series-01").html(parseFloat(stats['1%'].toFixed(1)))
    $("#series-5").html(parseFloat(stats['5%'].toFixed(1)))
    $("#series-10").html(parseFloat(stats['10%'].toFixed(1)))
    $("#series-20").html(parseFloat(stats['20%'].toFixed(1)))
    $("#series-50").html(parseFloat(stats['50%'].toFixed(1)))
    $("#series-80").html(parseFloat(stats['80%'].toFixed(1)))
    $("#series-90").html(parseFloat(stats['90%'].toFixed(1)))


    //Apply Color to row
    dataTable2.rows().every( function ( rowIdx, tableLoop, rowLoop ) {
        var data = this.data();
        delta = data[4]
        // Red gradient zone
        if(delta >= reference){
            fadepercent = getPercent(delta, reference, min)
            rgb = colorGradient(fadepercent, white, red)
        }

        // Green gradient zone
        if(delta <= reference){
            fadepercent = getPercent(delta, reference, max)
            rgb = colorGradient(fadepercent, white, green)
        }
        //$(this.row(rowIdx)).css('background-color', rgb);
        row    = $(dataTable2.cell(rowIdx,4).node())
        colmut = $(dataTable2.cell(rowIdx,3).node())

        row.css('background-color', rgb)
        row.addClass("fw-bold fs-4")
        colmut.addClass("fs-6 text-start") 
    });

    dataTable2.columns.adjust()
    dataTable2.draw(false)
    

    //populate range numbers
    $('#disabledRange').val(Math.abs(reference))
    $('#disabledRange').attr('min', Math.abs(min))
    $('#disabledRange').attr('max', Math.abs(max))
    $('#disabledRange').attr('data-bs-original-title', "WT ("+reference+")")
    $('#disabledRange').attr('aria-label', "WT ("+reference+")")
    $('#disabledRange').attr('value', Math.abs(reference))
    
    $('#disabledRange').prop('disabled', true);
    
    $('#best').html(max)
    $('#worse').html(min)
      
    $('#disabledRange').tooltip('show');
    $('#best').tooltip('show')
    $('#worse').tooltip('show')


    //Fill Wildtype by default
    getRMSDSingle(1) //Generate RMSD Table
    getENERGYSingle(1) //Generate Energy Table
    getPAIRWISESingle(1) //Get pairwise for Wildtype
    getNGLViewer(1)
    renderAnchorPoints()
    countHbonds(1)
    //Calculate Weblogos of all mutants.
    //getWebLogoSingle()

    //For replicas
    processed_mutants = processed;
   
}


/////////****************************************************************** */
//Control Replicas Subtables
/* Formatting function for row details - modify as you need */
function subtable (id) {
    tablereplica =  '<table id="datatableReplicas" width="100%" class="text-center table display compact table-sm">';
    tablereplica += '<thead><th>ID</th> <th>Cluster</th> <th>Parent</th> <th>Status</th> <th>ΔG </th> </thead> <tbody>';
                        
    corresponding = replica_elements[id]
    console.log(id)
    console.log(corresponding)
    corresponding.forEach(function(rep){
        console.log(rep)
        if(rep.status === "done"){
            re   = processed_mutants.find(p => p.mutantID === rep.mutantID)
            tablereplica += '<tr>'+
                '<td>'+re.mutantID+'</td>'+
                '<td>'+re.cluster+'</td>'+
                '<td>mutant '+id+'</td>'+
                '<td>' +re.status+'</td>'+
                '<td>' +Math.round(re.deltag_total*10)/10+'</td>'+
                
            '</tr>';
        } else{

            tablereplica += '<tr>'+
                '<td>'+rep.mutantID+'</td>'+
                '<td>'+rep.cluster+'</td>'+
                '<td>mutant '+id+'</td>'+
                '<td>' +rep.status+'</td>'+
                '<td> pending</td>'+
            '</tr>';
        }
        //$(node).addClass('lightBlue')
    })

    tablereplica += '</tbody></table>';
    $('#replicaBackdrop').modal('toggle')
    $('#replicaBackdropLabel').html("Confirmation replicas - Mutant #"+id)
    $('#replica-tablediv').html(tablereplica)
    

    dataTable4 = new DataTable("#datatableReplicas", {sortable: false, scrollCollapse: false, select: {style: 'os'}, paging: false,  bFilter: false, bInfo: false})
    
    //Handle Double click on Mutant table
    $('#datatableReplicas').on('dblclick','tr',function(e){
        let rowID = dataTable4.row(this).data()[0]
        dataTable4.rows(this).select()
        loadMutantDetail(rowID) //Fills Right panel with single mutant info
    })
    dataTable4.draw(false)


}


/////////****************************************************************** */



function calculateMutantWebLogos(component, weblogo){
    
    positions = weblogo.weblogo;
    CAP_PPM = [];
    Object.keys(positions).forEach(key => {
        labelx = key //Figure out the PDB converted position and WT amino from residuemap
        list = []
        weblogo_res.forEach(function(pos){
           //console.log(pos)
            if(!(pos in positions[key])){
                value = 0
            } else {
                value = positions[key][pos]
            }
            list.push(value)
        })
        CAP_PPM.push(list)
    })
    
    //console.log(CAP_PPM)
    props = {
        values: CAP_PPM,
        alphabet: logojs.ProteinAlphabet
    }

    logojs.embedProteinLogo(document.getElementById("weblogoGood_chart"), { ppm: CAP_PPM });
    //logojs.embedRawLogo(document.getElementById("weblogoGood_chart"), props);
    
}

//MUTANT DETAIL (SINGLE MUTANT)
function loadMultiMutantDetail(mutantIDS){
    //Call API to create info for many mutants

}

//REMOVE Label in all charts
function removeMutantFromSpace(mutantID){ ////////////////////////////////////////////////////////////////PENDING TO IMPLEMENT WITH BUTTONS PER ANCHOR SELECTED
    targetLabel = "Mutant "+mutantID
    
    rmsd_chart.data.datasets = chart.data.datasets.filter(function(obj) {
        return (obj.label != targetLabel); 
    });

    energy_chart.data.datasets = chart.data.datasets.filter(function(obj) {
        return (obj.label != targetLabel); 
    });

    // Repaint
    rmsd_chart.update();
    energy_chart.update();
}

//PAINT RMSD GRAPH
function paintRMSD_single(component, dataRMSD){

    
    rmsd = dataRMSD.rmsd
    mutantID = dataRMSD.mutantID
    ctx_rmsd = document.getElementById(component);


    //Extract Data from array
    data2 = []
    for(let i=0; i <= rmsd.length; i++){
        data2.push({
            x: i+1,
            y: rmsd[i]
        })
    }


    
    //Get overall means
    maxx = rmsd.length
    mean = average(rmsd)
    maxy = Math.max(rmsd)+0.2
    miny = mean-0.2

    //Manage opacity

    if (rmsd_chart !== undefined){
    //Update Data
        //color = getRandomColor()
        color = getRandomColor2(mutantColors.length) //gets next color of palette in hex
        color = hexToRgbA(color,0.8) //Same color with opacity
        color = rgba2hex(color)
        newdata =  {
            label: 'Mutant '+mutantID,
            data: data2,
            fill: false,
            borderColor: color,
            backgroundColor: color,
            showLine: true,
            pointStyle: 'line',
            borderWidth: 1,
            pointRadius: 0
        }   
        mutantColors.push({
            mutantID: mutantID,
            color: color
        })

        rmsd_chart.data.datasets.push(newdata)
        rmsd_chart.update()
    } else {
    //Plot the RMSD Graph
     
     mutantColors.push({
        mutantID: mutantID,
        color: rgba2hex(hexToRgbA(getRandomColor2(mutantColors.length),0.9)) //gets next color of palette in hex//rgba2hex("rgba(204, 204, 204, 0.9)")
     })

     //Animation Object
    const totalDuration = 500;
    const delayBetweenPoints = totalDuration / data2.length;
    const previousY = (ctx) => ctx.index === 0 ? ctx.chart.scales.y.getPixelForValue(100) : ctx.chart.getDatasetMeta(ctx.datasetIndex).data[ctx.index - 1].getProps(['y'], true).y;
    animation = {
        x: {
          type: 'number',
          easing: 'linear',
          duration: delayBetweenPoints,
          from: NaN, // the point is initially skipped
          delay(ctx) {
            if (ctx.type !== 'data' || ctx.xStarted) {
              return 0;
            }
            ctx.xStarted = true;
            return ctx.index * delayBetweenPoints;
          }
        },
        y: {
          type: 'number',
          easing: 'linear',
          duration: delayBetweenPoints,
          from: previousY,
          delay(ctx) {
            if (ctx.type !== 'data' || ctx.yStarted) {
              return 0;
            }
            ctx.yStarted = true;
            return ctx.index * delayBetweenPoints;
          }
        }
      };



     //Render Chart
     rmsd_chart = new Chart(ctx_rmsd, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Wildtype',
                data: data2,
                fill: false,
                borderColor: rgba2hex('rgba(204, 204, 204, 0.9)'),
                backgroundColor: rgba2hex('rgba(204, 204, 204, 0.9)'),
                showLine: true,
                pointStyle: 'line',
                borderWidth: 1,
                pointRadius: 0,
            }]
        },
        options: {
            animation,
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    onClick: function (e, legendItem, legend) {
                        var text = legendItem.text;
                        Object.keys(charts).forEach(function (id) {
                            var ci = charts[id]
                            ci.legend.legendItems.forEach(function (item) {             
                              if (item.text == text) {
                                if (ci.data.datasets[item.datasetIndex].hidden == true) {
                                    ci.data.datasets[item.datasetIndex].hidden = false;
                                } else {
                                    ci.data.datasets[item.datasetIndex].hidden = true;
                                }  
                              }
                            });
                            ci.update();
                        });
                        setTimeout(() => resetZoom_pairwise(), 2000);
                    }
                }, 
                zoom: {
                    animation: {
                        duration: 1000,
                        easing: 'easeOutCubic'
                    },
                    pan: {
                        enabled: true,
                        mode: 'xy'
                    },
                    zoom: {
                      wheel: {
                        enabled: true,
                      },
                      pinch: {
                        enabled: true,
                      },
                      mode: 'xy',
                    }
                }
            },  
            
            scales: {
                x: {
                    type: 'linear',
                    beginAtZero: true,
                    max: maxx,
                    min: 0,
                    title: { 
                        text: 'MD Frame Number',
                        display: true
                    }
                },
                y: {
                    display: true,
                    beginAtZero: true,
                    max: maxy,
                    min: miny,
                    title: {
                        text: 'Distance to Frame 1 (Angstroms)',
                        display: true
                    }
                }
            }
        }
    })
    charts.push(rmsd_chart)
    }
}


//Order DIVS inside seqcompare
function reOrderSeqs(order){
    currentOrder = order.value
    paintSequenceExplorer(0,0,true) 
    executeOrder()
}

function executeOrder(){
    switch(currentOrder){
        case "mutantID":
            paintSequenceExplorer(0,0,true) 
        break;

        case "energyASC":
            $('#sequenceHolder').each(function(){
                var $this = $(this);
                $this.append($this.find('.sortable').get().sort(function(a, b) {
                    return $(a).data('index') - $(b).data('index');
                }));
            });
        break;

        case "energyDESC":
            $('#sequenceHolder').each(function(){
                var $this = $(this);
                $this.append($this.find('.sortable').get().sort(function(a, b) {
                    return $(b).data('index') - $(a).data('index');
                }));
            });
        break;
    }
}

function setSegment(e){
    selectSegment = e.value
    paintSequenceExplorer(0,0,true) //Just repaint and set/show a different SelectSegment
    executeOrder()
}

//Changes how we color the sequence explorer
function changeSeqCompare(e){
    seqMethod = e.value
    paintSequenceExplorer(0,0,true) //Just repaint and order
    executeOrder()
}

//Uses Energy values from the database to build the sequenceviewer
function paintSequenceExplorer(component, dataEnergy, justRepaint = false){
    
    if(!justRepaint){
        mutantID = dataEnergy.mutantID // See dyme_api.py MongoDB query at /getMutantEnergy
        energy   = dataEnergy.energy
        combination = energy.combination   
    
        seqvalues[mutantID] = []
        seqvalues[mutantID]["R"] = []
        seqvalues[mutantID]["L"] = []


        Object.entries(energy["LOC"]).forEach(function(res, index){
            num = String(String(res).split(/\s+/)[0]).split(",")[1]
            threletter = String(res).split(/\s+/)[1]
            amino1 = to1[String(res).split(/\s+/)[1]]
            resnum = String(res).split(",")[0]
            relindex = String(res).split(/\s+/)[2]
            posreal = parseInt(relindex,10)
            posindex = parseInt(resnum,10)
            ener    = parseFloat(energy["TOT_AVG_PR"][resnum]);
            ener_std = parseFloat(energy["TOT_STD_PR"][resnum]);
            if(mutantID == 1){
                origsequence.push(amino1) //This exists empty from the initial script declaration
                mutated = 0;
            } else {
                //console.log(origsequence[posindex-1] + " is the same as " +amino1)
                
                if(origsequence[posindex-1] != amino1){
                    mutated = 1;
                } else {
                    mutated = 0
                }
            }
            seqvalues[mutantID][num].push({mutantID: mutantID, number: resnum, residue: amino1, energy: ener, mutated: mutated, type: combination, posreal: posreal, std: ener_std, three: threletter})
        //} else {
        //    amino1 = to1[String(res).split(/\s+/)[1]]
        //    resnum = String(res).split(",")[0]
        //    relindex = String(res).split(/\s+/)[2]
        //    posreal = parseInt(relindex,10)
        //    ener   = parseFloat(energy["TOT_AVG_PR"][resnum]);
        //    ener_std = parseFloat(energy["TOT_STD_PR"][resnum]);
        //    seqvalues[mutantID]["R"].push({mutantID: mutantID, number: resnum, residue: amino1, energy: ener, mutated: 0, type: combination, posreal: posreal, std: ener_std})
       // }
    })
    } else {

    } 
    //console.log(seqvalues)
    //Wipe content
    $("#sequenceHolder").html("")
    $("#sequenceHolder").swipeableMultiselect({
        values: seqvalues, segment: selectSegment
    }); //basic usage


    
}


//PAINT ENERGY GRAPH
function paintENERGY_single(component, dataEnergy){
   
    //energy = dataRMSD.rmsd
    mutantID = dataEnergy.mutantID
    energy   = dataEnergy.energy
    

    //get anchorpoints
    //if (rmsd_chart !== undefined){

    //Build Labels for graph (once)
    data = []
    datasets = []
   
        labels = []
        Object.entries(residuemap).forEach(function(res){
            res[1].forEach(function(chain){
                if(chain !== null){
                    if(chain["isanchor"]){
                        num = chain["resno_PDB"]
                        resid = chain["resno_NGL"]
                        origresname = to1[chain["name"]]
                        
                        if(displayNGLinsteadOfPDB){
                            displaynum = resid
                        } else {
                            displaynum = num
                        }

                        resname = energy["LOC"][resid].split(" ")[1]                       
                        resname = to1[resname]

                        labels.push(origresname+displaynum)

                        //Get Values for mutant
                        avg_delta = energy["TOT_AVG_PR"][resid]
                        std_delta = energy["TOT_STD_PR"][resid]
                        err_delta = energy["TOT_ERR_PR"][resid]
                        
                        data.push({
                            label: resname,
                            x: num,
                            y: 1*avg_delta, 
                            yMin: (1*avg_delta)-(1*err_delta),
                            yMax: (1*avg_delta)+(1*err_delta),
                            yErr: 1*err_delta
                        
                        })
                    }
                }
            })
        })
    

    //For each mutated position, get real PDB index and its data
    /*
    Object.entries(energy["mutations"]).forEach(function(mut){
        chain = mut[0].split(":")[0]
        resid = mut[0].split(":")[1]
        map   = residuemap[chain][resid-1]
        
        //Position and Original
        pdbElem = map["resno_PDB"]
        origRes = to1[map["name"]]
        mutaRes = mut[1]
        console.log(origRes+pdbElem+mutaRes)

        //Get Values for mutant
        avg_delta = energy["TOT_AVG_PR"][resid]
        std_delta = energy["TOT_STD_PR"][resid]
        err_delta = energy["TOT_ERR_PR"][resid]

        data.push({
            label: pdbElem,
            x: pdbElem,
            y: 1*avg_delta, 
            yMin: (1*avg_delta)-(1*err_delta),
            yMax: (1*avg_delta)+(1*err_delta),
           
        })
    })
    */

    var color = mutantColors.find(obj => {
        return obj.mutantID === mutantID
    })
    if(mutantID != 1){
        lab = "Mutant "+mutantID
    } else{
        lab = "Wildtype"
    }
    datasetadd = {
        label: lab,
        borderColor: color.color,
        backgroundColor: color.color,
        data: data,
        datalabels: {
            align: 'end',
        }
    }

    if(energy_chart === undefined){
        //Create new chart
        ctx_energy = document.getElementById(component);  
    
        energy_chart = new Chart(ctx_energy, {
            type: 'barWithErrorBars',
            plugins: [ChartDataLabels],
            data: {
                datasets: [datasetadd]
            },
            options: {
                plugins: {
                    legend: {
                        position: 'bottom',
                        onClick: function (e, legendItem, legend) {
                            var text = legendItem.text;
                            Object.keys(charts).forEach(function (id) {
                                var ci = charts[id]
                                ci.legend.legendItems.forEach(function (item) {             
                                  if (item.text == text) {
                                    if (ci.data.datasets[item.datasetIndex].hidden == true) {
                                        ci.data.datasets[item.datasetIndex].hidden = false;
                                    } else {
                                        ci.data.datasets[item.datasetIndex].hidden = true;
                                    }  
                                  }
                                });
                                ci.update();
                            });
                            setTimeout(() => resetZoom_pairwise(), 2000);
                        }
                    }, 
                    datalabels: {
                        color: 'red',
                        align: "center",
                        anchor: "end",
                        padding: 10,

                    },
                    zoom: {
                        animation: {
                            duration: 1000,
                            easing: 'easeOutCubic'
                        },
                        pan: {
                            enabled: true,
                            mode: 'xy'
                        },
                        zoom: {
                          wheel: {
                            enabled: true,
                          },
                          pinch: {
                            enabled: true,
                          },
                          mode: 'xy',
                        }
                    },
                    tooltip: {
                        bodyFont: {
                            size: 14 // Increase font size (default is usually 12, so +2 points)
                        },
                        titleFont: {
                            size: 14
                        },
                        callbacks: {
                            label: function (context) {
                                let value = context.raw.y.toFixed(2); // Rounds to 2 decimal places
                                //let min = context.raw.yMin.toFixed(1); // Rounds min value
                                //let max = context.raw.yMax.toFixed(1); // Rounds max value
                                let err = context.raw.yErr.toFixed(2); // Rounds max value 
                                //return `ΔG ${value} kcal/mol (Min: ${min}, Max: ${max}`;
                                return `ΔG: ${value} (±${err}) kcal/mol`;
                            }
                        }
                    }
                },
                responsive: true, 
                legend: {
                        display: true, 
                },
                elements: {
                    pointRadius: 10,
                    pointHoverRadius: 10,
                    pointStyle: 'star'
                },       
                scales: {
                    x: {
                        type: 'category',
                        labels: labels,
                        beginAtZero: false,
                        title: { 
                            text: 'Anchor point Position',
                            display: true
                        }
                    },
                    y: {
                        display: true,
                        beginAtZero: false,
                        reverse: true,
                        title: {
                            text: 'ΔG (kcal/mol)',
                            display: true
                        }
                    }
                }
            }
        })
        charts.push(energy_chart)
    } else {
        //Add new data to existing chart
        energy_chart.data.datasets.push(datasetadd)
        energy_chart.update()
    }



}

//Toggle Residue IDs to NGL instead of PDB numbering
function toggleNumbering(){
    labels = []

    if(displayNGLinsteadOfPDB){
        displayNGLinsteadOfPDB = false
    } else {
        displayNGLinsteadOfPDB = true
    }

    Object.entries(residuemap).forEach(function(res){
        res[1].forEach(function(chain){
            if(chain !== null){
                if(chain["isanchor"]){
                    num = chain["resno_PDB"]
                    resid = chain["resno_NGL"]
                    origresname = to1[chain["name"]]
                    
                    if(displayNGLinsteadOfPDB){
                        displaynum = resid                        
                    } else {
                        displaynum = num
                    }

                    resname = energy["LOC"][resid].split(" ")[1]                       
                    resname = to1[resname]

                    labels.push(origresname+displaynum)

                    
                }
            }
        })
    })
    energy_chart.options.scales.x.labels = labels
    pairwise_chart.options.scales.y.display = !displayNGLinsteadOfPDB
    pairwise_chart.options.scales.y2.display = displayNGLinsteadOfPDB
    energy_chart.update()
    pairwise_chart.update();
   
}





//PAINT ENERGY MAP CHART MATRIX
function paintENERGY_matrix(component, dataEnergy){

    ctx_contact = document.getElementById(component); //Pairwise_chart
    
    heatmap_chart = new Chart(ctx_contact, {
        type: 'matrix', 
        data: {
            datasets: [{
                label: 'My Matrix',
                data: [
                    {x: '1', y: '275', v: 11},
                    {x: '1', y: '312', v: 12},
                    {x: '1', y: '317', v: 13},
                    {x: '1', y: '318', v: 21},
                    {x: '1', y: '319', v: 22},
                    {x: '1', y: '320', v: 23},
                ],
                backgroundColor(context) {
                    const value = context.dataset.data[context.dataIndex].v;
                    const alpha = (value - 5) / 40;
                    return Chart.helpers.color('green').alpha(alpha).rgbString();
                },
                width(context) {
                    const a = context.chart.chartArea;
                    if (!a) {
                        return 0;
                    }
                    return (a.right - a.left) / 3 - 2;
                },
                height(context) {
                    const a = context.chart.chartArea;
                    if (!a) {
                        return 0;
                    }
                    return (a.bottom - a.top) / 3 - 2;
                }
            }]
        },
        options: {
            legend: {
                display: false
            },
            tooltips: {
                callbacks: {
                    title() {
                        return '';
                    },
                    label(context) {
                        const v = context.dataset.data[context.dataIndex];
                        return ['x: ' + v.x, 'y: ' + v.y, 'v: ' + v.v];
                    }
                }
            },
            scales: {
                x: {
                    type: 'category',
                    labels: ['A', 'B', 'C'],
                    ticks: {
                        display: true
                    },
                    gridLines: {
                        display: false
                    }
                },
                y: {
                    type: 'category',
                    labels: ['X', 'Y', 'Z'],
                    offset: true,
                    reverse: false,
                    ticks: {
                        display: true
                    },
                    gridLines: {
                        display: false
                    }
                }
            }
        }
    });
}


function paintENERGY_pairwise(component, dataEnergy){

    ctx_pairwise = document.getElementById(component); //Pairwise_chart
    mutantID = dataEnergy.mutantID
    pairwise = dataEnergy.pairwise

    

    //Loop indexes
    min = Math.min.apply(null, Object.values(pairwise.TOT_PW)) //get min energy
    max = Math.max.apply(null, Object.values(pairwise.TOT_PW)) //get max energy
    const map = (value, x1, y1, x2, y2) => (value - x1) * (y2 - x2) / (y1 - x1) + x2; //map to percent

    //Labels and data   
    dots = []
    //let labelxnum = {}
    labelx = [] //X label
    labely = [] //Standard Y axis, with converted map
    labely2 = [] //Second Y axis for showing original residues
    resmap  = {}
    resmap2 = {} //Only to store y2 names and labels
    resmap3 = {}
    mutablechain = ""
     //initialize

    //Get residuemap from anchorpoint object
    Object.entries(residuemap).forEach(function(res){
        res[1].forEach(function(chain){
            if(chain !== null){
                num = chain["resno_PDB"]
                resid = chain["resno_NGL"]
                cha1 = chain["chain"]
                origresname = to1[chain["name"]]
                resmap[resid] = origresname+num
                resmap2[resid] = origresname+resid
                resmap3[resid] = cha1+":"+resid //This one holds the index of the chain:amino, as stored in the mutant. It paints the mutation to show in the tooltip
                if(chain["isanchor"]){
                    mutablechain = cha1 //get the mutable chain.. no need to modify this in the api
                }
            } 
        })
    })
    //Loop again to get the list
    residuesinxaxix = []
    Object.entries(residuemap).forEach(function(res){
        res[1].forEach(function(chain){
            if(chain !== null){
                if(chain["chain"] == mutablechain){
                    num = chain["resno_PDB"]
                    origresname = to1[chain["name"]]
                    residuesinxaxix.push(origresname+num) //Make a list of residues that are meant to display on X. For some reason MMGBSA pairwise sometimes comes with pairs in the same chain??.. which is odd
                } 
            }
        })
    })

    receptorresidues = []
    //The color of the entering mutant
    var color = mutantColors.find(obj => {
        return obj.mutantID === mutantID
    })

    //x_2 = 0 // This loops MMPBSA data to build the heatmap dots
    for (const key in pairwise.RES1) {
        x1 = pairwise.RES2[key] //Residue for this key
        y1 = pairwise.RES1[key] //Residue for this key
        v1 = pairwise.TOT_PW[key] //actual energy value from MMPBSA in database for this position
        muts = pairwise.mutations 
        //Relevant Energy Threshold.. anything below 0.5 kcal is a weak vdb contact...
        if(v1 < -0.51 && !residuesinxaxix.includes(resmap[x1])){ // Make sure we don't display an anchorpoint on X label
                //console.log(resmap[x1])
                v1 = map(v1,-0.4, min,5,100) //Calculate alpha transparency for this coords
                receptorresidues.push(x1) 
                if (!labelx.includes(resmap[x1])) {
                    labelx.push(resmap[x1]);
                    //labelxnum[resmap[x1]] = x_2+pairwise_offset
                    //x_2 = x_2+1
                }
                
                if (!labely.includes(resmap[y1])) {
                    labely.push(resmap[y1]);
                    labely2.push(resmap2[y1]); //Fill alternate Y axis (with PDB)

                }
                y2label = resmap3[y1] //Label of a mutation in this dot, if it exists
                //Add datapoint
                dots.push(
                    {x: resmap[x1], y: resmap[y1], v: v1, en: pairwise.TOT_PW[key], mutations: muts, y2: y2label} //Add a datapoint to the heatmap
                )

                //Store the max contact energy being displayed for threshold comparison
                if(pairwise.TOT_PW[key] < maxenergyofseries ){
                    maxenergyofseries = pairwise.TOT_PW[key];
                }
        }
       
    }  
    //console.log(dots)
    //console.log(labelx)
    //console.log(labely)
    //console.log(labely2)
    //pairwise_offset += 0.05;
    //dots.sort((a, b) => parseInt(a.x.slice(1)) - parseInt(b.x.slice(1)));
    dots.sort((a, b) => parseInt((a.x || "").slice(1)) - parseInt((b.x || "").slice(1)));
    labelx.sort((a, b) => parseInt((a.x || "").slice(1)) - parseInt((b.x || "").slice(1)));
    labely.sort((a, b) => parseInt((a.x || "").slice(1)) - parseInt((b.x || "").slice(1)));
    labely2.sort((a, b) => parseInt((a.x || "").slice(1)) - parseInt((b.x || "").slice(1)));

   // console.log(labely)
    
    if(mutantID != 1){
        lab = "Mutant "+mutantID
    } else{
        lab = "Wildtype"
    }

    datasetadd = {
        label: lab,
        borderColor: color.color,
        backgroundColor: color.color,
        data: dots,
        datalabels: {
            align: 'end',
        },
        width: 20,
        height: 20,
        //xAxisID: 'x2'

        backgroundColor: function(ctx) {
            const threshold = thresholdMap;
            const alphaMin = 0.1;
            const alphaMax = 1.0;

            const value = ctx.raw.en*-1;  // <- per-dot value
            const maxVal = maxenergyofseries*-1;        // <- global max (must be accessible)

            // Convert hex (#RRGGBB) to RGB
            const hex = color.color.replace('#', '');
            const r = parseInt(hex.substring(0, 2), 16);
            const g = parseInt(hex.substring(2, 4), 16);
            const b = parseInt(hex.substring(4, 6), 16);

            // Compute alpha
            

            let alpha = alphaMax;
            if (value > threshold) {
                alpha = alphaMin + ((value/threshold) / (threshold)) * (alphaMax - alphaMin);
                alpha = Math.max(alphaMin, Math.min(alphaMax, alpha));
            }
            //console.log(value)
            return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        }
    }
    



    if(pairwise_chart === undefined){
        Chart.register(shiftPlugin);
        pairwise_chart = new Chart(ctx_pairwise, {
            type: 'matrix', 
            data: {
                datasets: [
                    datasetadd
                ]
            },
            options: {
                plugins: {
                    legend: {
                        position: 'bottom',
                        onClick: function (e, legendItem, legend) {
                            var text = legendItem.text;
                            Object.keys(charts).forEach(function (id) {
                                var ci = charts[id]
                                ci.legend.legendItems.forEach(function (item) {             
                                  if (item.text == text) {
                                    if (ci.data.datasets[item.datasetIndex].hidden == true) {
                                        ci.data.datasets[item.datasetIndex].hidden = false;
                                    } else {
                                        ci.data.datasets[item.datasetIndex].hidden = true;
                                    }  
                                  }
                                });
                                ci.update();
                            });
                            setTimeout(() => resetZoom_pairwise(), 2000);
                        },
                    },
                    zoom: {
                        animation: {
                            duration: 1000,
                            easing: 'easeOutCubic'
                        },
                        pan: {
                            enabled: true,
                            mode: 'xy'
                        },
                        zoom: {
                          wheel: {
                            enabled: true,
                          },
                          pinch: {
                            enabled: true,
                          },
                          mode: 'xy',
                        }
                    },
                    tooltip: {
                        bodyFont: {
                            size: 14 // Increase font size (default is usually 12, so +2 points)
                        },
                        titleFont: {
                            size: 14
                        },
                        callbacks: {
                            title: function(context) {
                                
                                
                                if(!displayNGLinsteadOfPDB){ //PEDRO: 2025 - Fix showing the toggled yAxis on the heatmap plugin
                                    anchorshow = context[0].formattedValue //Show initial
                                } else {
                                    const index = pairwise_chart.options.scales.y.labels.indexOf(context[0].formattedValue);
                                    anchorshow = pairwise_chart.options.scales.y2.labels[index] // Show mapped
                                }
                                if(context[0].raw.mutations[context[0].raw.y2] !== undefined){ //2025 - PEDRO - SHOW MUTATION IF IT EXISTS ON THE TOOLTIP
                                    anchorshow  = anchorshow+context[0].raw.mutations[context[0].raw.y2]
                                } 

                                //let title = "ΔG from "+context[0].formattedValue+" to "+context[0].label
                                let title = "Pairwise ΔG from "+anchorshow+" to "+context[0].label
                                //console.log(context)
                                return title;
                            },
                            label: function(context) {
                                
                                let label = context.dataset.label || '';
        
                                if (label) {
                                    label += ': '; //TODO - ADD point mutation to this position of the mutant
                                }
                                if (context.raw.en !== null) {
                                    label += new Intl.NumberFormat('en-US', { style: 'decimal', value: '.'}).format(context.raw.en)+" kcal/mol";
                                }
                                return label;
                            }
                        }
                    },
                    shiftPlugin: true
                }, 
                legend: {
                    display: true,
                    
                },
                tooltips: {
                    callbacks: {
                        title() {
                            return '';
                        },
                        label(context) {
                            const v = context.dataset.data[context.dataIndex];
                            return ['x: ' + v.x, 'y: ' + v.y, 'v: ' + v.v];
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'category',
                        labels: labelx,
                        beginAtZero: false,
                        ticks: {
                            display: true,
                            autoSkip: true,
                            maxTicksLimit: 50,
                            autoSkipPadding: 5
                        },
                        gridLines: {
                            display: false
                        },
                        title: { 
                            text: 'Counterpart Residue',
                            display: true
                        }
                    },  
                    //,
                    //x2: {
                    //    type: 'linear',
                    //   display: false,
                    //    position: 'bottom',  // Align with x-axis
                    //    display: true,      // Keep it invisible
                    //    min: 0,
                    //    max: labelx.length - 1,  // Ensure the max matches the number of labels
                    //    ticks: {
                    //        stepSize: 1,      // Ensure alignment with categorical scale
                    //    }
                    //},
                    y: {
                        type: 'category',
                        labels: labely,
                        offset: true,
                        reverse: true,
                        title: { 
                            text: 'Anchor point',
                            display: true
                        },
                        ticks: {
                            display: true,
                            autoSkipPadding: 5
                        },
                        gridLines: {
                            display: false
                        }
                    },
                    y2: { //Additional label for showing original PDB numbering, instead of map
                        type: 'category',
                        labels: labely2,  // Second label set
                        offset: true,
                        reverse: true,
                        display: false,  // Start hidden
                        title: { 
                            text: 'Anchor point',
                            display: true
                        },
                        ticks: {
                            display: true,
                            autoSkipPadding: 5
                        },
                        gridLines: {
                            display: false
                        }
                    }
                }
            }
        });
        charts.push(pairwise_chart)
        
    } else {
       //Add new data to existing chart
       pairwise_chart.data.datasets.push(datasetadd)
       updateXLabels(pairwise_chart, labelx)
       updateYLabels(pairwise_chart, labely)
       updateY2Labels(pairwise_chart, labely2)
       pairwise_chart.update();
       setTimeout(() => resetZoom_pairwise(), 1500);

      
    }
}

function updateXLabels(chart, raw) {
  const existing = chart.options.scales.x.labels ?? [];
  const incoming = raw;
  const merged   = sortResidueLabels([...existing, ...incoming]);
  chart.options.scales.x.labels = merged;               // <-- lock order here
  chart.options.scales.x.type = 'category'; // for clarity
}

function updateYLabels(chart, raw) {
  const existing = chart.options.scales.y.labels ?? [];
  const incoming = raw;
  const merged   = sortResidueLabels([...existing, ...incoming]);
  chart.options.scales.y.labels = merged;               // <-- lock order here
  chart.options.scales.y.type = 'category'; // for clarity
}

function updateY2Labels(chart, raw) {
  const existing = chart.options.scales.y2.labels ?? [];
  const incoming = raw;
  const merged   = sortResidueLabels([...existing, ...incoming]);
  chart.options.scales.y2.labels = merged;               // <-- lock order here
  chart.options.scales.y2.type = 'category'; // for clarity
}

function resetZoom_pairwise(){
    console.log('rezising')
    pairwise_chart.resetZoom(mode = 'none')
}


//Renders anchorpoint buttons below NGL canvas
function renderAnchorPoints(){
    var btn = ''
    Object.entries(residuemap).forEach(function(res){
        res[1].forEach(function(chain){
            if(chain !== null){
                if(chain["isanchor"]){
                    num     = chain["resno_PDB"]
                    resid   = chain["resno_NGL"]
                    origresname = to1[chain["name"]]
                    ch   = chain["chain"]
                    btn += '<button class="btn btn-orange btn-sm" onclick="focusOnAnchor(\''+ch+":"+resid+'\')">'+origresname+num+'</button> '
                }
            }
        })
    })   
    btn += "<br><span class='small text-muted'>(Click on Anchor point to Focus) </span>"
    $("#anchorpointlist").html(btn)
}


function focusOnAnchor(label, { componentIndex = 0, duration = 1000 } = {}) {
  const comp = molStructure.compList[componentIndex];
  if (!comp) return;

  // Parse "A:620" or "620" (default chain A)
  const m = String(label).trim().match(/^([A-Za-z])?:?(\d+)$/);
  if (!m) return;

  const chain = (m[1] || 'A').toUpperCase();
  const resno = +m[2];
  const sel = `:${chain} and ${resno}`;

  // Get StructureView
  comp.autoView(sel, 1500);  // adjust zoom factor if needed
}


//Add button for a mutant in 3D Explorer
function addMutantButtons(mutantID){  
        //buttons    = '<button onclick="launchOnVMD('+mutantID+')" id="mutant_'+mutantID+'" class="btn btn-sm btn-outline-dark w-30">Open</button>'
        var color = mutantColors.find(obj => {
            return obj.mutantID === mutantID
        })
        buttons    = `<div>
                <button onclick="launchOnVMD(${mutantID})" id="mutant_${mutantID}" class="btn btn-outline-dark btn-icon"><i data-feather="download-cloud"></i></button>
                <button onclick="toggleStruct(this, ${mutantID})" id="mutant_${mutantID}_struc" class="btn  btn-green btn-icon">STR</button>
                <button onclick="toggleWater(this, ${mutantID})" id="mutant_${mutantID}_water" class="btn  btn-blue btn-icon">WAT</button>
                <div class='minibox' style='background-color: ${color.color}'></div> ${mutantID}
            </div>`;
        
        $('#mutantbuttonsNGL').append(buttons)
        feather.replace()
}


//Toggle Structure On or Off in 3D viewer
function toggleStruct(button, id){
    var currentVisibility = groupsNGL[id].molecule.visible;
    groupsNGL[id].molecule.setVisibility(!currentVisibility);
    if(!currentVisibility){
        jQuery(button).addClass("btn-green")
        jQuery(button).removeClass("btn-outline-green")
    } else {
        jQuery(button).removeClass("btn-green")
        jQuery(button).addClass("btn-outline-green")
    }
}

//Turns water on and off at 3D Viewer
function toggleWater(button, id){
    Object.keys(groupsNGL[id].sphereRep).forEach(function(key) {
        var site = groupsNGL[id].sphereRep[key];
        currentVisibility = site.visible;
        groupsNGL[id].sphereRep[key].setVisibility(!currentVisibility)
        if(!currentVisibility){
            jQuery(button).addClass("btn-blue")
            jQuery(button).removeClass("btn-outline-blue")
        } else {
            jQuery(button).removeClass("btn-blue")
            jQuery(button).addClass("btn-outline-blue")
        }
    });
}

//Turns contacts on/off
function toggleContacts(button, id){

}


//update Table inside tooltip
function updateWatersTable(id){
    $("#table-waters-body").html("");
    
    if(Object.keys(waterdisplay).length > 0) {
      
        //Contiene mutantes con agua
        Object.entries(waterdisplay).forEach(([mutantID, residues]) => {
          if(mutantID == id){
            rows = []
            numatoms = residues.length
        
            // Loop through the inner object
            Object.entries(residues).forEach(([name, infowaters]) => {
                if(name != 'sites'){
                    if(infowaters.waters.length > 0){
                    buts = "";
                    watsclases = []
                    infowaters.waters.forEach(function(water, index){
                        //console.log(water)
                        buts += `<button class="btn btn-outline-red btn-icon wat${water}" title="Residence: ${infowaters.residence[index]}%" type="button">${water}</button>`
                        watsclases.push("b"+water)
                    })
                        reside = infowaters.residence.reduce((a, b) => a + b);
                        if(reside > 100) {
                            reside = 100;
                        }
                        rows.push(`
                        <td>${name}</td>
                        <td style="text-align: left;">
                            ${buts}
                        </td>
                        <td>${reside}%</td>`)
                    }
                }
            });

            htmlrow = ""
            rows.forEach(function(row){
                htmlrow += `<tr>${row}</tr>`
            });         
          }
        });
        //Fill waters table with info per mutant
    }   
    $("#table-waters-body").html(htmlrow);
    //Add hover classes
    

    $('#table-waters-body .btn').on('mouseenter', function () {
        // Get the group class (bXXXX) for the hovered button
        const groupClass = $(this).attr('class').split(' ').find(cls => cls.startsWith('wat'));

        if (groupClass) {
            // Only apply the 'active' class to buttons that share the same group class
            $(`#table-waters-body .${groupClass}`).addClass('active');
        }
    });

    $('#table-waters-body .btn').on('mouseleave', function () {
        // Get the group class (bXXXX) for the hovered button
        const groupClass = $(this).attr('class').split(' ').find(cls => cls.startsWith('wat'));

        if (groupClass) {
            // Remove the 'active' class only from buttons in the same group
            $(`#table-waters-body .${groupClass}`).removeClass('active');
        }
    });

    //Rename title a bit
    if(id == 1){
        nam_mutant = 'Wildtype';
    } else {
        nam_mutant = 'Mutant ID #'+id;
    }
    //Render title
    $("#waterBackdropLabel").html('Water-contacts Summary Panel ('+nam_mutant+')');

    $("#waterBackdrop").modal('show') //Show Water-contact Summary table after refactoring
}


function updateWatersTableFront(){
    $("#table-waters-body-front").html("");
    console.log(waterdisplay)
    htmlrow = ""
    if(Object.keys(waterdisplay).length > 0) {
        Object.entries(waterdisplay).forEach(([mutantID, residues]) => {
            numatoms = 0
            wats = 0;
            Object.entries(residues).forEach(([name, infowaters]) => {
                if(name != 'sites'){
                    wats   += infowaters['waters'].length
                    numatoms += 1
                } else {
                    sites = infowaters
                }
            })

            mutantColors.forEach(function(mut){
                if(mut.mutantID == mutantID){
                    col = mut.color
                }
            })
            
            htmlrow += `<tr>
                    <td style="text-align: left"><div class='minibox' style='background-color: ${col}'></div> ${mutantID}</td>
                    <td>${sites}</td>
                    <!--<td>${numatoms}</td>-->
                    <td>${wats}</td>
                    <td>
                        <button class="btn btn-danger btn-sm" onclick="updateWatersTable(${mutantID})">View Waters</button>
                    </td>
                </tr>`
        });
        //Fill waters table with info per mutant
        $("#table-waters-body-front").html(htmlrow);
        
    }    

}



//MAIN NGL VIEWER
function loadNGLViewer(canvas, response){
    
    mutantID = response["mutantID"]
    pdbtextf = response["pdbfile"]
    watersites = response["watersites"]
    mutantIDname = "Mutant "+mutantID
    //Create a string blob with the PDB file
    var stringBlob = new Blob( [ pdbtextf ], { type: 'text/plain'} );
    
    //Get Color
    var color = mutantColors.find(obj => {
        return obj.mutantID === mutantID
    })

    //If this is the first object in the canvas, create the stage
    if(stage === undefined){
        stage = new NGL.Stage(canvas.attr("id"));  
        stage.setParameters({ backgroundColor: "white"} )
        stage.setSpin(setspin);
       
    } 

    //Calculate Anchor points
    anchors = []
    allres = []
    
    Object.entries(residuemap).forEach(function(res){
        res[1].forEach(function(chain){
            if(chain !== null){
                allres.push(chain["resno_NGL"])
                if(chain["isanchor"]){
                    num     = chain["resno_PDB"]
                    resid   = chain["resno_NGL"]
                    origresname = to1[chain["name"]]

                    //Anchorpoint list for selector
                    anchors.push(resid)

                    data.push({
                        ngl_pos: resname,
                        pdb_pos: num,
                        label: origresname+num,                        
                    })    
                }
            }
        })
    })
    seleall = allres[0]+"-"+allres[allres.length-1]
    
    //Load PDB info stage
    stage.loadFile( stringBlob, { ext: "pdb" , defaultRepresentation: false, name: mutantIDname} ).then(function(o){
        //molStructure.clearRepresentations();
        //console.log(o.structure.getResidue(13))
        //TEMPORAL HIDE STRUCTURE 3D
        //$("#viewer4loading").remove();
        //setTimeout(function(){ $('#staticBackdrop').modal('hide')}, 100);
        //return
        //REMOVE TILL HERE TO SHOW AGAIN PEDRO

        // Group 1: Molecule 1, its representations, and spheres
        groupsNGL[mutantID] = {};  // Create group 1 at index 0
        groupsNGL[mutantID].molecule = o;  // PDB molecule 1
        groupsNGL[mutantID].sphereRep = [];
        groupsNGL[mutantID].contactsRep = [];
      

        seleres = anchors.join(', ');
        pairres = receptorresidues.join(', ')
        var duration = 1000;

        //////////////////////Add representations for molecule 1 (group 1)////////////////////////////// 
        if(mutantID === 1){
            groupsNGL[mutantID].molecule.addRepresentation("cartoon",  {sele: "all and (not hydrogen)", color: color.color.slice(0, -2), pickable: true, opacity: 0.1});
            groupsNGL[mutantID].molecule.addRepresentation("ball+stick",    {sele: "("+seleres+")"+" and (not hydrogen)", pickable: true});
            //groupsNGL[mutantID].molecule.addRepresentation("contact",    {sele: "("+seleres+")", pickable: true, radius: 0.5, maxDistance: 3.5, piStacking: true, color: "#5579bbff"})   
            groupsNGL[mutantID].molecule.addRepresentation('label', {
                  // pick one anchor atom per residue: CB (or CA for GLY which has n CB)
                  sele: 'protein and (name CA)',
                  labelType: 'text',
                  labelText: ap => `${ap.resname}${ap.resno}${ap.chainname ? ':' + ap.chainname : ''}`,
                  color: 'black',
                  attachment: 'middle-right',  // nudge relative to anchor atom
                  xOffset: 0,
                  yOffset: 0,
                  zOffset: 1.5,                // lift the label off the surface a bit
                  useScreen: true              // keep constant screen size
                  });      
            groupsNGL[mutantID].molecule.autoView(duration, seleres);
        } else {
            groupsNGL[mutantID].molecule.addRepresentation("ribbon",  {sele: "all and (not hydrogen)", color: color.color.slice(0, -2), opacity: 0.5, pickable: true});
            groupsNGL[mutantID].molecule.addRepresentation("ball+stick",    {sele: "("+seleres+")"+" and (not hydrogen)", color: "element", colorValue: color.color.slice(0, -2), pickable: true}) //Pedro change rep Aug 1 2024
        }
        //////////////////////////////////////////////////////////////////////////////

        //////////////////////////////////ADD WATER SITES/////////////////////////////
        var spherePositions1 = []
        
        // Put here for each wetspot add object to spherepositions   
        //console.log(watersites)

        //Check If Dyme found any water sites, and iterate them to build the site
        sites = 0
        
        waterdisplay[mutantID] = {}


        //Decide which waters to show
        //Object.entries(watersites["water_ids"]["anchor_contacts"]).forEach(function([atomid, watersite]){
        //    involved_waters = watersite["waters"]
        //    console.log(watersite["residue"])
        //    involved_waters.forEach(function(watid){
        //        perc = watersites["water_ids"]["important_waters"][watid]["residence_percentage"]
        //        if(perc >=5){
        //          console.log(perc)
        //        }
        //    })
        //})




        if(Object.keys(watersites["water_ids"]["anchor_contacts"]).length > 0) {
            Object.entries(watersites["water_ids"]["anchor_contacts"]).forEach(function([atomid, watersite]){ //atomid is the residue, not the water
                //Vars for the site to display
                
                if(watersite["watersite_centroid"] != undefined){ //If project has centroids calculated (needs new scavengeer)

                    //Limit display options to threshold
                    painted = []
                    if(atomid != undefined){
                        console.log(atomid)
                        accum_residence = 0
                        label1 = ""
                        residue_name = watersite["residue"] //Atom at the residue near water
                        involved_waters = watersite["waters"] //Actual water ids in the site
                        centroid = watersite["watersite_centroid"] //Coordinate to show (centroid of waters at the site)
                        addthisone = false

                        waterdisplay[mutantID][residue_name] = {}
                        waterdisplay[mutantID][residue_name]["waters"] = []
                        waterdisplay[mutantID][residue_name]["residence"] = []
                        waterdisplay[mutantID]['sites'] = 0
                        involved_waters.forEach(function(watid){
                            if(!painted.includes(watid)){
                                watpercent = watersites["water_ids"]["important_waters"][watid]["residence_percentage"] //For labeling
                                watres     = watersites["water_ids"]["important_waters"][watid]["residue"] //For future display
                                watframes  = watersites["water_ids"]["important_waters"][watid]["frames"] //For future display
                                    if(watpercent >= 5 ){ //Only grab waters better than 5% residence
                                accum_residence +=watpercent
                                painted.push(watid)
                                addthisone = true                            
 
                            waterdisplay[mutantID][residue_name]["waters"].push(watid)
                            waterdisplay[mutantID][residue_name]["residence"].push(watersites["water_ids"]["important_waters"][watid]["residence_percentage"])
                                    }
                            } 
                        })
                        
                        if(addthisone && accum_residence > 5){ //Limit residence to 5% (all waters) and upper
                            //console.log(involved_waters)
                            sites +=1                        
                            //console.log(label1+" "+accum_residence)
                            spherePositions1.push({ position: centroid, label: `Site ${sites} (${accum_residence}%)`, resident: accum_residence})
                        }
                        waterdisplay[mutantID]['sites'] = sites     
                        
                    }
                }

                 // Create spheres for group 1
            });
            if(waterdisplay[mutantID]['sites'] > 0){
                updateWatersTableFront()
            }
            

        }
       
        spherePositions1.forEach(function(item) {
            var shape = new NGL.Shape('highlight');
            col = hexToRgbA(color.color.slice(0,-2), 1.0).match(/\d+/g).slice(0, 3).map(num => parseInt(num) / 255)
            shape.addSphere(item.position, col, 2.5*(item.resident/100), "Water "+item.label+" (Mutant "+mutantID+")");
            shape.addText(item.position, [0,0,0], 1, item.label, col);
            var shapecomp = stage.addComponentFromObject(shape);

            var sphereRepresentation = shapecomp.addRepresentation('buffer', {
                opacity: 0.5,
                side: 'double',
                wireframe: false,
                label: "test"
            });
            //console.log(sphereRepresentation)
            groupsNGL[mutantID].sphereRep.push(sphereRepresentation);  // Store sphere representations for group 1
         });            
       
        //VIEW Watersites
        //average_position = [39.705692132314048, 29.12733713785807, 24.961631298065186];
        //var shape = new NGL.Shape('highlight');
        //shape.addSphere(average_position, [1.0, 0.0, 0.0], 1.0, 'average_position'); // Red color
        //var shapeComp = stage.addComponentFromObject(shape)
        
        //shapeComp.addRepresentation('buffer', {
        //        opacity: 0.1,  // 50% transparent
        //        side: 'double',  // Make it visible from all sides
        //        wireframe: false  // Set to true if you prefer an outline
        //});
        //////////////////////////////////////////////////////////////////////////////
           

        //Define Superposing Reference
        if(canvas.attr('id') == "mutantviewer"){
            $("#viewer4loading").remove();
           //Add buttons to handle this mutant
           //console.log("AA");
           setTimeout(function(){ $('#staticBackdrop').modal('hide')}, 100);
        }
        

        function transformCoordinates(spherePositions, matrix) {
            return spherePositions.map(pos => {
                let v = new NGL.Vector3(pos[0], pos[1], pos[2]);  // Convert to NGL vector
                v.applyMatrix4(matrix);  // Apply the transformation matrix
                return [v.x, v.y, v.z];  // Return transformed coordinates
            });
        }
        function addSpheres(spherePositions) {
            var shape = new NGL.Shape('highlight');
        
            spherePositions.forEach(pos => {
                shape.addSphere(pos, [1, 0, 0], 1.0, 'sphere');  // Add red spheres
            });
        
            if (shapeComp) {
                stage.removeComponent(shapeComp);  // Remove previous spheres
            }
        
            shapeComp = stage.addComponentFromObject(shape);
            shapeComp.addRepresentation('buffer', { opacity: 0.5 });
        }

        if(mutantID !== 1){
            groupsNGL[mutantID].molecule.superpose(groupsNGL[1].molecule, false, seleall)
            //let matrix = groupsNGL[mutantID].molecule.matrix.clone();
            //let transformedSpheres = transformCoordinates(spherePositions1, matrix);
            //addSpheres(transformedSpheres);  
        }
       
    })
    box = canvas.width();
    canvas.css({"width:": box+"px", "height": box+"px", "overflow": ""});
    stage.handleResize();
    
    molStructure = stage
}



//Create fake contact using NGL, to display desired cpptraj contacts
function  manualHbond(mutantID, sel1, sel2, name="") {
  // Resolve atom indices
  comp = groupsNGL[mutantID].molecule;
  const idx1 = comp.structure.getAtomIndices(new NGL.Selection(sel1))[0]; //i.e. 620 and .OP1 (this is how the exact atom is reached)
  const idx2 = comp.structure.getAtomIndices(new NGL.Selection(sel2))[0];
  if (idx1 === undefined || idx2 === undefined) return;

  // Get positions
  const a1 = comp.structure.getAtomProxy(); a1.index = idx1;
  const a2 = comp.structure.getAtomProxy(); a2.index = idx2;
  const pos1 = a1.positionToArray();
  const pos2 = a2.positionToArray();

  // Create shape and add cylinder
  const shape = new NGL.Shape("manual-hbond");
  shape.addCylinder(pos1, pos2, [0.6, 0.8, 1.0], 0.15, "Contact "+name);

  // Display in viewer
  
  const shapeComp = stage.addComponentFromObject(shape);
  var contactRepresentation = shapeComp.addRepresentation("buffer");
  groupsNGL[mutantID].contactsRep.push(contactRepresentation);
  
}

//Extract and show contacts: For future use - PEDRO NOV 2025
function drawContacts(mutantID){
    mutantObjects.forEach(function(mutant){
    if(mutant.mutantID == mutantID){
        contacts = mutant[dict_cpptraj_index+contactThreshold]
        Object.keys(contacts).forEach(function(origin){
            res1 = parseInt(origin.replace(/\D/g, ""), 10);
            contacts[origin].forEach(function(destination) {
                destname  = Object.keys(destination)[0]
                console.log(destname)
                destname2 = destname.replace(/\D/g, "") 
                atoms    = destination[destname]
                res2     = parseInt(destname.replace(/\D/g, ""), 10);

                atom1 = atoms.split("_")[0].split("-")[0]
                atom2 = atoms.split("_")[1].split("-")[0]
                
                str1 = res1+" and ."+atom1
                str2 = res2+" and ."+atom2
                manualHbond(mutantID, str1, str2, origin+ " to "+ destname2)
            })
        })
    }})
}



//NGL Tools
function exportStage(){
    stage.exportImage()
}

function ngl_toggle_spin(){
    setspin = !setspin
    stage.setSpin(setspin)
}

function ngl_reset_view(){
    var duration = 1000;
    molStructure.autoView(duration, seleres);
}

//Some button Tools
function resetZoom(element){
    switch(element){
        case "rmsd":
            rmsd_chart.resetZoom(mode = 'none')
        break;
        case "pairwise":
            pairwise_chart.resetZoom(mode = 'none')
        break;
        case "energy":
            energy_chart.resetZoom(mode = 'none') 
    }
}

function open_directory(){
    window.open("file://"+path_to_project, "_blank", "width=800,height=600,resizable=yes,scrollbars=yes");
}

//Exports all molecules in session to combined PDB file
async function exportPDB(opts = {}) {

   const {
    filename = "all_mutants_transformed.pdb",
    onlyVisible = false,
    includeRemarks = true
  } = opts;

  if (!stage || !stage.viewer) {
    console.error("NGL stage not found");
    return;
  }

  const rpad = (s, n, ch=" ") => (s+"").padEnd(n, ch).slice(0, n);
  const lpad = (s, n, ch=" ") => (s+"").padStart(n, ch).slice(-n);

  function formatAtomName(atomName="", element="") {
    const e = (element||"").trim().toUpperCase();
    const name = (atomName||"").trim();
    return (e.length === 1) ? rpad(name, 4) : lpad(name, 4);
  }

  function formatATOM({
    serial, het, atomName, altloc, resname, chainname, resno, inscode,
    x, y, z, occupancy=1.00, bfactor=0.00, element
  }) {
    const rec = het ? "HETATM" : "ATOM  ";
    return (
      rec +
      lpad(serial, 5) + " " +
      formatAtomName(atomName, element) +
      (altloc ? altloc[0] : " ") +
      lpad((resname||"").toUpperCase().slice(0,3), 3) + " " +
      (chainname ? chainname[0] : " ") +
      lpad(resno ?? 1, 4) +
      (inscode ? inscode[0] : " ") + "   " +
      lpad(x.toFixed(3), 8) +
      lpad(y.toFixed(3), 8) +
      lpad(z.toFixed(3), 8) +
      lpad(occupancy.toFixed(2), 6) +
      lpad(bfactor.toFixed(2), 6) +
      "          " +
      lpad((element||"").toUpperCase().slice(-2), 2)
    );
  }

  // Column-major matrix × [x y z 1]^T
  function applyMat4(x, y, z, M) {
    const e = M?.elements || M;
    if (!e || e.length !== 16) return { x, y, z };
    return {
      x: e[0]*x + e[4]*y + e[8]*z + e[12],
      y: e[1]*x + e[5]*y + e[9]*z + e[13],
      z: e[2]*x + e[6]*y + e[10]*z + e[14],
    };
  }

  // Collect components
  const comps = [];
  stage.eachComponent(c => {
    if (!c.structure) return;
    if (onlyVisible && !c.visible) return;
    comps.push(c);
  });

  if (!comps.length) {
    console.warn("No structure components to export.");
    return;
  }

  // Build the entire PDB content
  let out = "";
  if (includeRemarks) {
    out += "REMARK  100 Generated by exportTransformedPDBWithNames(): matrices applied\n";
    out += "REMARK  100 Each MODEL carries a TITLE with the mutantID\n";
  }

  let globalSerial = 1;
  let modelIndex = 1;

  for (const comp of comps) {
    const compName = (comp.name && String(comp.name).trim()) || `MODEL_${modelIndex}`;
    const M = comp.matrix && comp.matrix.elements ? comp.matrix : { elements: [
      1,0,0,0,
      0,1,0,0,
      0,0,1,0,
      0,0,0,1
    ]};

    out += `MODEL        ${String(modelIndex)}\n`;
    out += `TITLE     ${compName}\n`;
    out += `REMARK  100 NAME: ${compName}\n`;

    let prevChain = null;

    comp.structure.eachAtom(atom => {
      const chain = atom.chainname || "";
      if (prevChain !== null && chain !== prevChain) out += "TER\n";
      prevChain = chain;

      const p = applyMat4(atom.x, atom.y, atom.z, M);

      out += formatATOM({
        serial: globalSerial++,
        het: atom.isHetero,
        atomName: atom.atomname || atom.element || "X",
        altloc: atom.altloc || " ",
        resname: atom.resname || "UNK",
        chainname: chain || "A",
        resno: atom.resno ?? 1,
        inscode: atom.inscode || " ",
        x: p.x, y: p.y, z: p.z,
        occupancy: Number.isFinite(atom.occupancy) ? atom.occupancy : 1.00,
        bfactor: Number.isFinite(atom.bfactor) ? atom.bfactor : 0.00,
        element: atom.element || (atom.atomname ? atom.atomname[0] : "X")
      }) + "\n";
    });

    out += "ENDMDL\n";
    modelIndex++;
  }

  out += "END\n";

  // 🔹 Same CSV-like download method (no Blob, no URL.createObjectURL)
  const data = "data:text/plain;charset=utf-8," + encodeURIComponent(out);
  const link = document.createElement("a");
  link.setAttribute("href", data);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);  
}






//Some button Tools
async function exportPNG(element){
    var id = $("#idproject").val()

    switch(element){
        case "rmsd":
            //var image = rmsd_chart.toBase64Image();
            var divname = '#rmsdPNG'
            var name = 'RMSD_DYME_project'+id+'.png';
        break;
        case "perresidue":
            //var image = energy_chart.toBase64Image();
            var divname = '#perresiduePNG'            
            var name = 'PERRESIDUE_DYME_project'+id+'.png';
        break;
        case "pairwise":
            //var image = pairwise_chart.toBase64Image();
            var divname = '#pairwisePNG'
            var name = 'PAIRWISE_DYME_project'+id+'.png';
        break;
        case "energy":
            var divname = '#sequenceHolderAll'
            name  = `SEQUENCE-BY-ENERGY_DYME_project${id}.png`;
        break;
        case "contact": 
            var divname = '#contactPNG'
            name  = `CONTACT_EXPLORER_DYME_project${id}.png`;
        break;
         case "3D": 
            var divname = '#explorerPNG'
            name  = `CONTACT_EXPLORER_DYME_project${id}.png`;
        break;
        
    }   

     el = document.querySelector(divname);

     const image = await htmlToImage.toPng(el, {
        pixelRatio: 2,       // like scale
        cacheBust: true,     // avoids stale images
        backgroundColor: '#fff' // keep transparency; set to '#fff' if you want white
     });

        
        //var ecanvas = await html2canvas(el, { scale: 2, useCORS: true, allowTaint: false });

        //image = ecanvas.toDataURL('image/png');

   try {
        var a = document.createElement('a');
        a.href = image;       // Make sure "image" is a valid base64 string or URL
        a.download = name;    // Filename
        document.body.appendChild(a); // Best practice: append before clicking
    a.click();
    document.body.removeChild(a);
        console.log("Download started successfully.");
    } catch (error) {
        console.error("Failed to trigger download:", error);
    }
}

//Some button Tools
function exportXLS(element){
    var id = $("#idproject").val()
    switch(element){
        case "rmsd":
            var chart = rmsd_chart;
            var name = 'RMSD_DYME_project'+id+'.csv';
        break;
        case "perresidue":
            var chart = energy_chart;
            var name = 'PERRESIDUE_DYME_project'+id+'.csv';
        break;
        case "pairwise":
            var chart = pairwise_chart;
            var name = 'PAIRWISE_DYME_project'+id+'.csv';
        break;
        case "energy":
            //Generate data structure for energy explorer CSV export
            energycsv = {}

            seqvalues.forEach(function(seq){
                console.log(a)
            })
        


            return    
        break;
    }   
    downloadCSV({ filename: name, chart: chart })
}   

function convertChartDataToCSV(args) {  
    var result, ctr, keys, columnDelimiter, lineDelimiter, data;
  
    data = args.data || null;
    if (data == null || !data.length) {
      return null;
    }

    var label = args.label;
    columnDelimiter = args.columnDelimiter || ';';
    lineDelimiter   = args.lineDelimiter || '\n';
  
    // Filter out unwanted keys
    keys = Object.keys(data[0]).filter(key => !["v", "mutations", "y2"].includes(key));
  
    result = '';
    result += label + lineDelimiter;
    result += keys.join(columnDelimiter);
    result += lineDelimiter;
  
    data.forEach(function(item) {
      ctr = 0;
      keys.forEach(function(key) {
        if (ctr > 0) result += columnDelimiter;
        result += item[key];
        ctr++;
      });
      result += lineDelimiter;
    });

    return result;
  }
//Download CSV Feature
function downloadCSV(args) {
    var data, filename, link;
    var csv = "";
    for(var i = 0; i < args.chart.data.datasets.length; i++){
      csv += convertChartDataToCSV({
        data: args.chart.data.datasets[i].data,
        label: args.chart.data.datasets[i].label
      });   
    }
    if (csv == null) return;

    filename = args.filename || 'chart-data.csv';
  
    if (!csv.match(/^data:text\/csv/i)) {
      csv = 'data:text/csv;charset=utf-8,' + csv;
    }
    
    data = encodeURI(csv);
    link = document.createElement('a');
    link.setAttribute('href', data);
    link.setAttribute('download', filename);
    document.body.appendChild(link); // Required for FF
    link.click(); 
    document.body.removeChild(link);   
  }


// Launch a VMD xdg-open command
// requires registering the app:// protocol on the user's OS
function launchVMD(comp, res, file, mutid){

    var a = document.createElement('A');
    a.href = encodeURI(res);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function(){ $('#modalVMD').modal('hide')}, 1000);

    // Create a blob from the file content
    const blob = new Blob([file], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    // Create a temporary <a> element to trigger download
    a = document.createElement("a");
    a.href = url;
    a.download = "vmd_mutant_"+mutid+".vmd"
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

}



// Formatting function for row details - modify as you need
function format(d) {

    mut = mutantd[d]
    
    bonds = ""
    dest = ""
    
    Object.keys(mut).forEach(key => {
       pos   = mut[key]['pdb']
       atoms = mut[key]['hbonds']
       
       atoms.forEach(function(hbond){
          Object.keys(hbond).forEach(res_atom => {
             dest += res_atom+"-"+hbond[res_atom]+"<br>"
          })
       })
       bonds += "<tr><td>"+pos+"</td><td>"+dest+"</td></tr>"
       dest = ""
    });

    return (
        "<table class='table w-100'><thead><th>Ligand</th><th>Receptor</th></thead><tbody>"+bonds+"</tbody></table>"
    );
}









//Fill Hbonds Table
function renderHbondsTable_Old(comp,res){
    //console.log(res)
    mutanth = res
    //Clear

    dtcontrol = {
        className: 'dt-control',
        orderable: false,
        data: null,
        defaultContent: ''
    }

    dtcontrol = '<class="dt-control" orderable="false" data="" defaultContent=""></>'

    mt = [, mutanth.mutantID, mutanth.counters.backbone, mutanth.counters.side, mutanth.counters.total]

    mutantd[mutanth.mutantID] = mutanth.hbonds

    dataTable3.row.add(mt)   
    dataTable3.columns.adjust()
    dataTable3.draw(false)
}










//////////////////////////////////////////////////////////////////////////////////
///HBONDS TABLE

function reverseContactTable(){
    if(dict_cpptraj_index == "cpptraj_forward"){
        dict_cpptraj_index = "cpptraj_reverse"
    } else {
        dict_cpptraj_index = "cpptraj_forward"
    }
    renderHbondsTable("","")
}


function renderHbondsTable(comp,res){
    
    var mutarray   = mutantList["proc"]
    console.log("Response from hbondApiTable")
    //console.log(res)
    //Push Incoming mutant into the contact array
    if(res != ""){
        mutantObjects.push(res)     
    }
    
    var headerRow = $("#header-row");
    var tableBody = $("#table-body");
    //Add first header
            // Clear existing table content
    headerRow.empty();
    tableBody.empty();

    //Get original columns from Wildtype mutant
    
    headerRow.append("<th></th>");
    //headerRow.append("<th>WT</th>");

    //I. ///////////PAINT TABLE BASIC
    //Extract first column, combined with all mutants in the array (amino acid and position)
    row = 0
    lista = []

    for(i=0;i<=mutantObjects.length-1;i++){
        //console.log(i)
        //positions = Object.keys(mutantObjects[i]['cpptraj'])
        positions = Object.keys(mutantObjects[i][dict_cpptraj_index+contactThreshold])
        
        positions.forEach( function (pos){
            if(!lista.includes(pos)){
                lista.push(pos)
            }
        })
    }

    //Sort Nuemrically, without messing string keys
    //var collator = new Intl.Collator([], {numeric: true});
    
    lista = lista.sort(customSort)
    anchors1   = mutantObjects[0]['anchors']

    //Fill column 1 (position)
    lista.forEach( function (pos){
            classposition=""
            if(anchors1.includes(pos)){
                classposition="anchorred"
            }

            //tableBody.append("<tr id='"+pos+"'> <td class='"+classposition+" clickable'>" + pos + "</td></tr>"); //Creates a position TR row per element.
            //tableBody.append("<tr id='"+pos+"_accordeon' class='collapse accordion-collapse'><td id='"+pos+"_accordeon_td' colspan='"+(mutantObjects.length+1)+"' class='"+classposition+"'>as</td></tr>"); //Creates a position TR row per element.
            
            tableBody.append("<tr id='"+pos+"'> <td class='"+classposition+" clickable'>" + pos + "</td></tr>"); //Creates a position TR row per element.
            tableBody.append("<tr id='"+pos+"_accordeon'><td id='"+pos+"_accordeon_td' class='collapse accordion-collapse fontbig' colspan='"+(mutantObjects.length+1)+"' class='"+classposition+"'></td></tr>"); //Creates a position TR row per element.
    })
    tableBody.append("<tr id='_deltag'><td>ENERGY (ΔG)</td></tr>"); //Creates a position TR row per element.    
    //II. ///////////PAINT COLUMN CELLS PER MUTANT, COLORED AND PREETY
    //Start by iterating cpptraj object

    //This will often be Mutant #1
    //console.log(mutantObjects)
    indexwt  = findIndexByName(mutantObjects, "mut_"+current_wildtype);
    //console.log(indexwt)
    wildtype = mutantObjects[indexwt][dict_cpptraj_index+contactThreshold] //Get cpptraj object for wildtype - PENDING/ HANDLE EMPTY
    //If wildtype is different from 1, move wildtype to new position and exchange with another
    temp     = mutantObjects[0]
    mutantObjects[0] = mutantObjects[indexwt]
    mutantObjects[indexwt] = temp


    var mutantID
    allcppcontacts = []
    for(i=0;i<=mutantObjects.length-1;i++){
        //console.log(i)
        
        mutantID = mutantObjects[i]["name"]
        allcppcontacts[mutantID] = [];
        if(mutantID.includes(filterByName) || (i == indexwt)){
            //Create header for Wildtype and the rest. Just override Wt for MutantID 1
            console.log("Plotting mutant "+mutantID)
            
            //If first element is 1, wildtype
            //console.log(i)
            if(i == 0){
                headerRow.append("<th>Wildtype</th>");
                color = "greencell"
            } else {
                tit = mutantID.split("_")[1]
                ///<div class='minibox' style='background-color:"+color.color+"'></div> //For drawing color square
                headerRow.append("<th> Mutant "+tit+"</th>");
                color = "pending"
            }
            
            //Get all contacts for mutantID in cpptraj object iterator
            //positions = Object.keys(mutantObjects[i]['cpptraj']) 
            lista.forEach( function (pos) {
                //We can assume all positions exist in the table ids already
                //we simply add in order of appearence
                contactlist = []
                wtcontactlist = []

                    //First element of the mutantObject array
                    if(typeof wildtype[pos] !== 'undefined') {
                        wtcontacts = wildtype[pos]
                        //1. Compare contacts and decide color
                        wtcontacts.forEach(function(amino) {
                            if(!wtcontactlist.includes(Object.keys(amino)[0])) {
                                wtcontactlist.push(Object.keys(amino)[0]) //Holds an array of interacting positions with pos
                            }
                        })
                        color = ""
                    } 

                    //Actual mutant being compared
                    contcontacts = 0
                    vdw = 0
                    hbond = 0
                    bb = 0
                    ss = 0
                    orig = ""
                    dest = ""

                    if(typeof mutantObjects[i][dict_cpptraj_index+contactThreshold][pos] !== 'undefined') {
                        contacts   = mutantObjects[i][dict_cpptraj_index+contactThreshold][pos];                 
                        contacts.forEach(function(amino) {
                                //Push unique Contacts into a list for pos
                                atompair = Object.values(amino)[0]+"";
                                [orig, dest] = atompair.split("_") //Separate atoms
                                if (isVdW(orig,dest)){
                                    //console.log(orig)
                                    vdw=vdw+1
                                } else {
                                    hbond=hbond+1
                                }

                                //check if contat is with backbone or sidechain/ring
                                if (isBackbone(orig,dest)){
                                    bb=bb+1
                                } else {
                                    ss=ss+1
                                }

                                //Accumulate contacts
                                if(!contactlist.includes(Object.keys(amino)[0])) {
                                    contactlist.push(Object.keys(amino)[0]) //Holds an array of interacting positions with pos
                                    dna.forEach(function(base){
                                        a = Object.keys(amino)[0]
                                        if(a.includes(base)){
                                            sidechainstring = "Base"
                                        }
                                    })
                                }
                        })
                    }

                //Figure if we are equal than wildtype and paint accordingly
                if(haveSameContents(contactlist, wtcontactlist) && (color = "pending")){
                    color = "greencell"
                } else {
                    color = "redcell"
                }

                if(i == 0){
                    color = ""
                }

                tit = mutantID.split("_")[1]
                tooltip = `MutantID: ${tit} &#013;Res.Contacts: ${contactlist.length} &#013;&#013;HBond: ${hbond} | VdW: ${vdw} &#013;Backbone: ${bb} | ${sidechainstring}: ${ss}`
                //Paint Cell
                $("#"+pos).append("<td title='"+tooltip+"' href='#' id='"+pos+"_"+i+"' onclick='showAtomContent(\""+pos+"__"+i+"__"+mutantID+"\")' class='"+color+"'>"+contactlist.length+"</td>")
            })
            //Add last row with energy of this mutantID
            mutantID = mutantObjects[i]["mutantID"]
            //console.log("llegue aqui "+mutantID)
            a  = mutarray.find(o => o.mutantID === mutantID);
            
            dg = Math.round(a.deltag_total * 10)/10
            $("#_deltag").append("<td>" + dg + "</td>"); //Creates a position TR row per element.
        }
    }
    
    

}


/////////////////////////////////////////////////////////
//Helper Functions for Hbonds Table
//Jan 11 2024
function showAtomContent(posmut){
    [pos, position, name] = posmut.split("__")
    atomlists = {}
    aminolist = {}
    var contacts   = mutantObjects[position][dict_cpptraj_index+contactThreshold][pos];

    //Process Information for position
    contacts.forEach(function(amino) {
        Object.keys(amino).forEach(function(targetamino){
            var dest = ""
            var orig = ""
            var atompair = amino[targetamino]+"";
            [orig, dest] = atompair.split("_") //Separate atoms
            posA = pos+" "+orig
            posB = targetamino+" "+dest

            //Check if contact is wdw or hbond
            if (isVdW(orig,dest)){
                type="vdw"
            } else {
                type="hbond"
            }

            //check if contat is with backbone or sidechain/ring
            if (isBackbone(orig, dest)){
                with1="Backbone"
            } else {
                with1=sidechainstring // o base
            }
            
            //Build tree content
            if(typeof atomlists[targetamino] == "undefined" ){
                atomlists[targetamino] = {}
            }

            if(typeof atomlists[targetamino][orig] !== "undefined" ){
                atomlists[targetamino][orig].push({'atom': dest, 'type': type, 'with': with1})
            } else {
                atomlists[targetamino][orig] = [{'atom': dest,  'type': type, 'with': with1}]
            }
        })
    })

    
    //Build HTML
    //console.log(atomlists)
    //Convert pos to mutation in pos
    container = positionElement.replace("||pos||",pos)
   
    aminoelems = ""
    Object.keys(atomlists).forEach(function(destamino){
        aminoelem = aminoElement.replace("||amino1||",destamino)
        atomelems = ""
        Object.keys(atomlists[destamino]).forEach(function(origatom){
            atomelem = atomElement.replace("||atomOrig1||", origatom) 
            bond = ""
            atomlists[destamino][origatom].forEach(function(destatom){
                atom = destatom['atom']
                type = destatom['type']
                with1= destatom['with']

                bond += '<li class="'+type+'">'+atom+'('+with1+')</li>'
                //remember to add icons of bonds
            })
            atomelem = atomelem.replace("||atoms_desti||",bond)
            atomelems += atomelem
        })
        aminoelem = aminoelem.replace("||atoms||",atomelems)
        aminoelems += aminoelem
        //console.log(atomelems)
    })
    container = container.replace("||aminos||",aminoelems)
    nameforfield = "Mutant ID:  "+name.split("_")[1];
    container = `<b>${nameforfield}</b> <a style="color: blue" onclick="collapseall()">(collapse)</a> <br><br> ${container}`
    //console.log(container)
          
    idaccordeon = "#"+pos+"_accordeon_td"
    $("tr > .collapse:visible").toggle()
    $(idaccordeon).toggle();
    $(idaccordeon).html(container)
}


//Classifies a bond in vdw or hbond
//Classifies a bond in vdw or hbond
function isVdW(a1,a2){
    var toBeReturned=false;
    hydrophobic.forEach(function(atom){
        if((a1.includes(atom)) || (a2.includes(atom))){
            toBeReturned = true
        }
    })
    return toBeReturned
}

//Determines if the contact is sidechain or ring
function isBackbone(a1, a2){
    //Protein
    var toBeReturned=true;
    sideChainAtoms.forEach(function(atom){
        if((a1.includes(atom)) || (a2.includes(atom))){
            toBeReturned = false;
        } 

        //if((a1.length == 1) || a2.length == 1){
        //    if( (a1 == "N") || (a2 == "N")  ) {
        //        toBeReturned = true
        //    }
        //}
    })
    return toBeReturned
}

const customSort = (a, b) => {
    const numA = parseInt(a.match(/\d+/)[0]);
    const numB = parseInt(b.match(/\d+/)[0]);
    return numA - numB;
};

function findIndexByName(array, nameToFind) {
    for (let i = 0; i < array.length; i++) {
        if (array[i].name === nameToFind) {
        return i; // Return the index if the name is found
        }
    }
    return -1; // Return -1 if the name is not found in the array
}

function changeSource(){
    dict_cpptraj_index = $("#selsource").val();
    renderTable()
}

function setFilterSite(){
    filterByName = $("#seltarget").val();
    renderTable()
}

function collapseall(){
    $("tr > .collapse:visible").toggle()
}

const haveSameContents = (a, b) => {
    for (const v of new Set([...a, ...b]))
        if (a.filter(e => e === v).length !== b.filter(e => e === v).length)
        return false;
    return true;
    };

    const ordered = (mutantObj) => {Object.keys(mutantObj).sort().reduce(
            (obj, key) => { 
                obj[key] = mutantObj[key]; 
                return obj;
            }, 
        {}
        );
    }

function changeThreshold(threshold){
    if(threshold == 10){
        threshold = ""
    }
    contactThreshold = threshold
    renderHbondsTable("","")
}
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////






//1 Ask Dyme to select ids for you
//2 Return ids and call this function

//Table Filters
function filterByMutations(ids){
   tam = ids.length-1
    if(ids.length > 0) {
        ids = ids.join([separator = '|'])
        // ids should contain the ids like this 1|470|715|924
        dataTable2.column(0).search('^('+ids+')$',true,false).draw()
    }
    setTimeout(function(){ 
        $('#staticBackdrop').modal('hide')
        
        if(tam == 0){
            res = confirm("This mutant combination doesn't exist. Would you like to simulate it?")
            if(res){
                enqueueNewMutant(filterCriteria)
            } else {

            }
        }

    }, 2000)
    
}


function renderFilterOptions(){
    var btn = ''
    elem = []
    selectors = ""
    classs = "btn-xs btn-primary float-end"
    labclass = "float-start"
    //Create a dropdown per anchorpoint with their corresponding mutable combos
    Object.entries(residuemap).forEach(function(res){
            //console.log(res)
            selector = ""
            res[1].forEach(function(chain){
                if(chain !== null){
                    if(chain["isanchor"]){
                        console.log(chain)
                        pos  = chain["resno_NGL"]
                        pdb  = chain["resno_PDB"]
                        opts = chain["mutable_into"]
                        nom = to1[chain["name"]]
                        ch = chain["chain"]
                        //elem.push({"id": pos, "pos": nom+pos, "res": opts})
                        selector = `<label class='${labclass}' for="f_${pos}">${nom+pdb}</label>&nbsp;&nbsp; <select class="${classs}" id='f_${pos}' name='f_${pos}' onchange='addcriteria(this, "${pos}", "${nom}", "${ch}", "${pdb}")'>`
                        o = "<option value='0'>Add..</option>"
                        console.log(opts)
                        if (Object.keys(opts).length !== 0) {
                        opts.forEach(function(a){
                            o = o+`<option value='${a}'>${a}</option>`
                        })
                        } else {
                            standard_residues.forEach(function(a){
                                o = o+`<option value='${a}'>${a}</option>`
                            })
                        }
                        

                        selectors = selectors+selector+o+"</select><br>"
                    }
                }  
            })
    })
    $("#anchorpointlist_filter").html(selectors)
}

function addcriteria(selected, pos, nom, chain, pdb){
    crit = selected.value
    //alert(`${pos}:${nom} is ${crit}`)
    ind = `${chain}:${pos}`
    if(filterCriteria.length <=  2){
        filterCriteria.push({index: ind, pos: pos, nom: nom, res: crit, pdb: pdb})
    } else {
        alert("The maximum filter criteria is a triplet")
    }
    selected.selectedIndex = 0; 
    
    //Add to filter list card
    updateFilterList()
    
}

function updateFilterList(){
    //anchorpointlist_criterias
    text = ""
    filterCriteria.forEach(function(crit){
        text += '<div class="badge bg-primary text-white rounded-pill">'+crit["nom"]+":"+crit["pdb"]+":"+crit["res"]+'</div>'
    })
    $("#anchorpointlist_criterias").html(text)
}

function clearCriteria(){
    filterCriteria = [] 
    updateFilterList()
}

function closeCriteria(){
    $("#filterModal").modal('hide')
}

function closeReplica(){
    $("#replicaBackdrop").modal('hide')
}

function closeWatersites(){
    $("#waterBackdrop").modal('hide')
}

function openWatersites(id){
    
}


function clearSearch(){
    dataTable2.column(0).search('',true,false).draw()
    $("#filterModal").modal('hide')
}