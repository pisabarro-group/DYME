console.log("I LOADED JOB CONTROL  JS")
var dataTable2 = ""
var mutants = ""
//Onload
$( document ).ready(function() {

    $('#staticBackdrop2').modal('show');

    getProjectData() //Load title, etc
    getProjectJobStatusTable() //Load Project Data

    dataTable2 = new DataTable("#datatablesjobs", {sortable: true, scrollCollapse: false, pageLength: 20,paging: true,  bFilter: true, bInfo: true,   order: [[1, 'asc']],
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
        {  },
        {  },
        {  },
        {  },
        {  }
    ], pageResize: true
    })

    // Add event listener for opening and closing details
    $("#datatablesjobs").on('click', 'td.dt-control', function (e) {
        let tr = e.target.closest('tr');
        let row = dataTable2.row(tr);
       
        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
        }
        else {
            // Open this row
            row.child(format(row.data()[1])).show();
        }
    });
})

//FUNCTIONS ENTRY POINTS
//Get Project Data
function getProjectData(){
    var id = { idproject: $("#idproject").val()}
    callApi("getProjectData","",id, true)
}

//
function getProjectJobStatusTable(){
    var id = { idproject: $("#idproject").val()}
    callApi("getProjectJobs","",id, true)
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

        case 'render_jobs_table':
            //Change page
            text = res['response']
            renderJobs(text)
            setTimeout(function(){
                $('#staticBackdrop2').modal('hide');
            }, 1000);
            
        break;

        default:
        break;
    }
}





//Page Functions
function renderJobs(mut) {
    mutants = mut
    //Clear

    dtcontrol = {
        className: 'dt-control',
        orderable: false,
        data: null,
        defaultContent: ''
    }

    dtcontrol = '<class="dt-control" orderable="false" data="" defaultContent=""></>'

    mutants.forEach(function(mutant){
        
        mt = [, mutant.mutantID, mutant.combination, mutant.status, mutant.status_vars.md_date_start, mutant.status_vars.md_elapsed_time, mutant.status_vars.md_remaining_time, mutant.status_vars.md_progress_percentage, ""]
        dataTable2.row.add(mt)
    })

    dataTable2.columns.adjust()
    dataTable2.draw(false)
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

function showLoading(){

}

// Formatting function for row details - modify as you need
function format(d) {
    // `d` is the original data object for the row
    info = mutants[d]
    return (
        '<dl>' +
        '<dt>Full name:</dt>' +
        '<dd>' +
        d.name +
        '</dd>' +
        '<dt>Extension number:</dt>' +
        '<dd>' +
        d.extn +
        '</dd>' +
        '<dt>Extra info:</dt>' +
        '<dd>And any further details here (images etc)...</dd>' +
        '</dl>'
    );
}