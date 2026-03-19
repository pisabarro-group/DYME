//NGL objects
var stage
var molStructure
var contacts

//NGL Representation Objects for Step 4
var interfaceRepresentation = [{res: ""}] //Pointer to Atoms between mutable protein and all other objects
var allRepresentation //Pointer to all Atoms, default representation
var chainByChainRepresentation = [] //Array of representations by chain
var representationTypes = ["backbone", "ball+stick", "line", "point", "ribbon"]
var mutable_chains = []
var anchors = []

//NGL selectors
var chainByChainSelector = [] //Chain by chain selector
var idxlist = [] // First atom of each chain

//DYME Variables
var Dyme_Projectinputs = []
var Dyme_Simulation = []
var Dyme_MolecularObjects = []
var Dyme_Anchorpoints = []
var Dyme_Analysis = []
var Dyme_Clusters = []
var Dyme_Residuemap = {}


// A $( document ).ready() block.
$( document ).ready(function() {
    fillLeapOptions() 
    $("#projectName").focus()
    $(".colorPickSelector").colorPick(); //Load Colorpicker for Step4

    //Show by default
    $("#cutoffRow").prop('hidden', false); 
    $("#constraintTolRow").prop('hidden', false); 
    $("#ewaldTolRow").prop('hidden', false);
    

});

//Close accrodion elements when other open
var myGroup = $('#accordionExample');
myGroup.on('show.bs.collapse','.collapse', function() {
    //myGroup.find('.collapse').collapse('hide');
});



//Resize Events for NGL viewer
window.addEventListener( "resize", function( event ){
    stage.handleResize();
}, false );

//Only allow Alphanumeric and Spaces in the project name
  $('#projectName').keyup(function() {
    if (this.value.match(/[^a-zA-Z0-9 ]/g)) {
      this.value = this.value.replace(/[^a-zA-Z0-9 ]/g, '');
    } 
  });
  
  $('#projectName').focusout(function() {
    this.value = this.value.trim();
  });


  $("#pdbFile").change(function(){
   // alert("A file has been selected.");
   $("#pdbFileName").html(this.files[0].name);
   $("#pdbFileName").prop('hidden', false); 
   $("#pdbAlert").prop('hidden', true); 
  });

   
   $("#leadPdbFile").change(function(){
    // alert("A file has been selected.");
    $("#leadPdbFilename").html(this.files[0].name);
    $("#leadPdbFilename").prop('hidden', false); 
    $("#leadPdbFilenameAlert").prop('hidden', true); 
    $("#btnNextStep1").prop('disabled', false);
   });
 
   //Control what happens when step1 tabs are changed - changes the sourcetype
   $('a[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
        var target = $(e.target).attr("aria-controls") // 

        if(target == "frompdb")
            $("#sourcetype").val("pdb")
        
        if(target == "fromamber")
            $("#sourcetype").val("amber")
   });



  //Control Changes on Chain selector checkboxes
  $("#heteroatoms").change(function(){
    checkboxes = document.getElementById("chainSelectorTable").getElementsByTagName("input")
    var any = false
    //If any checkboxes are selected, show continue
    for (var i = 0; i < checkboxes.length; i++)
        any |= checkboxes[i].checked
    $('#continueChainsBtn').prop( "disabled", !any );

    if (window['stage'] != undefined) {
        heterogens = document.getElementById('heteroatoms').value
        molStructure.removeAllComponents();


        if (heterogens == 'water')
                selection += "A and (protein or nucleic or water)"
        
        if (heterogens == 'none')
                selection += " and (protein or nucleic)"

                molStructure.addRepresentation("cartoon", {sele: "A and (protein or nucleic or water)"});
                molStructure.addRepresentation("cartoon", {sele: "B and (protein or nucleic or water)"});
                molStructure.addRepresentation("ball+stick", {sele: "C and (protein or nucleic or water)"});
        
   }});


   //Step3 Textfields
   $("#dt").on('input',function(){ 
        if($("#dt").val() > 4){
            alert("Time steps larger than 4 femtoseconds are likely to fail. Choose a value between 1 and 4");
        }
        recalculate() 
    });
   $("#steps").on('input',function(){ recalculate() });
   $("#equilibrationSteps").on('input',function(){ recalculate() })
   $("#totalframes").change(function(){ 
    if($("#totalframes").val() > 5000){
        alert("This setting will make MD trajectory files 10 times bigger. Make sure you have enough disk space");
    }
    recalculate() 
    });
   $("#leapWaterboxSize").on('input',function(){ recalculate() });
   
   //Step3 ChangeSelect
   $("#nonbondedmethod").change(function(){
     if($("#nonbondedmethod").val() == "NoCutoff"){
        $("#cutoffRow").prop('hidden', true); 
        $("#constraintTolRow").prop('hidden', true); 
        $("#ewaldTolRow").prop('hidden', true); 
     } 
     if($("#nonbondedmethod").val() == "CutoffNonPeriodic"){
        $("#cutoffRow").prop('hidden', false); 
        $("#constraintTolRow").prop('hidden', false); 
        $("#ewaldTolRow").prop('hidden', true); 
    } 
    if($("#nonbondedmethod").val() == "CutoffPeriodic"){
        $("#cutoffRow").prop('hidden', false); 
        $("#constraintTolRow").prop('hidden', false); 
        $("#ewaldTolRow").prop('hidden', true);
    } 
    if($("#nonbondedmethod").val() == "PME"){
        $("#cutoffRow").prop('hidden', false); 
        $("#constraintTolRow").prop('hidden', false); 
        $("#ewaldTolRow").prop('hidden', false);
    } 

    if($("#constraints").val() == "none"){
        $("#constraintTolRow").prop('hidden', true); 
     } else {
        $("#constraintTolRow").prop('hidden', false); 
     } 

   });

   //Setep3 Constraints
   $("#constraints").change(function(){
    if($("#constraints").val() == "none"){
        $("#constraintTolRow").prop('hidden', true); 
     } else {
        $("#constraintTolRow").prop('hidden', false); 
     } 
   });


   //Step3 NPV NTP
   $("#ensemble").change(function(){
        if($("#ensemble").val() == "nvt"){
            $("#pressureRow").prop('hidden', true); 
            $("#barostatIntervalRow").prop('hidden', true);
        } else {
            $("#pressureRow").prop('hidden', false); 
            $("#barostatIntervalRow").prop('hidden', false);
        }
   })


   //Recalculate Time length values and frame duration
   function recalculate(){
        dt = $("#dt").val()
        st = $("#steps").val()
        eq = $("#equilibrationSteps").val()
        fr = $("#totalframes").val() //Frames to capture


        //sets the same water box bufer size as cuttoff later on
        bufferbox = $("#leapWaterboxSize").val()
        cut = bufferbox/10
        totalt = dt*st
        eqtime = dt*eq
        $("#equilibrationtime").html(solveUnit(dt*eq))
        $("#simulationtime").html(solveUnit(dt*st))
        $("#frameSize").html(solveUnit((st/fr)*dt))
        $("#cutoff").val(Number(cut.toPrecision(1)))
        
   }
   //Solve timelength vs units
   function solveUnit(val){
    
        ind = (val/1000).toString()
        if(val.length <= 3){
            return val+"fs"
        }

        if(ind.length <= 3){
            return ind+"ps"
        }

        ind = (val/1000000).toString()
        if(ind.length <= 3){
            return ind+"ns"
        }

        ind = (val/1000000000).toString()
        if(ind.length <= 3){
            return ind+"ms"
        }
   }

 //Success Action
 function processResult(res){
    //alert(JSON.stringify(res, null, 4));    
    switch(res.action){
        case "showmessage":
            showAlert("Response",res.response);
        break;
        case "fillLeapOptionsSelect":
            $("#leapSources").html(res.response);
        break;

        case "gotoStep2":
            //Show next tab
            $('#wizard2-tab').tab('show');
            loadNGLViewer($("#viewport"));
            checkChains();
        break;

        case "gotoStep3":
            //Show next tab
            $('#wizard3-tab').tab('show');
            //alert(res.response)
            $("#cutoffRow").prop('hidden', true); 
            $("#constraintTolRow").prop('hidden', true); 
            $("#ewaldTolRow").prop('hidden', true); 
        break;

        case "gotoStep4":
            //Show next tab
            $('#wizard4-tab').tab('show');
            setTimeout(function(){
                // Get the width here
                loadNGLViewer($("#step4viewport"));

            },1000);
        break;

            //loadNGLViewer();
            //checkChains();
        
    }
    console.log("Call ok - Server responded API request to "+res.action);
 }

