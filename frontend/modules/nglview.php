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

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
    <link rel="stylesheet" href="../css/ngl/font-awesome.min.css" />
    
    <link rel="stylesheet" href="../css/ngl/main.css" />
    <link rel="subresource" href="../css/ngl/light.css" />
    <link rel="subresource" href="../css/ngl/dark.css" />
    <link rel="stylesheet" id="theme" href="../css/ngl/dark.css">
</head>

<body>
    <!-- NGL -->
    <script src="../js/ngl/ngl.js"></script>

    <!-- UI -->
    <script src="../js/ngl/signals.min.js"></script>
    <script src="../js/ngl/tether.min.js"></script>
    <script src="../js/ngl/colorpicker.min.js"></script>
    <script src="../js/ngl/ui.js"></script>
    <script src="../js/ngl/ui.extra.js"></script>
    <script src="../js/ngl/ui.ngl.js"></script>
    <script src="../js/ngl/gui.js"></script>

    <script>
        NGL.cssDirectory = "../css/ngl";
        NGL.documentationUrl = "";
        NGL.examplesListUrl = "";
        NGL.examplesScriptUrl = "";

        test = "img/projects/3/mutants/1/outputs/water_traj.xtc"

        // Datasources
        NGL.DatasourceRegistry.add("data", new NGL.StaticDatasource(test));

        var stage;
        document.addEventListener("DOMContentLoaded", function (){
            stage = new NGL.Stage();
            NGL.StageWidget(stage);
           
            var load = NGL.getQuery("load");
            if(load) stage.loadFile(load, { defaultRepresentation: true });
           
            var script = NGL.getQuery("script");
            if(script) stage.loadScript("scripts/" + script + ".js");
        } );
    </script>

</body>
</html>