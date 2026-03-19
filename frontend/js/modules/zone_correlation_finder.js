console.log("I LOADED CORRELATION FINDER JS")

//Onload
$( document ).ready(function() {
    dataTable2 = new DataTable("#datatablesmutants", {sortable: true, scrollCollapse: true, pageLength: 100, select: {style: 'os'},paging: true, scrollY: '20vh', lengthChange: false, bFilter: false, bInfo: false})
})

matrixdata = {}
aimodel = {}
residuemap = ""
defaults = {}
dropdowns = {}
newmutantsarray = []
var intervalID 

origfiller_matrix = '<div><br /> </div><div><br /></div><div class="spinner-border" role="status"> </div> &nbsp; <br /><br /><div class="d-flex justify-content-center align-middle"><h5>Generating Correlation Matrix</h5></div>'
origfiller_ai = '<div><br /> </div><div><br /></div><div class="spinner-border" role="status"> </div> &nbsp;<br /><br /><div class="d-flex justify-content-center align-middle"><h5>Recalibrating Neural Network. Please be patient</h5></div><div class="log-box" id="neuralprogress"></div>'


//FUNCTIONS ENTRY POINTS
//Get Project Data
function getProjectData(){
    var id = { idproject: $("#idproject").val()}
    callApi("getProjectData","",id, true)
}

//
function checkUpdatesNeural(){
    var id = { idproject: $("#idproject").val()}
    callApi("getModelProgress","",id, true)
}

//CorrelationMatrix
function getCorrelationMatrix(regener=0){
        var id = {idproject: $("#idproject").val(), regenerate: regener}
        if(regener == 1) {
            $("#correlationmatrix").html(origfiller_matrix) 
        }
        callApi("getCorrelationMatrix","",id,true)
}

//AAI Modeller
function buildReturnAIModel(regener=0){
    var id = {idproject: $("#idproject").val(), regenerate: regener}
    if(regener == 1) {
        $("#neuralcontainer").html(origfiller_ai) 
    }
    callApi("buildReturnAIModel","",id,true)
}

//Get ResidueMAP
function getResidueMap(){
    var id = {idproject: $("#idproject").val()}
    callApi("getResidueMap","",id,true)
}



//Process Async response from callApi - All API responses are asynchronously sent here
function processResult(res){
    console.log("Got response from server API for "+res['action'])

    switch(res['action']) {
        
        case 'render_project':
            //Change page
            $("#titlepage").html(res["response"][0]["name"])
            path_to_project = res["response"][0]["project_folder"]
        break;

        case 'informProgressNeural':
            //Change page
            text = res['response']
            if(text.includes("Finished")){
                clearInterval(intervalID)
                id = $("#idproject").val()
                d = new Date();
                btn2    = '<button class="btn btn-primary" type="button" onclick="buildReturnAIModel(1)">Regenerate AI Model</button>'
                element = "<img src='"+"img/projects/"+id+"/outputs/predictive_model_map.png?"+d.getTime()+"' class='w-100'>"+btn2
                //Load here the MSE and Test set population number. Display after picture
                $("#neuralcontainer").html(element)
            } else{
                $("#neuralprogress").html(res["response"])
            }
        break;

        case 'renderModel_existing':
            id      = $("#idproject").val()
            d = new Date();
            btn2    = '<button class="btn btn-primary" type="button" onclick="buildReturnAIModel(1)">Regenerate AI Model</button>'
            element = "<img src='"+"img/projects/"+id+"/outputs/predictive_model_map.png?"+d.getTime()+"' class='w-100'>"+btn2
            //Load here the MSE and Test set population number. Display after picture
            $("#neuralcontainer").html(element)
        break;


        //Fetch Correlation matrix
        case 'render_matrix':
            component  = res['component']
            response   = res['response']
            paintMATRIX(component, response)
        break;

        //Rebuild Ai model and re train and display
        case 'renderModel':
            //component  = res['component']
            //response   = res['response']
            //paintMODEL(component, response)
            intervalID = setInterval(function(){
                checkUpdatesNeural()}
            , 1000)
        break;

        case 'residueMap':
            response   = res['response']
            residuemap = response["proj"][0]["residuemap"];
            renderAnchorPoints()
        break;

        default:
        break;
    }
}