//Shows loading overlay modal
function showLoading(){
    //alert("loading")
}
//Hides loading overlay modal
function removeLoading(){
    //alert("removeLoading")
}





//Loads NGL Viewer into the viewport
function loadNGLViewer(canvas) {
    stage = new NGL.Stage(canvas.attr("id"));
   
    stage.loadFile("api/getCurrentStructure", {ext:"pdb", defaultRepresentation: false}).then(function(o){
        //molStructure.clearRepresentations();
        molStructure = o
        allRepresentation = molStructure.addRepresentation("cartoon", {sele: "all", color: "#3998DB"});

        molStructure.autoView();

        if(canvas.attr('id') == "step4viewport"){
            $("#step4loading").remove();
            //document.body.appendChild(tooltip) //Create Custom Tooltip for viewer
            //stage.mouseControls.remove('hoverPick')
            //addTooltip()
            populateChainSelectorObjects(1); //Fill select boxes with chains for molecule object assigners
            paintChainButtons(); // Show buttons with red representations on hover
        }
    })  

    box = canvas.width();
    canvas.css({"width:": box+"px", "height": box+"px", "overflow": ""});
    stage.handleResize();
}


//MOLECULE VERIFICATION CHECKS
//--------------------------------------
function checkChains(){
//--------------------------------------
   //If more than 2 chains, select which ones

}

function checkResidues(){
    //If chains Ok, check residues in chains
}


function checkHeavyAtoms(){

}


//Accordeon 1

$("#continueChainsBtn").click(function(){

})




//Accordeon 2

$("#selectAllMissing").click(function(){

})


$("#deselectAllMissing").click(function(){

})


$("#btnCheckMissingResidues").click(function(){

})


//Accordeon 3
//Convert Nonstandard
$("#nstSelectAll").click(function(){

})

$("#nstDeselectAll").click(function(){

})

$("#btnFixSelectedNonstandard").click(function(){

})

//Add definitions for Nonstandard
$("#btnApplyCustomDefinitions").click(function(){

})


//Accordion 4
$("#btnFixAtoms").click(function(){

})


//Accordion 5
$("#btnSetWaterBox").click(function(){

})


//MOLECULE VERIFICATION ACTIONS
//--------------------------------------
function fixChains(){

}

function fixNonStandardResidues(){

}

function fixHeavyAtoms(){

}

function addHydrogens(){

}

function addWaterbox(){

}




//Validate inputs for Step 1 of the wizzard
//Used by btnNextStep1
//--------------------------------------
function validateStep1(){
        //--------------------------------------
        // Validate Project Name

        forcefield = $("#inputForcefield");
        waterSelect = $("#inputFWater");
    
        if($("#projectName").val() == ""){
            showAlert("Alert", "You must provide a name for your project")
            $("#projectName").focus();
            return false;
    
        } else if ($("#projectName").val().length <= 5){
            showAlert("Alert", "Your project name must be at least 5 characters long")
            $("#projectName").focus();
            return false;
        } 
        
    
        //VALIDATE PDB SOURCE
        if($("#sourcetype").val() == "pdb"){
            // Validate Forcefield and waterModel
            if (forcefield.val() == 0 || waterSelect.val() == "0"){
                showAlert("Alert","You must select a Force field and Water model");
                return false;
            }   
            // Validate file selector / dropdown
            if ($("#pdbFileName").html() == ""){
                showAlert("Alert","You must upload a file containing your molecules");
                return false; 
            }
        }

      
        //VALIDATE AMBER SOURCES
        if($("#sourcetype").val() == "amber"){
            // Validate file prmtop
            if ($("#leapPdbFile").html() == ""){
                showAlert("Alert","You must select a starting topology first (PDB file)");
                return false; 
            }
            // Validate file inpcrd
            if ($("#leapWaterbox option:selected").val() == "0"){                
                showAlert("Alert","You must select a Solvation Method!");
                return false; 
            }
        }

        if($("#leapWaterbox").val() == 0){
            showAlert("You must define a Solvation Method before continuing")
            return false
        }

    callApi("step1","#formStep1","");
}


//--------------------------------------
function validateStep2(){
//--------------------------------------

}


//--------------------------------------
function validateStep3(){
//--------------------------------------
    callApi("step3","#simulationOptions","");
}
    
    


//Water models allowed for each forcefield in OpenMM
var amber14WaterModels = [
    ["amber14/tip3p.xml", "TIP3P", false],
    ["amber14/tip3pfb.xml", "TIP3P-FB", true],
    ["amber14/spce.xml", "SPC/E", false],
    ["amber14/tip4pew.xml", "TIP4P-Ew", false],
    ["amber14/tip4pfb.xml", "TIP4P-FB", false],
    ["implicit/obc2.xml", "OBC (implicit solvent)", false],
    ["implicit/GBn.xml", "GBn (implicit solvent)", false],
    ["implicit/GBn2.xml", "GBn2 (implicit solvent)", false]
]

var charmm36WaterModels = [
    ["charmm36/water.xml", "CHARMM default", true],
    ["charmm36/tip3p-pme-b.xml", "TIP3P-PME-B", false],
    ["charmm36/tip3p-pme-f.xml", "TIP3P-PME-F", false],
    ["charmm36/spce.xml", "SPC/E", false],
    ["charmm36/tip4pew.xml", "TIP4P-Ew", false],
    ["charmm36/tip4p2005.xml", "TIP4P-2005", false],
    ["charmm36/tip5p.xml", "TIP5P", false],
    ["charmm36/tip5pew.xml", "TIP5P-Ew", false],
    ["implicit/obc2.xml", "OBC (implicit solvent)", false],
    ["implicit/GBn.xml", "GBn (implicit solvent)", false],
    ["implicit/GBn2.xml", "GBn2 (implicit solvent)", false]
]

var oldAmberWaterModels = [
    ["tip3p.xml", "TIP3P", false],
    ["tip3pfb.xml", "TIP3P-FB", true],
    ["spce.xml", "SPC/E", false],
    ["tip4pew.xml", "TIP4P-Ew", false],
    ["tip4pfb.xml", "TIP4P-FB", false],
    ["tip5p.xml", "TIP5P", false],
    ["implicit", "OBC (implicit solvent)", false]
]

var amoebaWaterModels = [
    ["explicit", "Explicit", true],
    ["implicit", "Implicit", false]
]



