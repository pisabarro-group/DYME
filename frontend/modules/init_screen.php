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
 * Repository: https://github.com/pguillem/DYME
 */
?>


<div id="layoutAuthentication_content">
    <main>
        <div class="container-xl px-4">
            <div class="row justify-content-center">

                

                <!-- Create Organization-->
                <div class="col-xl-5 col-lg-6 col-md-8 col-sm-11 mt-4">
                    <div class="card text-center h-100">
                        <div class="card-body px-5 pt-5 d-flex flex-column">
                            <div>
                                <div class="h3 text-primary">New Project</div>
                                <p class="text-muted mb-4">Start a new screening from scratch</p>
                            </div>
                            <div class="icons-org-create align-items-center mx-auto mt-auto">
                                <i class="icon-users" data-feather="file-plus"></i>
                                
                            </div>
                        </div>
                        <div class="card-footer bg-transparent px-5 py-4">
                        
                            <div class="small text-center"><a class="btn btn-block btn-primary" href="index?s=newproject"><i class="icon-users" data-feather="plus"></i>
                            Begin new Project</a></div>
                        </div>
                    </div>
                </div>

                
                <!-- Join Organization-->
                <div class="col-xl-5 col-lg-6 col-md-8 col-sm-11 mt-4">
                    <div class="card text-center h-100">
                        <div class="card-body px-5 pt-5 d-flex flex-column align-items-between">
                            <div>
                                <div class="h3 text-secondary">Open Existing Project</div>
                                <p class="text-muted mb-4">Continue working on an existing project</p>
                            </div>
                            <div class="icons-org-join align-items-center mx-auto">
                                
                                <i class="icon-arrow fas fa-long-arrow-alt-right"></i>
                                <i class="icon-users" data-feather="book-open"></i>
                            </div>
                        </div>
                        <div class="card-footer bg-transparent px-5 py-4">
                            <div class="small text-center"><a class="btn btn-block btn-secondary" href="index?s=listprojects"><i class="icon-arrow fas fa-long-arrow-alt-right"></i>
                            Go to Projects</a></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>
</div
