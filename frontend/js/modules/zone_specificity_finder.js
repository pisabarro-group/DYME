console.log("I LOADED SPECIFICITY FINDER JS")
//Globals for this zone
var dataTable2 = ""



//Onload
$( document ).ready(function() {

    //Execute Entry Functions
    getProjectData() //Load title, etc
    getProjectList()

    //Prepare Datatable
    dataTable2 = new DataTable("#projectmatchtable", {sortable: true, scrollCollapse: true, pageLength: 100, select: {style: 'os'},paging: false, scrollY: '60vh', lengthChange: false, bFilter: false, bInfo: false, order: [2, 'asc']})
    
    $('#datatablesmutants').on('dblclick','tr',function(e){
        let rowID = dataTable2.row(this).data()[0]
        dataTable2.rows(this).select()
        alert("clicked row "+rowID)
        //loadMutantDetail(rowID) //Fills Right panel with single mutant info
    })
})


//FUNCTIONS ENTRY POINTS
//Get Project Data
function getProjectData(){
    var id = { idproject: $("#idproject").val()}
    callApi("getProjectData","",id, true)
}
//Get Project List
function getProjectList(){
    var id = { idproject: $("#idproject").val()}
    callApi("getProjectList","",id, true)
}

//Compare against project
function comparewith(idp){
    var id   = $("#idproject").val()
    var comp = {idorig: id, idcomp: idp}
    callApi("compareMutants","",comp, true) //TEST FIRST
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

        case 'renderDropdown':
            //Change page
            renderDropdown(res["response"])
        break;

        case 'renderMatchTable':
            //Change page
            renderTable(res["response"], res["component"])
        break;

        case 'renderError':
            error = res["response"]
            error = error["error"]
            $("#errorMessage").html(error)
            showAlert("Warning!",error)
        break;

        default:
        break;
    }
}


//Must Exist in every JS section file

function renderDropdown(data){
    projects = data.listelements

    Object.entries(projects).forEach(([key, value]) => {
        console.log(key)
        pname = value['name']
        console.log(value['seq'])
        $("#projectoptions").html('<a class="dropdown-item" onclick="comparewith('+key+')"> Project '+key+' ('+pname+')'+'</a>')
    });
}

function renderTable(response, component){

    //Clear Table
    dataTable2.clear()
    mutants    = response["matrix"]
    residuemap_target = response["residuemap_target"]
    residuemap_compar = response["residuemap_compar"]

    console.log(mutants)

    Object.entries(mutants).forEach(function(mut){
        if(isNumeric(mut[0])){
           id = mut[0]
           line = mut[1]
           console.log(line)
           //Content

        //Targetmutations
        tarmuts = ""
        Object.keys(line.target_mutations).forEach(key => {
            chain   = key.split(":")[0]
            pos     = key.split(":")[1]
            mutated = line.target_mutations[key]
            pdbElem = residuemap_target[chain][pos-1]["resno_PDB"]
            origRes = to1[residuemap_target[chain][pos-1]["name"]]
            tarmuts += '<div class="badge bg-primary text-white rounded-pill">'+origRes+":"+pdbElem+":"+mutated+'</div>'
        });

        comparmuts = ""
        Object.keys(line.compar_mutations).forEach(key => {
            chain   = key.split(":")[0]
            pos     = key.split(":")[1]
            mutated = line.compar_mutations[key]
            pdbElem = residuemap_compar[chain][pos-1]["resno_PDB"]
            origRes = to1[residuemap_compar[chain][pos-1]["name"]]
            comparmuts += '<div class="badge bg-primary text-white rounded-pill">'+origRes+":"+pdbElem+":"+mutated+'</div>'
        });
        
        //Comparedmutations
           console.log(line.compar_mutations)
           
           mt = [line.target_id_mutant, tarmuts, Math.round(line.target_energy * 10)/10,Math.round(line.difference * 10)/10,Math.round(line.compar_energy*10)/10,comparmuts,line.compar_id_mutant]
           dataTable2.row.add(mt)

        } else{
           id = mut[0]
           line = mut[1]
           switch(id){
                case "target_name":
                    $("#targetname").html("Mutant id. "+line)
                break;
                case "compar_name":
                    $("#comparname").html("Mutant id. "+line)
                break;
                case "target_wt_energy":
                    $("#t_wtenergy").html(Math.round(line * 10)/10)
                break;
                case "compar_wt_energy":
                    $("#c_wtenergy").html(Math.round(line * 10)/10)
                break;
           }
        }
    })
    $("#containerTable").removeClass("invisible")
    $("#containerTable_hide").remove()
    
    dataTable2.columns.adjust()
    dataTable2.draw(false)
    
}


function showLoading(){

}

function isNumeric(str) {
    if (typeof str != "string") return false // we only process strings!  
    return !isNaN(str) && // use type coercion to parse the _entirety_ of the string (`parseFloat` alone does not do this)...
           !isNaN(parseFloat(str)) // ...and ensure strings of whitespace fail
  }