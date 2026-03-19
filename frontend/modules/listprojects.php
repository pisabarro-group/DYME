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
?>

<main>
<header class="page-header page-header-dark bg-gradient-primary-to-secondary pb-10">
    <div class="container-fluid px-4">
        <div class="page-header-content pt-4">
            <div class="row align-items-center justify-content-between">
                <div class="col-auto mt-4">
                    <h1 class="page-header-title">
                        <div class="page-header-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-arrow-right-circle"><circle cx="12" cy="12" r="10"></circle><polyline points="12 16 16 12 12 8"></polyline><line x1="8" y1="12" x2="16" y2="12"></line></svg></div>
                        Workspace Selector
                    </h1>
                    <div class="page-header-subtitle">
                     Select an existing project to open its workspace<br>
                    </div>
                </div>
            </div>
        </div>
    </div>
</header>


<!-- A single DIV table to display the existing projects -->


<div class="container mb-4 px-8 mt-n10">
    <div class="card">
            <div class="card-header">Existing Projects</div>
            <div class="card-body px-0" id='projectlist'>
                <!-- List of projects-->
                <div class="d-flex align-items-center justify-content-between px-4">
                    <div class="spinner-border" role="status"> </div> 
                    <div class="d-flex justify-content-center align-middle"><h5>Loading Project List</h5></div>
                    &nbsp;<br /><br />
                </div>
                <hr>    
            </div>
    </div>
</div>
</main>