//Controls onChange events of the Forcefield selector of the wizzard
//creates the proper list of water models in the water model dropdown
// ** Mirrored from Peter Eastman's openmm-setup with a few tweaks
//--------------------------------------
function handleWater(sel) {
//--------------------------------------
forcefield = sel.value;
waterSelect = $("#inputFWater")[0];
currentWater = waterSelect.value;

if(sel.value == "0"){
    $("#inputFWater").prop( "disabled", true );
    sel.selectedIndex = 0;
    waterSelect.selectedIndex = 0;
} else {
    $("#inputFWater").prop( "disabled", false );

}

if (forcefield == 'charmm_polar_2019.xml')
    $("#waterModelRow").hide();
else {
    $("#waterModelRow").show();
    if (forcefield.includes("amber14"))
        models = amber14WaterModels;
     else if (forcefield == "charmm36.xml")
        models = charmm36WaterModels;    
     else if (forcefield == "amoeba2018.xml")
        models = amoebaWaterModels;
    else
        models = oldAmberWaterModels;

    while (waterSelect.length > 0)
        waterSelect.remove(0)

    //Add first option of DYME
    option = document.createElement("option");
    option.value = "0";
    option.text = "Select a Water Model...";
    waterSelect.add(option);

    for (i = 0; i < models.length; i++) {
        option = document.createElement("option");
        option.value = models[i][0];
        option.text = models[i][1];
        waterSelect.add(option);
    }
    for (i = 0; i < models.length; i++)
        if (models[i][2])
            waterSelect.selectedIndex = i;
    for (i = 0; i < models.length; i++)
        if (currentWater == models[i][0])
            waterSelect.selectedIndex = i;

    waterSelect.selectedIndex = 0;
}
}


//Controls onChange events of the waterSelect selector
//Enables the btnNextStep1 if watermodel is chosen (doesn't validate file)
//--------------------------------------
function activateContinue(sel){
//--------------------------------------
if(sel.value == "0"){
   $("#btnNextStep1").prop('disabled', true);
} else {
   $("#btnNextStep1").prop('disabled', false);
}
}






//Loads Option list for amberTleap sources
//Get availble sources from leap directory
function fillLeapOptions(){
    callApi("getLeapSources","","");
}

function handleAddleapSource(selected){
      a = selected.value
    ico = "<i class='fa fa-check text-primary'></i>"
    can = "<button class='btn btn-xs btn-icon float-end' type='button' onclick='this.parentElement.remove(this);remleapsource(a)'><i class='fa fa-times'></i></button>";
    opt = "<li class='list-group-item'>"+ico+' '+a+' '+can+"</li>";
    
    $("#leapSources").val($("#leapSources option:first").val());
    $("#leapSourcesList").append(opt);
    $("#leapSourcesContent").append("<option value='"+a+"' selected>"+a+"</option>");
    
}

$("#leapFiles").change(function(){
    var names = $('#leapFiles')[0].files;
    $("#leapSourcesListUploaded").html("");
    for(var i=0 ; i <= names.length-1 ; i++) {
        ico = "<i class='fa fa-check text-primary'></i>"
        can = "<button class='btn btn-xs btn-icon float-end' type='button' onclick='$(\"#leapSourcesListUploaded\").html(\"\"); document.getElementById(\"leapFiles\").value=\"\"'><i class='fa fa-times'></i></button>";
        opt = "<li class='list-group-item'>"+ico+$('#leapFiles')[0].files.item(i).name+can+"</li>";
        $("#leapSourcesListUploaded").append(opt);
    }
});
//Updates leapSourcesContent hidden selector (this is what sends the array of selected leap sources)
function remleapsource(val){
    alert(val)
    $("#leapSourcesContent option[value='"+val+"']").remove();
}


//STEP4 FUNCTIONS - 



//STEP4 BUTTON CLICKS
//Next1 Button

//ADD MOLECULE
$("#addMolecule").click( function (){
    var contelems = $("#tablanames").children().length+1
    var molid = "mol"+contelems;
    var chainselectd = "chainselectortd"+contelems;
    var resindextd = "resindextd"+contelems;

    var nueva = '<tr><td><div class="colorPickSelector" id="'+molid+'"></div></td><td><input type="text" name="molname['+contelems+']" id="molname['+contelems+']" value="" placeholder="Desired Name" class="form-control"></td><td id="'+chainselectd+'"><select id="chainselector['+contelems+']" name="chainselector['+contelems+']" class="form-control" onselect="addChainToObject(this)"><option>Add Chain...</option></select></td><td>    <ul id="'+resindextd+'" class="list-unstyled" style="overflow: auto; white-space: nowrap;">        <li class="float-start align-middle">            <div class="w-5 d-inline-flex">Chain-A[GLU1]</div>            <div class="w-25 d-inline-flex"><input type="text" name="offset['+contelems+'][]" id="offset['+contelems+'][]" value="0"  maxlength="4" placeholder="Desired Name" class="form-control"></div>        </li>    </ul></td><td>    <div class="form-check align-left">        <input class="form-check-input float-start" type="checkbox" id="mutable['+contelems+']">        <label class="form-check-label float-start" for="flexCheckDefault">           Mutable?        </label>    </div></td></tr>';
    $("#tablanames").append(nueva);
    $("#"+molid).colorPick({"initialColor": getRandomColor()});
    $("select").on('mouseenter','option',function(e) {
        console.log("hols")
        // this refers to the option so you can do this.value if you need..
    });
    populateChainSelectorObjects(contelems);
    $("#nextDiv1").attr("hidden", false);
})

//RESET ADD MOLECULE
$("#resetAddMolecule").click( function(){
    $("#tablanames").html(""); 
    $("#nextDiv1").attr("hidden", true);
})






//NEXT1 BUTTON
$("#nextDYME1").click(function(){
    //Validate First panel options and fire accordeon step 2

    //Number of Molecular Objects Defined
    if($('[id^=resindextd]').length >= 2){
        $('[id^=resindextd]').each(function(k, ele){
            //Check if each object has chains
            if($(ele).children().length !== 0){
                //Check if at least one object is mutable
                var ischecked = false
                var cant = 0
                $('[id^=mutable]').each(function(k, ele){
                    if($(ele).is(':checked')){
                        ischecked = true
                        cant=cant+1
                    }
                })

                //Check that there is at least one mutable object
                if(!ischecked){
                    showAlert("Error","You must declare at least one Molecular Object as 'Mutable'");
                    return
                } //Also check if user chose more than one! not supported yet
                if(cant > 1){
                    showAlert("Error","Only one Mutable object is currently supported. Put all your mutable chains in the same object");
                    return    
                }

                //TODO Check that all chains are assigned to molecular objects

                //Check if each object was given a name
                $('[id^=molname]').each(function(k, ele){
                    if($(ele).val() === ""){
                        showAlert("Error","Check that all Molecular Objects have a name (column 1 of the table)");
                        return    
                    }
                })

                //Collapse Dyme Accordeon
                //$("#collapseDyme1").collapse().toggle("");
                
                $("#collapseDyme1").collapse("hide");
                $("#collapseDyme2").collapse("show");

                //ALL TESTS PASSED. MOVE TO ACCORDEON2
                //1. Paint the viewer per object color / Remove chain hover buttons
                removeControlButtons()
                //2. Build molecular object arrays
                buildMolecularObjects()
                //3. Build anchor selector Grid and paint in accordeon 2             
                //4.Build ResidueMaps
                buildResidueMapTranslation()
                // 3.1 Get intermolecular contacts between Mutable objects and all others - render anchor selector grid from it
                recomputeRepresentations() //Includes BuildAnchorGrid!!!!!

               
                //
                

                // 3.2 make every button a residue, same color as objects. Orange is reserved for selected residues
                //switchToNextDyme2()
                // 3.3 each selected residue displays on hover over the button. each selected residue displays surface
                //4. Close accordeon 1 and open accordeon 2
                

            } else {
                showAlert("Error","You must Add at least one chain to each Molecular Object");
                return
            }
        })
    } else {
        showAlert("Error","You must define at least 2 Molecular Objects");
        return
    }
})





