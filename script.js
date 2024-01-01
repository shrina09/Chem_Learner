$(document).ready( 
    function()
    {
        //When the add element button is clicked
        $("#ElementAddbtn").click(
            function() 
            {
                $("form").submit(function(event) {
                    event.preventDefault();
                })
                
                $.post("/elementadd",
                //Passing element table values
                {
                    Enum: $("#Enum").val(),
                    Ecode: $("#Ecode").val(),
                    Ename: $("#Ename").val(),
                    Ecolour1: $("#Ecolour1").val(),
                    Ecolour2: $("#Ecolour2").val(),
                    Ecolour3: $("#Ecolour3").val(),
                    radius: $("#radius").val()
                }
                ).done(function() {
                    //If it is sucessful an alert is sent out 
                    alert("Added Sucessfully");
                })
                .fail(function () {
                    //If it is unsucessful an alert is sent out 
                    alert("Adding was Not Sucessful");
                });
            }
        );
    }
);

$(document).ready( 
    function()
    {
        //When the delete element button is clicked
        $("#ElementDeletebtn").click(
            function() 
            {
                $("form").submit(function(event) {
                    event.preventDefault();
                })
                
                $.post("/elementDelete",
                //Passing the name of the element
                {
                    Ename: $("#rmv-ele").val(),
                }
                ).done(function () {
                    //If it is sucessful an alert is sent out 
                    alert("Delete Successful");
                })
                .fail(function () {
                    //If it is unsucessful an alert is sent out 
                    alert("Delete Not Working");
                });
            }
        );

    }
);

$(document).ready( 
    function()
    {
        //When the upload button is clicked
        $("#up-file").click(
            function()
            {
                $("form").submit(function(event) {
                    event.preventDefault();
                })
                
                //Getting the molecule name and the file name
                var molName = $("#Mname").val().trim()
                var sdfFile = $("#file_sdf")[0].files[0]
                
                //Bundling up data to send it to the server
                var dataForm = new FormData()
                dataForm.append('Mname', molName);
                dataForm.append('file_sdf', sdfFile);
                
                //Telling the server where to go to grab the data from
                $.ajax({
                    url: '/SdfUpload',
                    type: 'POST',
                    data: dataForm, 
                    processData: false,
                    contentType: false,
                    success: function() {
                        //If it is sucessful an alert is sent out 
                        alert("File Upload Sucessful")
                    },
                    error: function() {
                        //If it is unsucessful an alert is sent out 
                        alert("File Upload Unsucessful");
                    },
                });

                $("#up-form").trigger("reset")
            }
        );
    }
);

$(document).ready(
    //Telling the server where to go to grab the data from
    $.ajax({
    url: '/returnMol', 
    type: 'GET',
    dataType: 'json', 
    success: function (data) {
        //If it is sucessful
        var molList = $('#disp-mol'); 
        molList.empty();
      
        var mols = data; 

        for (var i = 0; i < mols.length; i++) {
            var mol = mols[i];

            // creating a molecule bar element and a button for the name
            var molBar = $('<div class="bar-mol"></div>');
            var molButton = $('<button class="mol-name"></button>').text(mol.name);
            molBar.append(molButton);
            
            //For displaying the number of bonds and the atoms in the molecule
            var molCount = $('<div class="mol-count"></div>').hide();
            molCount.append($('<span class="mol-atom"></span>').text('Atoms: ' + mol.atom_count + ' \n'));
            molCount.append($('<span class="mol-bond"></span>').text('Bonds: ' + mol.bond_count + ' \n'));
            
            //To display the number of atoms and bonds when the button containing the name of the molecule is hovered over
            molButton.hover(function() {
            $(this).next('.mol-count').show();
            }, function() {
            $(this).next('.mol-count').hide();
            });
            
            molBar.append(molCount);
            
            //When the button containing the name is clicked the molecule displaying and rotation functionality is started
            molBar.on('click', function () {
            var molName = $(this).find('.mol-name').text();
            molProcess(molName);
            });

            molList.append(molBar);
        }
    },
    error: function(){
        alert("Select not working");
    }
})
);

function molProcess(molName) {
    //Telling the server where to go to grab the data from
    $.ajax({
      url: '/molShow', 
      type: 'POST',
      data: {'molName': molName},

      success: function (data) {
        //If it is sucessful then size the molecule to a scale and then display it
        data = data.replace('width="1000"', 'width="500"');
        data = data.replace('height="1000"', 'height="400"');
        data = data.replace('<svg ', '<svg version="1.1" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid meet" ');

        //Shows the molecules and allows for rotation functionality (the 3 rotations buttons will appear)
        $("#view-img").empty();
        $("#view-img").append(data);
        $('html, body').animate({
            scrollTop: $(document).height()
          }, 1000); 
          $('#rowbtn').show();
      },
      error: function () {
        //If it is unsucessful an alert is sent out 
        alert("The Molecule View Failed");
      }
    })
};

//Telling the server where to go to grab the data from
function RotReq(axis) {
    $.ajax({
        url: '/rotView', 
        type: 'POST',
        data: {'axis': axis},
    });
}

//Function ot take care of the rotation buttons
$(document).ready(function () {
    //For getting the sdf file content
    sdfReceive();

    var rotX = "#x-rot";
    var rotY = "#y-rot";
    var rotZ = "#z-rot";
    
    //IF the x rotation button is clicked 
    $(rotX).click(function() {
        RotReq("x");
        sdfReceive();
    });
    
    //IF the y rotation button is clicked 
    $(rotY).click(function() {
        RotReq("y");
        sdfReceive();
    });
    
    //IF the z rotation button is clicked 
    $(rotZ).click(function() {
        RotReq("z");
        sdfReceive();
    });
});

//For receiving the sdf data
function sdfReceive(){
    //Telling the server where to go to grab the data from
    $.ajax({
        url: "/recvSvg",
        type: "GET",
        dataType: "text",
        success: function(data) {
            //IF it is sucessful then display the molecule and size it
            var displayBox = $('#view-img');
            displayBox.empty();
            displayBox.empty();
            data = data.replace('width="1000"', 'width="500"');
            data = data.replace('height="1000"', 'height="400"');
            data = data.replace('<svg ', '<svg version="1.1" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid meet" ');
            displayBox.append(data);
        },
        error: function() {
           //If it is unsucessful an alert is sent out 
           alert("The Molecule View Failed")
        }
    });
}
