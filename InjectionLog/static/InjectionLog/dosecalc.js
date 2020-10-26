function WeightUnits()
{
  var multiplier = 0.454;
  var theForm = document.forms["GS Calculator"];
  var units = theForm.elements["weight_units"];
  if(units.checked==true)
  {
    multiplier=1;
    document.getElementById("kg_units").innerHTML="kg";
  }
  else {
    multiplier = 0.454
    document.getElementById("kg_units").innerHTML="lb";
  }
  return multiplier;
}

function get_dosage()
{
  var theForm = document.forms["GS Calculator"];
  var Concentration = theForm.elements["GSBrand"].value;
  var option_select = theForm.elements["GSBrand"].options.selectedIndex;
  var brand_type = theForm.elements["GSBrand"].options[option_select].text;
  var CatWeight = theForm.elements["inputWeight"].value;
  var GSDose = theForm.elements["GSDose"].value;
  var Pill = theForm.elements["GSBrand"].options[option_select].getAttribute("data-pills");

  document.getElementById("concentration").value= Concentration;
  document.getElementById("brand_value").value= brand_type;
  var dose = CatWeight * WeightUnits() * GSDose / Concentration;
  if (Pill != "Injectable") {
  var dose = Math.ceil((2 * CatWeight * WeightUnits() * GSDose)/Concentration/2)
}



  if(isFinite(dose)){
    var calculated = Math.ceil(dose*10)/10

    document.getElementById("calculateddose").value= calculated;
    if (Pill == "Injectable") {
    document.getElementById("totaldose").innerHTML=  calculated+ " mL needed";
  } else{
    document.getElementById("totaldose").innerHTML=  calculated+ " pills needed";
  }
  } else {
    document.getElementById("totaldose").innerHTML= "Please enter values...";
  }

}

$('#GS Calculator').submit(function() {
  get_dosage();
});


function gaba_trigger()
{
  var theForm = document.forms["GS Calculator"];
  var check = theForm.elements["using_gaba"];
  if(check.checked == true)
  {
    document.getElementById("gaba_volume").style.display = "block";

  }
  else {
    document.getElementById("gaba_volume").style.display = "none";
  }

}

function symptom_trigger()
{
  var theForm = document.forms["GS Calculator"];
  var check = theForm.elements["new_symptom"];
  if(check.checked == true)
  {
    document.getElementById("symptom_info").style.display = "block";

  }
  else {
    document.getElementById("symptom_info").style.display = "none";
  }

}

// Example starter JavaScript for disabling form submissions if there are invalid fields
(function() {
  'use strict';
  window.addEventListener('load', function() {
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.getElementsByClassName('needs-validation');
    // Loop over them and prevent submission
    var validation = Array.prototype.filter.call(forms, function(form) {
      form.addEventListener('submit', function(event) {
        if (form.checkValidity() === false) {
          event.preventDefault();
          event.stopPropagation();
          document.getElementById('validation_message').style.display="block";
          var elementExists = document.getElementById("GS Calculator");
          if (typeof(elementExists) != 'undefined' && elementExists != null)
          {

            get_dosage();
          }
          document.getElementById('validation_message').innerHTML="Cannot submit. Please check all fields";
        }
        form.classList.add('was-validated');
      }, false);

      form.addEventListener('change', function(event) {
        if (form.checkValidity() === false) {
          event.preventDefault();
          event.stopPropagation();
          document.getElementById('validation_message').style.display="none"
        }
        form.classList.add('was-validated');
      }, false);
      form.addEventListener('click', function(event) {
        if (form.checkValidity() === false) {
          event.stopPropagation();

        }
        form.classList.add('was-validated');
      }, false);
    });
  }, false);
})();

$(document).on('click', '.confirm-delete', function(){
    return confirm('Are you sure you want to delete this record?');
})



function relapse_trigger()
{
  var theForm = document.forms["catinfo"];
  var check = theForm.elements["relapse"];
  if(check.checked == true)
  {
    document.getElementById("relapse_fields").style.display = "block"

  }
  else {
    document.getElementById("relapse_fields").style.display = "none"
  }

}