//NEXT2 BUTTON
$("#nextDYME2").click(function(){
    //Validate First panel options and fire accordeon step 3
    $("#collapseDyme2").collapse("hide");
    $("#collapseDyme3").collapse("show");
    $("#collapseDyme4").collapse("hide");
    $("#collapseDyme5").collapse("hide");
    $("#collapseDyme6").collapse("hide");

})


//NEXT3 BUTTON
$("#nextDYME3").click(function(){
    //Validate First panel options and fire accordeon step 3
    buildMutagenesisTable()
    $("#collapseDyme2").collapse("hide");
    $("#collapseDyme3").collapse("hide");
    $("#collapseDyme4").collapse("show");
    $("#collapseDyme5").collapse("hide");
    $("#collapseDyme6").collapse("hide");
    resetComplexityTable()


})

$("#nextDYME4").click(function(){
    drawAnchorDivsDraggable();
    drawInitialClusters();
    $("#collapseDyme2").collapse("hide");
    $("#collapseDyme3").collapse("hide");
    $("#collapseDyme4").collapse("hide");
    $("#collapseDyme5").collapse("show");
    $("#collapseDyme6").collapse("hide");
})

$("#nextDYME5").click(function(){
  //  $("#collapseDyme2").collapse("hide");
  //  $("#collapseDyme3").collapse("hide");
  //  $("#collapseDyme4").collapse("hide");
  //  $("#collapseDyme5").collapse("hide");
  //  $("#collapseDyme6").collapse("show");
    computeAllConfigsCheck();
})



///////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////

// NEXTDYME 1 STUFF

// INSPIRED BY GITHUB/LIBMOL (Paul Pillot)
// HANDLES SOME NGL VIEWER FEATURES FOR SELECTOR LOGIC AND MANY MORE


// GetAtomList from # to Range
function getAtomListFromAToRange(start, range) {
    var numArr = [];
    for (var i = 0; i < range; i++) {
        numArr.push(start + i);
    }
    return numArr;
}

//Make Residue
function makeRes(atomP) {
    return {
        chainname: atomP.chainname,
        resname: atomP.resname,
        resno: atomP.resno,
        element: atomP.element,
        description: atomP.entity ? atomP.entity.description : 'unknown',
        atomList: getAtomListFromAToRange(atomP.residueAtomOffset, atomP.residueStore.atomCount[atomP.residueIndex])
    };
}

var contactTypesIndices = [
    'unknown',
    'ionicInteraction',
    'cationPi',
    'piStacking',
    'hydrogenBond',
    'halogenBond',
    'hydrophobic',
    'metalCoordination',
    'weakHydrogenBond',
    'waterHydrogenBond',
    'backboneHydrogenBond'
];




//Select residues with contacts
//Receives Representation Object
function getContactsArray(c) {
    contactPicker = c.repr.bufferList[0].picking;
    contactStore  = contactPicker.contacts.contactStore;
    atomSets      = contactPicker.contacts.features.atomSets;
    contactsDisplayed = contactPicker.array.reduce(
        function (arr, val) {
            if (arr.indexOf(val) === -1) {
                arr.push(val);
            }
            return arr;
        }, []);

    //console.log(contactsDisplayed)

    var contactsArray = [];
    structure         = molStructure.structure

    contactsDisplayed.forEach(function (val) {
        var atom1 = structure.getAtomProxy(atomSets[contactStore.index1[val]][0]);
        var res1 = makeRes(atom1);
        var atom2 = structure.getAtomProxy(atomSets[contactStore.index2[val]][0]);
        var res2 = makeRes(atom2);
        var type = contactStore.type[val];

        contactsArray.push({
            res1: res1,
            res2: res2,
            type: contactTypesIndices[type],
            seleString: '@' + res1.atomList.join(',') + ',' + res2.atomList.join(',')
        });
    });
    return contactsArray;
}




//Filter intermolecular contacts only (at the interfaces)
//receives contactsArray
function getInterfaceContactArray(co, mutableChains=["B"]){
    var intermolecularcontactsArray = [];
    interfaceRepresentation = [{res: ""}];
    alreadyAdded = []
    co.forEach(function (contacto) {
        //Filter by contact type... fetch Intermoleculars Only
        //console.log(contacto)
        if(contacto.res1['chainname'] !== contacto.res2['chainname']){
            //console.log(contacto)
            if(mutableChains.includes(contacto.res1['chainname'])){
                if(!mutableChains.includes(contacto.res2['chainname'])){
                    res = contacto.res1 
                    chax = contacto.res1['chainname']
                }
            } 
            
            if(mutableChains.includes(contacto.res2['chainname'])){
                if(!mutableChains.includes(contacto.res1['chainname'])){
                    res = contacto.res2
                    chax = contacto.res2['chainname']
                }
            }

            //seleString = '@' + res.atomList.join(',');
            intermolecularcontactsArray.push(contacto);
        }
    })
    return intermolecularcontactsArray;
}





//Get the selector for the index of first atom in first chain
function getFirstAtomIndexes (){
    molStructure.structure.eachChain(function(cp){
       idxList.push( cp.atomOffset );
    });
    sele = "@" + idxList.join(",");
    return sele;
}

//Gets information on all NGL chains into a preety array that actually gives us concrete information.. geez
function getAllChains(struct){
    var chains = []
    struct.eachChain(function(cp){

        //Get First residue by 0based index using the structure's residueProxy
        proxy = struct.getResidueProxy(cp.residueOffset)
        firstRes = proxy.qualifiedName().split(/:(.*)/s)[0].substring(0,5)
        resno = proxy.resno

        chains.push({
            chainindex: cp.index,
            chainname:  cp.chainname,
            atomsSelector: "@"+cp.atomOffset+"-"+cp.atomEnd,
            atomCount: cp.atomCount,
            atomFirst: cp.atomOffset,
            atomEnd: cp.atomEnd,
            residueCount: cp.residueCount,
            residueInit: cp.residueOffset,
            residueEnd: cp.residueEnd,
            residueRealPDBposition: 0, //TODO - calculate this on the fly
            realResidueInit: 0,
            realResidueEnd: 0,
            firstResidueNameAndIndex: firstRes,
            resnum: resno
        })
    });
    return chains;
}


//Section 4, after loading NGL object & atom Indexes
//Populates components of the chain selector for a given molecular
function populateChainSelectorObjects(id="1"){
    //Build initial object HTML

    var chainselectid = "chainselector["+id+"]";
    var component = newSelectChain(chainselectid, id);
    var td = "#chainselectortd"+id;
    var ul = "#resindextd"+id;
    $(td).html(component);
    $(ul).html("");
}


//Populate HTML DOM object with chan selector values
//map = chain map from getAlLChains
//DymeObjectId = Name of each selectbox
function newSelectChain(DymeObjectId, moleculeobjectid){
    map = []
    map = getAllChains(molStructure.structure);
    var sel = $('<select>').appendTo('body');
    sel.append($("<option>").attr('value', "none").text("Add Chain.."));
    var alreadyshown = []
    map.forEach(function(chain){
       //MOD Feb 2023 - Show each chain only once in the list
       if(!alreadyshown.includes(chain.chainname)){
        sel.append($("<option>").attr('value', chain.chainname).text("Chain "+chain.chainname));
       }
       alreadyshown.push(chain.chainname)
    });

    sel.attr("onchange", "assignSelectChainToObject(this,"+moleculeobjectid+")");
    sel.attr("id", DymeObjectId);
    sel.attr("name", DymeObjectId);
    sel.attr("class", "form-control");
    
    //jquery object with HTML
    return sel;
}