// PAINTING FUNCTIONS
function paintMATRIX(component, matrix) {
    matrixdata = matrix
    image   = matrix.path_www
    numdiff = matrix.mutants
    d = new Date();
    console.log(matrix)
    console.log(numdiff)

    btn = '<button class="btn btn-primary" type="button" onclick="getCorrelationMatrix(1)">Regenerate Matrix</button>'
    $("#correlationmatrix").html("<img src='"+image+"?"+d.getTime()+"' class='w-100'><br>"+btn)
}

function paintMODEL(component, model) {
    aimodel = model
    console.log(aimodel)
    //$("#correlationmatrix").html("<img src='"+matrix+"' class='w-100'>")
}



//Handle Modal WdataTable2arnings
function showLoading(){
    
}

//Execute Entry Functions

getProjectData() //Load title, etc
getCorrelationMatrix(0) //Load Correlation Matrix
buildReturnAIModel(0)
getResidueMap()

//ANCHORPOINT RENDERING
function getopts(resselected, id){
    opt = ''
    standard_residues.forEach(function(res){
        if(res == resselected){
            sele = 'selected'
        } else{
            sele = ''
        }
        opt += '<option value="'+res+'" '+sele+'>'+res+'</option>>'
        dropdowns[id] = opt //Save the option list for every amino acid dropdown
    })
    return opt
}

function restoreDropdowns(){
    $("select").each(function( index ) {
        id = $(this).attr('id')
        $(this).empty()
        $(this).append(dropdowns[id]) //Populate the amino acid dropdown with its original dropdown options
    })   
}



function renderAnchorPoints(){
    var btn = ''
    btn += "<dl class='row'>"
    defaults = {}

    Object.entries(residuemap).forEach(function(res){
        res[1].forEach(function(chain){
            if(chain !== null){
                if(chain["isanchor"]){
                    num         = chain["resno_PDB"]
                    resid       = chain["resno_NGL"]
                    cha         = chain["chain"]
                    origresname = to1[chain["name"]]
                    btn += '<dt class="col-sm-3"><button type="button" class="btn btn-light" style="width: 78px !important;">'+origresname+num+'</button></dt>'
                    btn += '<dd class="col-sm-9"><select id="'+cha+":"+num+'">'+getopts(origresname, cha+":"+num)+'</select></dd>'
                    defaults[cha+":"+num] = origresname
                }
            }
        })
    })
    btn += '</dl>'
    $("#anchorpointlist").html(btn)
}


function getAnchorSelects(){
    newmutants = {}
    text = ""
    contchanges = 0
    $("select").each(function( index ) {
        id     = $(this).attr('id')
        val    = $(this).val()
        //console.log( $(this).attr('id') + ": " + $(this).val() + id.includes(val));
        if(defaults[id] != val){
            //console.log("Change on "+id)
            newmutants[id] = val
            text += '<div class="badge bg-primary text-white rounded-pill">'+id+":"+val+'</div>'
            contchanges++
        }   
    });
    
    
    if(contchanges > 0){
        newmutantsarray.push(newmutants)
        addMutant(1,text)
    } else {
        $('#staticBackdrop').modal('show');
    }
}


function addMutant(idm, nuevo){
    sel='<input class="form-check-input" type="checkbox" id="'+idm+'" name="'+idm+'" value="">'
    mt = [nuevo, "pending", ""]
    dataTable2.row.add(mt)
    dataTable2.columns.adjust()
    dataTable2.draw(false)

    //Restore dropdowns
    restoreDropdowns()
}
    
function testMutants(){

}
