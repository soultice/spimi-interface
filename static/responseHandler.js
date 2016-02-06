(function() {
  // This is responsible for the http.get methods
    // it checks the current buttons pressed and starts the http.get 
    // to the correct address
  document.getElementById("Submit").onclick = function(event) { 
    event.preventDefault();
      var q = document.getElementById("Search").value;
      if (document.getElementById('cblower').checked){
        var cblower = 'True'}
      if (document.getElementById('cbstrip').checked){
        var cbstrip = 'True'}

      if (document.getElementById('after').checked) {
          makeRequest('/spimi/api/get_freq_after?q=' + q + '&strip=' + cbstrip
                      + '&lower=' + cblower)
          }
      if (document.getElementById('prev').checked) {
          makeRequest('/spimi/api/get_freq_prev?q=' + q + '&strip=' + cbstrip
                     + '&lower=' + cblower)
          }
      if (document.getElementById('cooc').checked) {
          makeRequest('/spimi/api/get_cooc?q=' + q + '&strip=' + cbstrip
                      + '&lower=' + cblower)
          }
      return false;
  };

  function makeRequest(url) {
    // This function starts the request
    httpRequest = new XMLHttpRequest();
    $("#loading").show();
    if (!httpRequest) {
      alert('Giving up :( Cannot create an XMLHTTP instance');
      return false;
    }
    httpRequest.onreadystatechange = alertContents;
    httpRequest.open('GET', url);
    httpRequest.send();
  }

  function alertContents() {
    // Checks for the ready state and status of the respons
      // throws an error if the .get response is != 200
      // also starts the create_table function from static/js/createTable.js
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      if (httpRequest.status === 200) {
          $("#loading").hide();
          var Text = JSON.parse(httpRequest.responseText);
          if (Text[0] == undefined){
            alert('The search request did not return a result')}
          createTable(Text);}
      else {
          alert('There was a problem with the request.');
      }
    }
  }

  function createTable(list) {
      // dynamically creates the table with its contents
    var cont = document.getElementById("container");
    var tb1 = document.createElement("table");
    var prevtable = document.getElementById("freq_table")
    tb1.setAttribute("class", "freq_table")
    tb1.setAttribute("id", "freq_table")
    var thead = document.createElement("thead")
    var titles = ['freq', 'word', 'left context', 'query', 'right context'];
    for (var i = 0; i< titles.length; i++){
        thead.appendChild(document.createElement("th")).
        appendChild(document.createTextNode(titles[i]))
        }
    tb1.appendChild(thead)
    for (var  i = 0; i < list.length; i++){
        var tr = document.createElement('tr');
        var td1 = document.createElement('td');
        td1.setAttribute("class", "td1")
        var td2 = document.createElement('td');
        td2.setAttribute("class", "td2")
        var td3 = document.createElement('td');
        td3.setAttribute("class", "td3")
        var td4 = document.createElement('td');
        td4.setAttribute("class", "td4")
        var td5 = document.createElement('td');
        td5.setAttribute("class", "td5")
        var text1 = document.createTextNode(list[i]['freq']);
        td1.appendChild(text1);
        td2.innerHTML = (list[i]['word'])
        //console.log(list[i]['sent'][0].length, list[i]['sent'][0])
        td3.innerHTML = (list[i]['sent'][0])
        td4.innerHTML = (list[i]['sent'][1])
        td5.innerHTML = (list[i]['sent'][2])
        //for (var i = 1; i <= 5; i++){
        //    var child = document.getElementById("td" + i)
        //    tr.appendChild(child)}
        tr.appendChild(td1);
        tr.appendChild(td2);
        tr.appendChild(td3)
        tr.appendChild(td4)
        tr.appendChild(td4)
        tr.appendChild(td5)
        tb1.appendChild(tr);
        }
    if (prevtable != null){
        calculate_max_td()
        prevtable.parentNode.removeChild(prevtable)
       }
    cont.appendChild(tb1)
    }

  function format_string(string) {
    }

  function calculate_max_td(){
    var cont = document.getElementById("container");
    var str = document.createElement("str")
    var threes = document.getElementsByClassName("td3")[0]
    str.innerHTML = "A"
    str.setAttribute("id", "str")
    cont.appendChild(str)
    strid = document.getElementById("str")
    console.log("client width:", cont.clientWidth * 0.39)
    console.log("body width",document.body.clientWidth)
    console.log("charwidth",str.offsetWidth)
    console.log(threes.innerHTML.length, threes.innerHTML)
  }

}

)();