//This is what we do when user selects a chain for any object in the screen
function assignSelectChainToObject (inp, objectid){
    //Add to UL list and remove from all selects
    
    if(inp.value !== "none"){
        console.log(inp.value)
        var ul = "#resindextd"+objectid;
        var chcontent;
        var element;
        
        map = getAllChains(molStructure.structure);
        element = ""
        map.forEach(function(chain){           
            //MOD Feb 2023 - Throw all fragments of the same chain into the molecular object
            if(chain.chainname === inp.value){
                chcontent = chain.firstResidueNameAndIndex; //First residue of the chain
                cname = chain.chainname; //Chain Name (From PDB file)
                current = chain.resnum
                if(parseInt(chain.residueCount, 10) < 2){
                    ena = "disabled"
                } else {
                    ena = ""
                }
                element += '<li class="float-start align-middle"><div class="w-5 d-inline-flex">'+cname+':'+chcontent+'</div> <div class="w-50 d-inline-flex"> <input type="text" name="chain'+chain.chainname+":"+current+'" id="chain'+chain.chainname+':'+current+'" value="'+current+'"  maxlength="4" placeholder="PDB Pos" class="form-control" '+ena+'> <button class="btn btn-xs btn-icon w-5 align-middle d-inline-flex" type="button" onclick="this.parentNode.parentNode.remove(this)"><i class="fa fa-times"></i></button></div></li>';
                
            }
         }); 
       //Add new element to list of chains, else user selected the first element
       $(ul).append(element); 
    }
}



//Paint chain buttons on the frame
var buttonsInFrame = []
var represeInFrame = []

function paintChainButtons(){
    var vpos = 0; //how many pixels to leave between buttons
    var reptype = "cartoon";
    map = getAllChains(molStructure.structure);
    map.forEach(function(chain){  
        vpos = vpos+60;    
        if(chain.residueCount === 1){
            reptype = "ball+stick";
        }

        var surfaceButton = createElement("input", {
            type: "button",
            value: "Chain "+chain.chainname+" ("+chain.residueCount+")"
        }, { top: vpos+"px", right: "12px" })

        surfaceButton.onmouseenter = function (){
            chainshower = molStructure.addRepresentation(reptype, {color: "red", sele: ":"+chain.chainname})
        }
        surfaceButton.onmouseout = function(){molStructure.removeRepresentation(chainshower)}

        addElement(surfaceButton)
    })
    
    
}
//Decorate Viewer with Buttons to identify Chains
function addElement (el) {
    Object.assign(el.style, {
      position: "absolute",
      zIndex: 10

    })
    molStructure.viewer.container.appendChild(el);
}


function createElement (name, properties, style) {
    var el = document.createElement(name)
    Object.assign(el, properties)
    Object.assign(el.style, style)
    return el
}






///////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////

// NEXTDYME2 STUFF
function removeControlButtons(){
    $("#step4viewport input").remove(); 
}


//2. Build molecular object arrays
function buildMolecularObjects(){
    Dyme_MolecularObjects = []
    //var form = $("#DYMEnames").serializeArray();
    var totalmolecules = $("#tablanames tr").length;
    console.log(totalmolecules)
    //IterateMolecular Objects
    for (let i = 1; i <= totalmolecules; i++) {
        var objectid = i //Molecular Object id
        var molname = $('input[name^="molname['+i+']"]').val() //Name of molecular object
        var chainsArray = []
        var mutabl = false

        //Add Residuemap to object
        $('#resindextd'+i+' li input').each(function(){ //Get each added chain
            var chain = $(this).attr('id').split(':')[0].substr(-1);
            if(typeof (chainsArray[chain] === 'undefined')){
                chainsArray[chain] = Dyme_Residuemap[chain];
            }
        })
        
        //getmutable if
        $('[id^=mutable]').each(function(k, ele){
            var t = parseInt($(ele).attr('id').match(/[0-9]+/));
            if($(ele).is(':checked') && t===i){
                mutabl = true
            }
        })
        


        //Get molecule object Color
        chain_color = rgb2hex($('#mol'+i).css("color")); //Converts RGB colors to Hex codes - gets RGB from whatever color the colorpicker has

        Dyme_MolecularObjects.push({
            objectid: objectid, //Id of the object (for DYME), in order of appearence
            objectname: molname, //Name given to the object
            chains:   chainsArray, //Array of the chains that belong to this object
            mutable: mutabl, //Boolean (whether this is a mutable object)
            object_color: chain_color,
            //parmedSelector: sel //selector
        })
    }    
}


var co;
//3. Build anchor selector Grid and paint in accordeon 2
function getIntermolecularAtoms(){
    //Create contact representation object
    var co = molStructure.addRepresentation("contact", {sele: "all and (not hydrogen)"})
    var mut_chas =[]

    //Calculate contacts from or towards Mutable chains
    Dyme_MolecularObjects.forEach(function(objeto){
        if(objeto.mutable){
            Object.entries(objeto.chains).forEach(function(cha){ //Por cada cadena mutable
                mut_chas.push(cha[0])
            })
        }
    })

    contacts_array = getContactsArray(co) // Gets which atoms have intermolecular interactions between mutable and non mutable chains
    molStructure.removeRepresentation(co) // Remove the dummy contact representation.. no longer needed (to see it at least)
    mutable_chains = mut_chas //Recreate the global variable holding which chains should be available to pick anchorpoints
    return getInterfaceContactArray(contacts_array, mut_chas);
}



//Recompute all representations in Canvas so we can apply the right colors of objects and the mutable candidates of the interface

function recomputeRepresentations(){
    //Remove all Current Representations
    molStructure.eachRepresentation(function(repr){
        molStructure.removeRepresentation(repr)
    })

    //Display each chain in its chosen color
    //Rebuild the proper representation for objects defined in the GUI
    Dyme_MolecularObjects.forEach(function(objeto){
        Object.entries(objeto.chains).forEach(function(cha){ //Por cada cadena mutable
            chainname = cha[0] 
            molStructure.addRepresentation("cartoon", {sele: ":"+chainname, color: objeto.object_color})
        })
    })

    //Display new stuff
    setTimeout(buildAnchorGrid,1000);
}


//Builds Residue Maps to PDB or whatever the user input was
function buildResidueMapTranslation(){
    Dyme_Residuemap = {}
    ele = []
    chains = []

    //Get molecular Objects chains.. calculate all residue indexes for all residues based on user input index
    //TODO - Calculate incrementals   
    struct = molStructure.structure;

    //Get all chains in the system. Just a simple copy of each.. ex A and B
    struct.eachChain(function(chain){
       if(!chains.includes(chain.chainname)){
        chains.push(chain.chainname)
       }
    })

    //For each chain
    chains.forEach(function(ch){
        ele = []
        struct.eachResidue(function(residue) {
            if(residue.chainname === ch){
                ele[residue.index] = {
                    name: residue.resname,
                    resno_NGL: residue.resno,
                    resno_PDB: residue.resno,
                    isanchor: false,
                    chain: ch,
                    mutable_into: {}
                } 
            }
        })
        //Fill array with all residues
        Dyme_Residuemap[ch] = ele
    })

    
    $("#DYMEnames input[id^=chain]").each(function(){
        chain = $(this).attr('id').split(':')[0].substr(-1)
        resno = $(this).attr('id').split(':')[1]
        realresno = $(this).val();
        index = parseInt(resno, 10)-1;
        cont = 0;
        
        Dyme_Residuemap[chain].forEach(function(res) {
            if(parseInt(res.resno_NGL,10) >= parseInt(resno,10)){
                //console.log(parseInt(realresno,10)+cont)
                res.resno_PDB = parseInt(realresno,10)+cont
                cont += 1
            }
        })
    })
}


//Toggles an Anchorgrid table
function toggleAnchorGrid(table){
    console.log(table)
    $("#"+table).toggle()
}

