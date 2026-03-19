//SYSTEM VARIABLE HANDLING
//AJAX REQUEST API HANDLING

//This function executes arbitraty API calls to WSGI (Ajax)
//If form exists.. fill form, else, just fill args
function callApi(remote_method="", form="", args, forcepost=false){

    //API Key
    //Include in the headers like a proper webapp.. not important for now


    if(remote_method == ""){
        showAlert("ERROR: Wrong Method called")
        return false
    }


    //Build Data
    if(form != ""){
        formData = new FormData($(form)[0]);
        typestr = "POST"
    } else {
        formData = JSON.stringify(args);
        typestr = "GET"
    }

    if(forcepost){
        typestr = "POST"
    }

    // Build URL
    uri = apiUrl+remote_method;

    //Send Ajax Request
    $.ajax({   
        type: typestr,
        url: uri,
        async: true,
        cache: false,
        data: formData,
        processData: false,
        contentType: false,
        dataType: "json",

        //Before Action
        beforeSend: function (result){
            showLoading(result)
        },
        //During Action

        //Success Action
        success: function (result){
            processResult(result)
        },
        //Failure Action   
        error: function (error){
            alert("error")
        }
     }); 
}

//EACH section's include js should contain showLoading, processResult and beforeSend Functions

//GUI FUNCTIONS HANDLING

//Wizzard-PDBFixer-Params handling


//Shows Modal box with message
//--------------------------------------
function showAlert(title,message, modal="#wizzardModal"){
//--------------------------------------
    $("#errorTitle").html(title);
    $("#errorMessage").html(message);
    $(modal).modal('show'); 
}


function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }

//2025, it was a bit inconveniento to use random colors... too often a similar would pop.
// not good for discerning mutants. This is a list of 19 discimilar colors. Only generate random after the first 20 have been used up.
function getRandomColor2(size){
    //Start with grey for wildtype always
    var palette = ['#a9a9a9','#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabed4', '#469990', '#dcbeff', '#9A6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075'];
    return palette[size];
  }

//Converts any RGB color to HEX
const rgb2hex = (rgb) => `#${rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/).slice(1).map(n => parseInt(n, 10).toString(16).padStart(2, '0')).join('')}`

//Convert HEX to RGBA
function hexToRgbA(hex, opacity){
    var c;
    if(/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)){
        c= hex.substring(1).split('');
        if(c.length== 3){
            c= [c[0], c[0], c[1], c[1], c[2], c[2]];
        }
        c= '0x'+c.join('');
        return 'rgba('+[(c>>16)&255, (c>>8)&255, c&255].join(',')+','+opacity+')';
    }
    throw new Error('Bad Hex');
}

//Comvert RGBA to HEX
function rgba2hex(rgba, forceRemoveAlpha = false) {
    return "#" + rgba.replace(/^rgba?\(|\s+|\)$/g, '') // Get's rgba / rgb string values
      .split(',') // splits them at ","
      .filter((string, index) => !forceRemoveAlpha || index !== 3)
      .map(string => parseFloat(string)) // Converts them to numbers
      .map((number, index) => index === 3 ? Math.round(number * 255) : number) // Converts alpha to 255 number
      .map(number => number.toString(16)) // Converts numbers to hex
      .map(string => string.length === 1 ? "0" + string : string) // Adds 0 when length of one number is 1
      .join("") // Puts the array to togehter to a string
  }




//Green
var green = {
    red: 26, green: 211, blue: 41
  };
//
var red = {
    red: 249, green: 80, blue: 80
  };

  //white
var white = {
    red: 255, green: 255, blue: 255
  };


//Creates 3 color gradient with fade percentage
// Gradient Function
function colorGradient(fadeFraction, rgbColor1, rgbColor2) {
    //console.log('>> fade: ', fadeFraction)
    var color1 = rgbColor1;
    var color2 = rgbColor2;
    var fade = fadeFraction;
    if (fade < 0.3){
        fade = 0.3;
    }

    var diffRed = color2.red - color1.red;
    var diffGreen = color2.green - color1.green;
    var diffBlue = color2.blue - color1.blue;
    var gradient = {
      red: parseInt(Math.floor(color1.red + (diffRed * fade)), 10),
      green: parseInt(Math.floor(color1.green + (diffGreen * fade)), 10),
      blue: parseInt(Math.floor(color1.blue + (diffBlue * fade)), 10),
    };
    return 'rgba(' + gradient.red + ',' + gradient.green + ',' + gradient.blue + ', '+fade+')';
}


