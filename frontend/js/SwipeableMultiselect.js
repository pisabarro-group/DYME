//PEDRO GUILLEM - TU DRESDEN - 2023
// This module controls display of the interface energy explorer.

(function ($) {

    var getValues = function (actives) {
        var values = [];
        actives.each(function () {
            values.push(this.childNodes[0].value);
        });
        return values;
    };

    var getValue = function (actives) {
        return actives[0].childNodes[0].value;
    };

    var setValue = function (labels, val) {
        labels.each(function () {
            if (val == this.childNodes[0].value)
                $(this).addClass('active');
        });
    };

    var setValues = function (labels, val) {
        labels.each(function () {
            for (var v of val) {
                if (v == this.childNodes[0].value)
                    $(this).addClass('active');
            }
        });
    };

    var methods = {
        Init: function (options, mutantID) {
            // Structure of values {}
            var seqvalues = options.values;
            var optsHtmlString = "";
            var index = 0;
            var accumenergy = 0
            var wtEnergies = [] //This is the energies of the wildtype
            var wtEnergies_noindex = []
            var stdstring = ""
            var segment = options.segment
            
            //Accumulate energy columns per position (to calculate percentage of gain/loss mainly)
            position_arrays = []
            Object.keys(seqvalues).forEach(function(ele){
                mutantID = ele
                valores = seqvalues[String(ele)]
                values = valores[segment]
                console.log(valores)
                for (var opt of values) { 
                    energ = opt.energy;
                    pos_real = opt.posreal;
                    pos = opt.number;

                    if(typeof position_arrays[pos] === 'undefined'){
                        position_arrays[pos] = []
                    }
                    position_arrays[pos].push(energ)
                }
            })

            //console.log(position_arrays)
            //Paint each position
            Object.keys(seqvalues).forEach(function(ele){
                mutantID = ele
                valores = seqvalues[String(ele)]
                                    
                //Ligand
                values = valores[segment]
                
                optsHtmlString = "";
                index = 1;
                show = Array.from({length:100}, (_, i) => (i + 1) * 5); // Generate the first 100 multiples of 5 (for top label bar)
                show.unshift(1); //Add number 1
                accumenergy = 0

                en = [] // These are the energies of the current mutant being read
                for (var opt of values) {                        
                    energ = opt.energy;
                    combi = opt.type;

                    accumenergy += energ;
                    en.push(energ)
                    //Accumulate energies of wildtype only in a separate array (to compare against later)
                    if(mutantID == 1){
                        pos = opt.number;
                        if(typeof wtEnergies[pos] === 'undefined'){
                            wtEnergies[pos] = 0
                            wtEnergies_noindex.push(energ)
                        }
                        wtEnergies[pos] = energ
                        sortable = ""
                        addpad = 'padding-top: 15px; padding-bottom: 10px;'
                    } else {
                        sortable = "sortable"
                        addpad = ''
                    }
                }
                //console.log(wtEnergies)
                //console.log(position_arrays)
                optsHtmlString = "<div class=\"row d-flex "+sortable+"\" data-index=\""+(Math.round(accumenergy * 100) / 100)+"\"><div class=\"col-sm-1 d-inline-block position-relative\"><h6 class=\"fixed px-1 py-2\">"+mutantID+" ("+combi+")"+"</h6></div><div class=\"col-sm d-inline-block\"> <ul class=\"list-group list-group-horizontal-sm \" style=\""+addpad+"\" id=\"mutant" + mutantID + "\" data-toggle=\"buttons\">"
                
               
                for (var opt of values) {
                        res = opt.residue;
                        pos = opt.number;
                        pos_real = opt.posreal;
                        energ = opt.energy;
                        mutated = opt.mutated;
                        three = opt.three;
                        //If wildtype
                        if(mutated == 1){
                            st = "custom-seqmut"
                        } else { 
                            st = ""  
                        }

                        if(res != null){
                            //colbut = perc2color(energ, en)
                            switch(seqMethod){                            
                                case 'selfMutant':
                                    colbut = perc2colorA(accumenergy, energ, en) // get color for this residue (selfMutant)
                                break;
                                case "gainLoss":
                                    if(mutantID == 1){
                                        colbut = perc2colorA(accumenergy, energ, en) // get color for this residue (selfMutant)
                                    } else {
                                        colbut = perc2colorB(pos, energ, wtEnergies, position_arrays, wtEnergies_noindex) // get color for this residue (gain/loss)
                                    }
                                break;
                                case "stdDev":
                                    energ = opt.std
                                    colbut = perc2colorC(energ) // get color for this residue
                                    stdstring = "+/- "
                                break;
                            }

                            if((show.includes(parseInt(pos, 10))) && (mutantID == 1)){
                                //show upper guide residue number on first row every 5 residues
                                console.log("Printing "+pos)
                                label = '<label class="position-absolute start-50 translate-middle" style="top: -8px;" for="'+mutantID+"_"+pos+'">'+pos+'</label>'
                                //label = ""  
                                
                            } else {
                                label = ""
                                
                            }
                            if(res == "[")
                                substitute = "ACE"
                            else if(res == "]")
                                substitute = "NHE"
                            else
                            substitute = three

                            tool = substitute+pos+": "+stdstring+energ.toFixed(2)+" kcal/mol";
                            optsHtmlString += "<br /><li class=\"multiselect-option "+st+" custom-seqwidth list-group-item py-2 px-1 btn btn-sm btn-primary\" style=\"background-color: "+colbut+"\" data-bs-toggle=\"tooltip\" data-bs-placement=\"bottom\" title=\""+tool+"\" energy=\""+energ+"\" id=\""+mutantID+"_"+pos+"\">"+label+res+"</li>";
                            
                        }
                        index++;
                }
                //Removed value of accumulated energy...
                //+(Math.round(accumenergy * 100) / 100)+--------------------------------here                    
                optsHtmlString += "</div><div class=\"col-sm-1 d-inline-block\" id=\"\">"+"</div></div>"
                    
                $("#sequenceHolder").append(optsHtmlString);
        
                var mousedownOn = {
                        el: null
                    };
        
                $(document)
                        .mouseup(function () {
                            mousedownOn.el = null;
                        });
        
                $("#mutant" + mutantID + " .multiselect-option")
                        .mousedown(function () {
                            var $this = $(this);
                            mousedownOn.el = $(this);
                            $this.button('toggle');
                        })
                        .mouseenter(function () {
                            var $this = $(this);
                            if (mousedownOn.el != null && $this.hasClass('active') != mousedownOn.el.hasClass('active')) {
                                $this.button('toggle', true);
                            }
                        })
                        .click(function (e) {
                            e.preventDefault();
                            return false;
                        });
                    
            })

           
        },
        GetSelectedValue: function() { //$("#platform-swipeable").swipeableMultiselect("GetSelectedValue");
            var $this = $(this);
            var actives = $this.find("li.active");
            var result = 0;
            if (actives.length > 0) {
                if (swipeableType == "radio") {
                    result = getValue(actives);
                }
            }
            return result;
        }, 
        SetActive: function (val) {
            var $this = $(this);
            var actives = $this.find("li.active");

            actives.each(function () {
                $(this).removeClass('active');
            });

            var labels = $this.find("li");
            
            var swipeableType = labels[0].childNodes[0].type;
            if (swipeableType == "checkbox") {
                if (val.constructor !== Array) {
                    $.error("Error! You are trying to call SetActive function passing only one value but the control is configured to accept multiple values. Please retry passing an Array of values.");
                }
                else {
                    setValues(labels, val);
                }
            }
            if (swipeableType == "radio") {

                if (val.constructor === Array) {
                    $.error("Error! You are trying to call SetActive function passing and Array but the control is configured to accept only one value. Please retry passing only one value.");
                }
                else {
                    setValue(labels, val);
                }
            }
        }
    };

    $.fn.swipeableMultiselect = function (methodOrOptions) {
        if (methods[methodOrOptions]) {
            return methods[methodOrOptions].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof methodOrOptions === 'object' || !methodOrOptions) {
            return methods.Init.apply(this, arguments);
        } else {
            $.error('Method ' + methodOrOptions + ' does not exist on jQuery.swipeableMultiselect');
        }
    };


})(jQuery);