// 3.1 Get intermolecular contacts between Mutable objects and all others - render anchor selector grid from it
//Use the mutable_chains variable to render a grid per mutable chain
function buildAnchorGrid(){
    var intermolecular = getIntermolecularAtoms() //Get atoms with intermolecular contacts (again)
    //console.log(intermolecular)
    var chainname
    var resno
    var res
    var buttons = ""
    var table   = ""
     //build a residue proxy from the main structure

    //For each mutable chain
    $("#anchorpointgrids").html("");
    Dyme_MolecularObjects.forEach(function(objeto){
       
        if(objeto.mutable){
            Object.entries(objeto.chains).forEach(function(cha){ //Por cada cadena mutable
                chainname = cha[0]
                residues = cha[1]

                table = ""
                buttons = ""

               
                
                residues.forEach(function(resi) {
                    //console.log(i)
                    //proxy = molStructure.structure.getResidueProxy(i); // TODO check if you need to be chain specific here
                    resno = resi.resno_NGL
                    resnoPDB = resi.resno_PDB
                    res   = resi.name
                    resnoContact = 0;

                    color = "btn-outline-dark" //Regular residue.. not in contact list
                    //For each residue in contact group - Figure out which ones we paint orange on the grid
                    intermolecular.forEach(function (contact){                        
                            if(chainname === contact.res1.chainname && resno === contact.res1.resno){
                                color = "btn-warning" //Orange
                                a = objeto["chains"][chainname][resno-1] //DYME_MolecularObject
                                b = Dyme_Residuemap[chainname][resno-1]
                                a.isanchor = true
                                b.isanchor = true
                            } else if (chainname === contact.res2.chainname && resno === contact.res2.resno){
                                color = "btn-warning" //Orange
                                a = objeto["chains"][chainname][resno-1] //DYME_MolecularObject
                                b = Dyme_Residuemap[chainname][resno-1] //Dyme_ResidueMap
                                a.isanchor = true
                                b.isanchor = true
                            }         
                    }) 


                    if(color === "btn-warning"){
                        interfaceRepresentation.push({
                            res: chainname+resno,
                            selector: resno+' and :'+chainname,
                            rep1: molStructure.addRepresentation("surface", {sele: resno+' and :'+chainname, surfaceType: "vws", opacity: 0.1, color: "#FFAF7A"}),
                            rep2: molStructure.addRepresentation("line", {sele: resno+' and :'+chainname})
                        })
                    }

                    buttons += '<button type="button" id="'+chainname+resno+'" class="btn btn-xs '+color+'" value="'+resno+' and :'+chainname+'" onclick="gridOnClick(this)" onmouseleave="leave(this)" onmouseenter="enter(this)">'+res+resnoPDB+'</button>';
                })
                
                eyeopen = "<button class='btn btn-sm btn-icon ml-auto' type='button' onclick='toggleAnchorGrid(\"anchorpoints"+chainname+"\")'><i id='togglechain"+chainname+"' class='fa fa-eye'></i></button>"

                table = "<br /><div class='d-flex justify-content-between align-items-center'><h4>Mutable Object "+objeto.objectname+" - Chain :"+chainname+"</h4>"+eyeopen+"</div>"
                table += '<div class="btn-toolbar" id="anchorpoints'+chainname+'" role="toolbar" aria-label="Anchor Points for chain'+chainname+'"><div class="btn-group mr-2 flex-wrap" id="anchorpoints'+chainname+'_buttons" role="group" aria-label="Chain '+chainname+'">';
                table += buttons 
                table += '</div></div><hr class="my-4">'

                //Add table to Anchorpoint div
                $("#anchorpointgrids").append(table);
            })
        }
    })
}

//THIS BLOCK DISPLAYS AN ENTIRE RESIDUE WHEN A BUTTON OF THE GRID IS HOVERED
//ALSO HANDLES THE CLICK ACTION, WHICH ACTUALLY SETS THE RESIDUE AS PERMANENTLY SELECTED
showTransient = [];
//When mouse clicks on buttongrid
function gridOnClick(but){
    try {

        //Add or remove selected representations based on click status
        var selectedRes = document.getElementById(but.id).value;

        if(!interfaceRepresentation.some(e => e.res === but.id)){
            interfaceRepresentation.push({
                                        res: but.id,
                                        selector: selectedRes,
                                        rep1: molStructure.addRepresentation("surface", {sele: selectedRes, surfaceType: "vws", opacity: 0.1, color: "#FFAF7A"}),
                                        rep2: molStructure.addRepresentation("line", {sele: selectedRes})
            });

            //Run up the colors
            $("#"+but.id).removeClass("btn-outline-dark");
            $("#"+but.id).addClass("btn-warning");

            //Set anchor in Residuemap
            pos = parseInt(selectedRes.split(' and :')[0], 10) //Extract pos and cha from buttonvalue
            cha = selectedRes.split(' and :')[1] //Extract pos and cha from buttonvalue
            Dyme_Residuemap[cha][pos-1].isanchor = true; 
            console_log(pos+cha)

       } else {
            molStructure.eachRepresentation(function(a) {
               if(a.parameters.sele === selectedRes){
                molStructure.removeRepresentation(a)
                $("#"+but.id).removeClass("btn-warning");
                $("#"+but.id).addClass("btn-outline-dark");

                //Unset anchor in Residuemap
                pos = parseInt(selectedRes.split(' and :')[0], 10) //Extract pos and cha from buttonvalue
                cha = selectedRes.split(' and :')[1] //Extract pos and cha from buttonvalue. The -1 is equal to the array index, not the resindex
                Dyme_Residuemap[cha][pos-1].isanchor = false;     
               }
            })

            interfaceRepresentation.forEach(function(re, index, obj){
                if(re["res"] === but.id){
                    //console.log(re["res"])
                    //molStructure.removeRepresentation(re["rep1"])
                    //molStructure.removeRepresentation(re["rep2"])
                    //Delete representation from list
                    obj.splice(index, 1)
                    //Return to non selected
                    //$("#"+but.id).removeClass("btn-warning");
                    //$("#"+but.id).addClass("btn-outline-dark");
                }
            }) 
        }
        
    } catch (error) {
            
    }
}



//When Mouse enters button grid
function enter(but){
    try {
        var selectedRes = document.getElementById(but.id).value;
        showTransient.push(molStructure.addRepresentation("surface", {sele: selectedRes, surfaceType: "vws", opacity: 0.1, color: "#FFFFFF"}))
        showTransient.push(molStructure.addRepresentation(("line", {sele: selectedRes+" and not hydrogen"})))    
    } catch (error) {
        
    }
}

//When mouse leaves button grid
function leave(but){
    showTransient.forEach(function(cadauno) {
        molStructure.removeRepresentation(cadauno)
    })    
}




//When We want to find neighbors
function neighbors(residue_id_button, radius_around_angstroms){
    residue_id_button = "H23" //Not ready.. you must change this example
    radius_around_angstroms = 3; //whatever.. just to test

    var selector = ""
    var cha      = residue_id_button.charAt(0) 
    interfaceRepresentation.forEach(function(re){
            if(re["selector"] !== undefined){
                selector += re["selector"];
            }
    }) 

    target_sele = new NGL.Selection(selector);
    radius = 5;
    neigh_atoms = molStructure.structure.getAtomSetWithinSelection( target_sele, radius_around_angstroms );
    resi_atoms = molStructure.structure.getAtomSetWithinGroup( neigh_atoms );
    molStructure.addRepresentation("surface", {sele: resi_atoms.toSeleString()+" and :"+cha, colorValue: "#FFFFFF", multipleBond: false });        
    
}




//STEP4 - PIPELINE MUTAGENESIS CONTROL