//Computes Color gradients for mutant within itself - used by seqExplorer
function perc2colorA(totalE, valueE, en) {
    //Red, Gree, Blue
    var left = [108,199,249]
    var center = [255,255,255]
    var right = [255,197,197]
    var max = Math.max.apply(Math, en)
    var min = Math.min.apply(Math, en)
   
    //left
    if(valueE < 0){
        perc = Math.abs(valueE)/Math.abs(min);
        r = center[0]-((center[0]-left[0])*perc)
        g = center[1]-((center[1]-left[1])*perc)
        b = center[2]-((center[2]-left[2])*perc)
    } else if(valueE == 0){
        r = center[0]
        g = center[1]
        b = center[2]
    } else if (valueE > 0){
        perc = Math.abs(valueE)/Math.abs(max);
        r = center[0]-((center[0]-right[0])*perc)
        g = center[1]-((center[1]-right[1])*perc)
        b = center[2]-((center[2]-right[2])*perc)
        
    }
   
    alpha = Math.round(perc*100)
    //console.log(alpha)
    //var h = r * 0x10000 + g * 0x100 + b * 0x1;
    //return '#' + ('000000' + h.toString(16)).slice(-6);
    return 'rgba('+r+','+g+','+b+','+alpha+')';
}





//Computes Color gradients depending on gain/loss with respect to wildtype - used by seqExplorer
// This gradient goes from red to green, via white. Red for worse and green for better
function perc2colorB(position, valueE, wtEnergies, pos_arrays, weEnergNoIndex) {
    //Red, Gree, Blue
    var left = [255,110,110]
    var center = [255,255,255]
    var right = [102,210,82]
    var wtene = wtEnergies[position]

    //Min and max of column for position (changes with each sequence added)
    var max = Math.max.apply(Math, pos_arrays[position]);
    var min = Math.min.apply(Math, pos_arrays[position]);
    
    //Min and max of entire series

    var max_s = Math.abs(Math.max.apply(Math, weEnergNoIndex))
    var min_s = Math.abs(Math.min.apply(Math, weEnergNoIndex))
    var range = max_s+min_s
    var alpha = convertRange(Math.abs(valueE), [0, range], [0, 1]);
    console.log(max_s)
    //GREEN
    if(valueE < wtene){  
        r    = convertRange(Math.abs(valueE), [Math.abs(min), Math.abs(wtene)], [102, 255]);
        g    = convertRange(Math.abs(valueE), [Math.abs(min), Math.abs(wtene)], [210, 255]);
        b    = convertRange(Math.abs(valueE), [Math.abs(min), Math.abs(wtene)], [82, 255]);
    } else if(Math.round(valueE) == 0){
        r = center[0]
        g = center[1]
        b = center[2]
    //RED
    } else if (valueE > wtene){
        r    = 255;
        g    = convertRange(Math.abs(valueE), [Math.abs(max), Math.abs(wtene)], [110, 255]);
        b    = convertRange(Math.abs(valueE), [Math.abs(max), Math.abs(wtene)], [110, 255]);
    }
    //alpha = Math.round(perc*100)
    return 'rgba('+r+','+g+','+b+','+alpha+')';
}

//Plot Standard Deviation Gradients
function perc2colorC(std) {
    //Red, Gree, Blue
    var left = [255,214,110]
    var center = [255,255,255]
    percG = convertRange( std, [0,5], [ 255, 214]);
    percB = convertRange( std, [0,5], [ 255, 110]);
    
    r = center[0]
    g = percG
    b = percB

    alpha = Math.round(100)
    return 'rgba('+r+','+g+','+b+','+alpha+')';
} 

function convertRange( value, r1, r2 ) { 
    return ( value - r1[ 0 ] ) * ( r2[ 1 ] - r2[ 0 ] ) / ( r1[ 1 ] - r1[ 0 ] ) + r2[ 0 ];
}

//Gets percentage of
function getPercent(value, min, max){
    return Math.abs((value - min) / (max - min))
}

