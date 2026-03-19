// A $( document ).ready() block.
$( document ).ready(function() {
    callApi("getExistingProjects","","",false)
});


function deleteProject(idp){
    if(confirm("Are you sure you want to delete Project "+idp+" and all its files?. This operation can't be undone")){
        alert("deleting")
        var id = { idproject: idp}
        callApi("deleteProjectTree","",id, true)
    }
}

function printProject(proj){   
    
    var percent = proj['status']['percentage']
    var id      = proj['id']
    var stage1 = proj['status']['stage1']
    var stage2 = proj['status']['stage2']

    var processing  = proj['status']['processing']
    var estimated   = proj['status']['estimated']
    var complete    = proj['status']['complete']
    var in_process  = proj['status']['in_process']
    var total       = proj['mutants']
    var left = total-complete;
    var progressname = "progress"+proj['id'];
    
    //Progress Bar Color (... not too elegant)
    bg = "bg-red"
    if(percent >= 15){
        bg = "bg-orange"
    } 
    
    if(percent >= 25){
        bg = "bg-yellow"
    } 
    
    if(percent >= 35){
        bg = "bg-green"
    } 
    
    if(percent >= 45){
        bg = "bg-teal"
    } 
    
    if(percent >= 55){
        bg = "bg-cyan"
    } 
    
    if(percent >= 80){
        bg = "bg-blue"
    }

    //Handle lower messages depending on percentage.. also controls stripped progress bar
    leftover = ""
    if(percent == 100){
        percent_sign = "Complete!"
        type = "progress-bar"
    } else {
        percent_sign = percent+" %"
        type = "progress-bar-striped"
        if(percent > 0){
            if(processing > 0){
                spin = '<div class="spinner-grow spinner-grow-sm text-primary" role="status"></div>'
            } else{
                spin = ""
            }
            leftover = spin+" "+left+" mutants pending ("+processing+" running)"
        }
    }


    //Handle Timeline 
    step1="active"
    step2=step3=step4 = "";
    
    if (percent > 0) {
        step1 = "active";
        step2 = "";
        step3 = "";
    }

    if (complete > 0) {
        step1 = "";
        step2 = "active";
        step3 = "";
    }

    if (complete == total) {
        step1 = "";
        step2 = "";
        step3 = "";
        step4 = "active";
    }

    //Handle Button Open / Close
    openbutton = ""
    openbuttonclass = "btn-success"
    openbuttonclassred = "btn-outline-red "
    if (complete == 0) {
        openbutton = 'aria-disabled="true"'
        openbuttonclass = 'btn-light disabled'
        //openbuttonclassred = 'btn-light disabled'
    }
  

    return `
    <div class="card col-md-12">
     <div class="card-body p-3">
            <div class="d-flex">
                <!--Icon here-->
                <div class="ms-3 col-md-2 ">
                    <div class="badge bg-primary fs-4 text-wrap" >
                        #${id} - ${proj["name"]}
                    </div><br /><br />
                    <div class="small">Created: ${proj["date"]}</div> 
                    <div class="small">Mutants: ${proj["mutants"]}</div> 
                    <div class="small">Clusters: ${proj["clusters"]}</div> 
                    <div class="small">Anchors: ${proj["anchors"]}</div>                        
                </div> 

                <!-- Four Step Example-->
                <div class="mb-5 col-md-7">
                
                    <div class="step step-green">
                        <div class="step-item ${step1}">
                            <a class="step-item-link" href="#!">Preparing Inputs</a>
                        </div>
                        <div class="step-item ${step2}">
                            <a class="step-item-link" href="#!">Simulating/Scavenging</a>
                        </div>
                        <div class="step-item ${step3}">
                            <a class="step-item-link" href="#!">Learning</a>
                        </div>
                        <div class="step-item ${step4}">
                            <a class="step-item-link" href="#!" tabindex="-1" aria-disabled="true">Done</a>
                        </div>
                    </div>
                

                    <!-- Progress Bars -->
                    <div>
                        <div class="progress fs-4 fw-bold" style="height: 32px;">
                            <div id='${progressname}' class="progress-bar ${type} progress-bar-animated ${bg}" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"> 
                            ${percent_sign}     
                            </div>
                        </div>
                        ${estimated} <br>
                        ${leftover}
                    </div>


                </div>    

                <!-- Action Button-->
                <div class="ms-3 justify-content-center col-md-3 align-middle ">
                    <a class="btn ${openbuttonclass}" href="index.php?s=mainproject&id=${proj["id"]}&zone=exploration_mutant" ${openbutton} role="button" >Open Workspace</a>
                    <button class="btn ${openbuttonclassred}" onclick="deleteProject(${proj["id"]})" type="button" ${openbutton} ><i class="fas fa-trash"></i>
                    </button>
                </div>
                

            </div>    
     </div>
    </div>
    `;
}


//Shows loading overlay modal
function showLoading(){
    //alert("loading")
}

var pr = ""
function processResult(res){
    switch(res.action){
        case "render_projects":
           var texto = ""
           var wait = 100
           res.response.forEach(function (pro) {
                texto += printProject(pro)
                console.log(pro)
                wait +=100
                setTimeout(function() {
                    var progressname = "progress"+pro['id'];
                    var percentage   = pro['status']['percentage'];
                    var $progressBar = $('#'+progressname);
                    console.log("yes")
                    $progressBar.css('width', percentage+'%');
                    $progressBar.prop('aria-valuenow', percentage);
                }, wait);
           });

           $("#"+res.component).html(texto)
           
           
        break;

        case "delete_project":
           alert("Project tree has been deleted")
           window.location.reload();
        break;
    }
}   