//Show or hide residue matrix table in step 4
$('input:radio[id="inlineradio_mutagenesis"]').change(function(){
        //If all residues for all anchorpoints
        if (this.checked && this.value == 'mutagenesis_useall') {
            $("#tablemutagenesis").prop('hidden', true); 
        } else {
            $("#tablemutagenesis").prop('hidden', false); 
        }
});

//Build mutagenesis table for all anchorpoints 
function buildMutagenesisTable(){
    //Reset content of table
    $("#mutagenesis_table").html('');
    var isdisabled = "" //Adds the word "disabled" to a checkbox

    //Create anchorporint array
    Object.keys(Dyme_Residuemap).forEach(function(chain){
        Dyme_Residuemap[chain].forEach(function(residue){
            if(residue.isanchor){

                tabletd = '<td><label class="fw-bold">'+residue.name+residue.resno_PDB+'</label></td>'
                standard_residues.forEach(function(ele){
                    //Avoid Wildtype redundancies - disable the residue checkbox if it is the same wildtype residue
                    if(ele === to1[residue.name]){
                        isdisabled = "disabled"
                    } else {
                        isdisabled = ""
                    }
                    tabletd +=  '<td class="justify-content-evenly"><input class="form-check-input" type="checkbox" id="anchor['+(residue.resno_NGL-1)+']['+ele+']" '+isdisabled+'></td>'
                })

                //Add final column (group selector)
                tabletd += '<td><select name="residueGroup" class="" id="residueGroup" onchange="applySelectorGroup(this, \''+(residue.resno_NGL-1)+'\')">'
                tabletd += '<option value="0">Select..</option>'

                //Loads residue type arrays
                residuetypes.forEach(function(a) {
                    for (var key in a) {
                        tabletd += '<option value="'+key+'">'+key.charAt(0).toUpperCase() + key.slice(1);+'</option>';
                    }
                })
                
                tabletd += '</select></td>'

                //Append Row into residue table
                $("#mutagenesis_table").append("<tr id='mutagenesis_table_row_"+(residue.resno_NGL-1)+"'>"+tabletd+"</tr>");
            }
        })
    })
}

//Apply Selector group to anchor point residues
function applySelectorGroup(sele, anchorpoint){
    //Get elements of selected anchor point TR
    index      = $(sele).val();
    //Do nothing
    if(index === "0"){
        return false
    }

    collection = residuetypes[0][index];
    rescheck = ""
    //activate / deactivate checks
    $("#mutagenesis_table_row_"+anchorpoint).children().children().each(function(index, element){
        try {
            matches = element.id.match(/\[.*?\]/g);
            rescheck = matches[1].substring(2, 1);
        } catch {

        }

        if(collection.includes(rescheck)){
            if(!$("[id='"+element.id+"']").prop('disabled')){ //Only activate checks that are not disabled - see line 1448
             $("[id='"+element.id+"']").attr('checked', true);
            }
        } else {
            $("[id='"+element.id+"']").attr('checked', false);
        }
    })
}


















//STEP5 - CLUSTERING CONTROLS

function drawAnchorDivsDraggable(){
    var div= ""
    $("#anchordivs").empty()

    Object.keys(Dyme_Residuemap).forEach(function(chain){
        Dyme_Residuemap[chain].forEach(function(residue){
            if(residue.isanchor){
                div = '<div class="btn btn-warning draggable flex-left me-3" indexres="'+(residue.resno_NGL)+'" chain="'+chain+'">'+residue.name+residue.resno_PDB+'</div>'
                $("#anchordivs").append(div)
            }
        })
    })

    //Set draggable components
    $(".draggable").draggable({
        revert: true,
        helper: 'clone',
        start: function (event, ui) {
            $(this).fadeTo('fast', 0.5);
        },
        stop: function (event, ui) {
            $(this).fadeTo(0, 1);
        }
    });
}

function drawInitialClusters(){
    //Set droppable components
    $("#clusters").empty()
    
    $("#clusters").append('<label for="selectcluster1">Cluster 1</label><br /><select class="form-control droppable w-50 me-3 p-2" id="selectcluster1" multiple=""></select>')
    $("#clusters").append('<button type="button" onclick="dropfromcluster(1, this)" class="btn btn-xs btn-danger float-start">Drop Selected Anchor</button> <br />')
    $(".droppable").droppable({
        hoverClass: 'active',
        drop: function (event, ui) {
            //What to do when we drag ontop
            var isinlist = false
            $(this).find('option').each(function() {
                if($(this).text() === $(ui.draggable).text()){
                    isinlist = true;
                } 
            })

            if(!isinlist){
                let arr = $(this).append('<option value="'+$(ui.draggable).attr("indexres")+'">'+$(ui.draggable).text()+'</option>');
            }
            $(ui.helper).remove();
            calculateComplexity()
        },
    });
}

//Addcluster button
$("#addCluster").click(function(e){
    var matched = $("#clusters select")
    var nextname = matched.length+1;

    console.log("generating cluster "+nextname)
    $("#clusters").append('<label id="labelcluster'+nextname+'" for="selectcluster'+nextname+'">Cluster '+nextname+'</label><br /><select class="form-control droppable w-50 me-3 p-2" id="selectcluster'+nextname+'" multiple=""></select>')
    $("#clusters").append('<button type="button" id="dropcluster'+nextname+'" onclick="dropfromcluster('+nextname+', this)" class="btn btn-xs btn-danger float-start">Drop Selected Anchor</button>')
    $("#clusters").append('<button type="button" id="dropclustertot'+nextname+'" onclick="dropcluster('+nextname+', this)" class="btn btn-xs btn-dark float-start">Drop Cluster '+nextname+'</button><br />')
    $(".droppable").droppable({
        hoverClass: 'active',
        drop: function (event, ui) {
            //What to do when we drag ontop
            var isinlist = false
            $(this).find('option').each(function() {
                if($(this).text() === $(ui.draggable).text()){
                    isinlist = true;
                } 
            })

            if(!isinlist){
                let arr = $(this).append('<option value="'+$(ui.draggable).attr("indexres")+'">'+$(ui.draggable).text()+'</option>');
            }
            $(ui.helper).remove();
            calculateComplexity()
        },
    });
})

//ResetclustersButton
$("#resetAddCluster").click(function(e){
    $("#clusters").empty()
    drawAnchorDivsDraggable()
    resetComplexityTable()
    drawInitialClusters()
})

//Reset values of complecity table to 0
function resetComplexityTable(){
    $("#singlets").html("0")
    $("#singlets_time").html("0")
    $("#duplets").html("0")
    $("#duplets_time").html("0")
    $("#triplets").html("0")
    $("#triplets_time").html("0")
    $("#total_mutants").html("0")
    $("#total_tuntime").html("0")
}