//We ran out of freaking letters in the alphabet... some symbols have been used to represent caps, custom residues and citruline
var to1 = {
    'ACE': "[",
    'NHE': "]",
    'GLY': "G",
    'ALA': "A",
    'VAL': "V",
    'LEU': "L",
    'ILE': "I",
    'PRO': "P",
    'PHE': "F",
    'MET': "M",
    'TRP': "W",
    'ASP': "D",
    'GLU': "E",
    'LYS': "K",
    'ARG': "R",
    'THR': "T",
    'HIS': "H",
    'SER': "S",
    'GLN': "Q",
    'ASN': "N",
    'TYR': "Y",
    'CYS': "C",
    'CY1': "C",
    'CY1': "C",
    'CY3': "C",
    'CY4': "C",
    'CYX': "C",
    'HIE': "H",
    'HID': "H",
    'HD2': "H",
    'HD1': "H",
    'HSD': "H",
    'HSE': "S",
    'HCY': "C",
    'DA': 'A',
    'DT': 'T',
    'DG': 'G',
    'DC': 'C',
    'DA5': 'A',
    'DT5': 'T',
    'DG5': 'G',
    'DC5': 'C',
    'DA3': 'A',
    'DT3': 'T',
    'DG3': 'G',
    'DC3': 'C',
    //Non Naturals Trial
    'LEN': '⅃',
    '2NP': 'ℵ',
    'PRC': 'ϸ',
    'CIT': '⅌',
    '55C': "X",
    'S55': "X",
    'R86': "Z",
}



var standard_residues = ['A', 'V', 'L', 'I', 'P','M','F','W','G','D','E','K','R','H','T','S','Q','C','Y','N']

var weblogo_res = ["A","B","C","D","E","F","G","H","I","K","L","M","N","P","Q","R","S","T","V","W","X","Y","Z"]

var aliphatic = ['A', 'V', 'L', 'I', 'P', 'M']
var charged = ['D','E','K','R','H']
var polar = ['T','S','Q','C','Y','N']
var aromatic = ['H', 'W', 'F', 'Y']



//Residue map Dictionary.. simply add more to modify selectors in step 4 of wizzard
const residuetypes = [{
    aliphatic: aliphatic,
    charged: charged,
    polar: polar,
    aromatic: aromatic
}]

//A quickie to calculate means faster
const average = array => array.reduce((a, b) => a + b) / array.length;

//20 color list for mutants
var default_colors = [
'#3cb44b', //green
'#ffe119', //yellow
'#4363d8', //blue
'#f58231', //orange
'#911eb4', //Purple
'#42d4f4', //Cyan
'#f032e6', //magenta
'#bfef45', //Lime
'#808000', //Olive
'#dcbeff', //Lavender
]

//Atom types
polar = ['N', 'O', 'S'] // Charged..
hydrophobic = ['C', 'CH', 'HA', 'HB','HD'] //Carbons + CarbonHydrogens.. (Remove HG, HE)
backbone = ['CA','O',"P", "OP1", "OP2", "O5'", "C5'", "C4'", "O4'", "C3'", "O3'", "C2'", "C1'"] //DNA and Protein Backbone Atoms

sideChainAtoms = [
    // Standard protein side chain atoms
    "CB", "CG", "CG1", "CG2", "CD", "CD1", "CD2", "CE", "CE1", "CE2", "CE3", 
    "CZ", "CZ1", "CZ2", "CZ3", "CH2", "ND1", "ND2", "NE", "NE1", "NE2", 
    "NH1", "NH2", "NZ", "OG", "OG1", "OH", "SD", "SG",

    // Hydrogen atoms associated with carbons
    "HB", "HB1", "HB2", "HG", "HG1", "HG2", "HD", "HD1", "HD2",
    "HE", "HE1", "HE2", "HE3", "HZ", "HZ1", "HZ2", "HZ3",
    "HH2", "HH11", "HH12", "HH21", "HH22",

    // Hydrogens associated with nitrogen in side chains
    "HD1", "HD2", "HE1", "HE2", "HE3", "HH1", "HH2", "HZ1", "HZ2", "HZ3",

    // DNA/RNA base atoms (side chain atoms of nucleotides)
    "N1", "N2", "N3", "N4", "N6", "N7", "N9", "C2", "C4", "C5", "C6", "C8", "O2", "O4", "O6",

    // Hydrogen atoms for DNA/RNA bases
    "H2", "H21", "H22", "H3", "H41", "H42", "H5", "H61", "H62", "H8"
];