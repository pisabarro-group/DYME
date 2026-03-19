let residuemap = ""

project      = ""
residuemap   = ""
clusters     = ""
anchorpoints = ""

$( document ).ready(function() {
    getProjectData()
});

function getProjectData(mutantID = 0){
        //var id = { idproject: $("#idproject").val(), mutantID: mutantID}
        var id = { idproject: $("#idproject").val()}
        callApi("getAllProjectData","",id,true)
        callApi("getAnchorPoints","",id,true)
}


//Process Async response from callApi - All API responses are asynchronously sent here
function processResult(res){
    console.log("Got response from server API for "+res['action'])

    switch(res['action']) {
        //Render the current table of mutants   
        
        //Get projectData
        case 'fill_project_data':
            project    = res["response"]
            residuemap = project[0]['project']["residuemap"]
            clusters   = project[0]['project']["clusters"]
            objects    = project[0]['project']["objects"]
            //anchorpoints = project['anchors']
            renderAnchorPoints()
        break;

       

    }
}





function renderAnchorPoints(){
    var btn = ''
    Object.entries(residuemap).forEach(function(res){
        res[1].forEach(function(chain){
            if(chain !== null){
                if(chain["isanchor"]){
                    num     = chain["resno_PDB"]
                    resid   = chain["resno_NGL"]
                    origresname = to1[chain["name"]]
                    btn += '<button class="btn btn-orange btn-sm" onclick="focusOnAnchor('+resid+')">'+origresname+num+'</button> '
                }
            }
        })
    })   
    btn += "<br><span class='small text-muted'>Anchorpoints</span>"
    $("#anchorpointlist").html(btn)
}


function showLoading(){}