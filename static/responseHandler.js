(function() {
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
    httpRequest = new XMLHttpRequest();

    if (!httpRequest) {
      alert('Giving up :( Cannot create an XMLHTTP instance');
      return false;
    }
    httpRequest.onreadystatechange = alertContents;
    httpRequest.open('GET', url);
    httpRequest.send();
  }

  function alertContents() {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      if (httpRequest.status === 200) {
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
    console.log("creating table")
    var cont = document.getElementById("container");
    var tb1 = document.createElement("table");
    var prevtable = document.getElementById("freq_table")
    tb1.setAttribute("class", "freq_table")
    tb1.setAttribute("id", "freq_table")
    var thead = document.createElement("thead")
    var titles = ['Frequency', 'Word', 'Sentence'];
    for (var i = 0; i< titles.length; i++){
        thead.appendChild(document.createElement("th")).
        appendChild(document.createTextNode(titles[i]))
        }
    tb1.appendChild(thead)
    for (var  i = 0; i < list.length; i++){
        var tr = document.createElement('tr');
        var td1 = document.createElement('td');
        td1.setAttribute("id", "td1")
        var td2 = document.createElement('td');
        td2.setAttribute("id", "td2")
        var td3 = document.createElement('td');
        td3.setAttribute("id", "td3")
        var td4 = document.createElement('td');
        td4.setAttribute("id", "td4")
        var td5 = document.createElement('td');
        td5.setAttribute("id", "td5")
        var text1 = document.createTextNode(list[i]['freq']);
        td1.appendChild(text1);
        td2.innerHTML = (list[i]['word'])
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
        prevtable.parentNode.removeChild(prevtable)
       }
    cont.appendChild(tb1)
    }

  function format_string(string, length) {}

}

)();
