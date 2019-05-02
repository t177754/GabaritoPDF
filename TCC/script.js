function newForm () {
    let toAddForm = document.getElementById('inputs');
    let input;
    for (x=1;x<=50;x++){
        toAddForm.appendChild(document.createElement("br"));
        input = document.createElement("input");
        input.type = "text";
        input.maxLength = 1;
        input.name = "question"+(x);
        console.log(input);
        console.log(toAddForm);
        toAddForm.append(x+":")
        toAddForm.appendChild(input);
    }
} 
newForm();