//Calculate complexity
var residuesPerAnchor = [];
function calculateComplexity(){
    residuesPerAnchor = [];
    if($('input[id=inlineradio_mutagenesis]:checked').val() === "mutagenesis_choose"){
        //Count Checked residues in total
        if($("input[id^=anchor]:checked").length > 0){
            $("input[id^=anchor]:checked").each(function(index,element){
                matches = element.id.match(/\[.*?\]/g);
                anchor = matches[0].split('[').pop().split(']')[0];

                if(typeof residuesPerAnchor[anchor] === 'undefined') {
                    residuesPerAnchor[anchor] = 1
                } else {
                    residuesPerAnchor[anchor] += 1
                }
            })
        }
    } else {
        residuesPerAnchor["ALL"] = 20;
    }

    var cluster = 0
    var singlets = 0
    var duplets = []
    var triplets = []
    var numcluster = 0;

    //We have the matrix per anchor or a single element ALL meaning all 20.
    $(".droppable").each(function(index, cluster){
        //if cluster has elements
        if($(cluster).children().length > 0){
            //Singlets
            clusters = []

            duplets[numcluster] = 0
            triplets[numcluster] = 0

            //CHECK HOW TO FILL for every cluster
            $(cluster).children().each(function(ind, option){
                if(typeof residuesPerAnchor["ALL"] === 'undefined') {
                    an = $(option).val()-1
                    singlets += residuesPerAnchor[an]
                    clusters[ind]  = residuesPerAnchor[an]
                } else {
                    singlets += residuesPerAnchor["ALL"]
                    clusters[ind] = residuesPerAnchor["ALL"]
                }
            })

            //Combinatorial Duplets
            if($(cluster).children().length > 1){
                ap = k_combinations(clusters, 2)
                ap.forEach(function(e){
                   duplets[numcluster] += e.reduce((a, b) => a * b)
                })
            } 

            //Combinatorial Triplets
            if($(cluster).children().length > 2){
                ap = k_combinations(clusters, 3);
                ap.forEach(function(e){
                   triplets[numcluster] += e.reduce((a, b) => a * b)
                })

            } 

            numcluster += 1
           
        }
       
    })

    
    //triplets.reduce((a, b) => a + b)

    //Assuming 30 gpus.. probably more, some slower ones
    $("#singlets").html(singlets)
    $("#singlets_time").html(Math.round(((singlets*40)/60)/30,1)+" hours")

    $("#duplets").html(duplets.reduce((a, b) => a + b))
    $("#duplets_time").html(Math.round((((duplets.reduce((a, b) => a + b))*40)/60)/30,1)+" hours")

    $("#triplets").html(triplets.reduce((a, b) => a + b))
    $("#triplets_time").html(Math.round((((triplets.reduce((a, b) => a + b))*40)/60)/30,1)+" hours")

    $("#total_mutants").html(singlets+duplets.reduce((a, b) => a + b)+triplets.reduce((a, b) => a + b))
    $("#total_tuntime").html(Math.round((((singlets+duplets.reduce((a, b) => a + b)+triplets.reduce((a, b) => a + b))*40)/60)/30,1)+" hours")

}


//CLUSTERING - Make manual - Automatic for later
//NOT YET USED
function buildbuildClustersByDistance(){
    var struc = structureComponent.structure;
    var ap1 = struc.getAtomProxy();
    var ap2 = struc.getAtomProxy();
    var selection = new NGL.Selection ();

    selection.setString ("14 15", true);
    var atomIndices = struc.getAtomIndices (selection);

    // simple example, can make more complex by loop through all combinations of atom pairs in a bigger selection etc
    ap1.index = atomIndices[0];
    ap2.index = atomIndices[1];

    var distances = ap1.distanceTo(ap2);
}

function dropfromcluster(clu, ele){    
    $("#selectcluster"+clu+" option:selected").remove()
    calculateComplexity()
}

function dropcluster(clu, ele){
    $("#selectcluster"+clu).remove()
    $("#labelcluster"+clu).remove()
    $("#dropcluster"+clu).remove()
    $("#dropclustertot"+clu).remove()
    $("#clusters br").remove()
    calculateComplexity()
}



////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//GATHER ALL DATA AND SEND TO SERVER - SAVES PROJECT AND GETS READY TO EXECUTE DYME
function computeAllConfigsCheck(){

    //Build Curated config file
    finalAnchorpointsArray()
    finalAnalysisArray()
    finalClustersArray()
    finalSimulationParametersArray()
    finalInputFilesArray()
    finalMolecularObjectsArray()

    //Build Big mega array to send to server
    Dyme_Project = [] 

    Dyme_Project = {
        objects:  Dyme_MolecularObjects,
        analysis: Dyme_Analysis,
        clusters: Dyme_Clusters,
        inputs:   Dyme_Projectinputs,
        simulation: Dyme_Simulation,
        residuemap: Dyme_Residuemap
    }

    callApi("processNewProject","",Dyme_Project, true)
}


//FINALIZE - Molecular Objects
function finalMolecularObjectsArray(){
    proxy = molStructure.structure.chainProxy
    Dyme_MolecularObjects.forEach(function(obj){        
            arr = []
            Object.keys(obj.chains).forEach(function(key){
                arr.push({key})
            })
            obj.chains = arr        //TODO: This is not working. Try to pass chain string as an object and not an array?   
    })
}


//FINALIZE - GET ANCHORPOINTS
function finalAnchorpointsArray(){
    //Foreach mutable residue
    mutables = []
    if($('input[id=inlineradio_mutagenesis]:checked').val() === "mutagenesis_choose"){
        $("input[id^=anchor]:checked").each(function(index, element){
            matches = element.id.match(/\[.*?\]/g);
            anchor  = matches[0].split('[').pop().split(']')[0];
            mutable = matches[1].split('[').pop().split(']')[0];

            if(typeof mutables[anchor] === 'undefined') {
                mutables[anchor] = []
            } 
            //Add selected mutable to anchor list
            mutables[anchor].push(mutable)
        })
    } else {
        anchors.forEach(function(anch){
            if(typeof mutables[anch] === 'undefined') {
                mutables[anch] = []
            } 
            mutables[anch] = standard_residues
        })
    }

    //Foreach Anchorpoint
    Dyme_Anchorpoints = []
    Object.keys(Dyme_Residuemap).forEach(function(chain){
        Dyme_Residuemap[chain].forEach(function(residue){
            if(residue.isanchor){ 
                ind = residue.resno_NGL-1
                residue.mutable_into = mutables[ind] //Assign anchorpoint possible residues
            }
        })
    })
}

function togglePB(to){
        $("#igbcheck").toggle()
        $("#inpcheck").toggle()
}

//FINALIZE - GET SETTINGS ARRAY
function finalAnalysisArray(){
    Dyme_Analysis = []
    $("#DYMEsettings input:checkbox:checked").each(function() {
        Dyme_Analysis.push($(this).attr("id"))
    }) 
    //PEDRO 2024 OCT - Add GBSA or PBSA option
    $("#DYMEsettings input:radio:checked").each(function() {
        Dyme_Analysis.push($(this).attr("id"))
    }) 
}

function finalSimulationParametersArray(){
    Dyme_Simulation = {}
    $('#simulationOptions').serializeArray().forEach(function(k){
        Dyme_Simulation[k.name] = k.value
    })
}


function finalClustersArray(){
    Dyme_Clusters = []
    $('select[id^="selectcluster"]').each(function(){
        id = parseInt($(this).attr('id').slice(-1))
        temp = []
        $(this).find('option').each(function(name, val){
            temp.push(val.value)
        }) 
        Dyme_Clusters[id] = temp
    })   
}


function finalInputFilesArray(){
    Dyme_Projectinputs = {}
    temp = []
    $('#formStep1').serializeArray().forEach(function(k){
        Dyme_Projectinputs[k.name] = k.value.replace(/\\\//g, "/");
    })
    
    temp = []
    $("#leapSourcesContent").find("option").each(function(){
        temp.push($(this).val())
    })
    Dyme_Projectinputs['leapSourcesContent'] = {}
    Dyme_Projectinputs['leapSourcesContent'] = temp


    temp = []
    $("#leapSourcesListUploaded li").each(function(i,e){
        temp.push(e.innerText)
    })
    Dyme_Projectinputs['leapSourcesContentUploaded'] = {}
    Dyme_Projectinputs['leapSourcesContentUploaded'] = temp

    //ADD IGB VALUE - FEB 2024
    Dyme_Projectinputs['igb'] = $("#igb").val()
    Dyme_Projectinputs['inp'] = $("#inp").val()
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////