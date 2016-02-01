(function() {
  document.getElementById("Submit").onclick = function(event) { 
    event.preventDefault();
      var q = document.getElementById("Search").value;
      if (document.getElementById('after').checked) {
          makeRequest('/spimi/api/get_freq_after?q=' + q)
          }
      if (document.getElementById('prev').checked) {
          makeRequest('/spimi/api/get_freq_prev?q=' + q)
          }
      if (document.getElementById('cooc').checked) {
          makeRequest('/spimi/api/get_cooc?q=' + q)
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
          console.log(Text[0])
          if (Text[0] == undefined){
            alert('The search request did not return a result')}
          if (document.getElementById('tree').checked) {
            var returnContent = document.getElementById('returnContent');
            if (returnContent != null) {
                parent = returnContent.parentNode;
                returnContent.innerHTML = Text;
                var Test = JSON.parse(Text);
                returnContent.innerHTML = (Object.keys(Test));
                }
            else {
            var returnContent = document.createElement("div");
            returnContent.setAttribute("id", "returnContent");
            var contentAppend = document.createTextNode(Text);
            returnContent.appendChild(contentAppend);
            var cont = document.getElementById("container");
            cont.appendChild(returnContent);
            }
        }
          if (document.getElementById('after').checked) {
            createTable(Text);
          }

          if (document.getElementById('prev').checked) {
            createTable(Text);
          }
          if (document.getElementById('cooc').checked) {
            createTable(Text);}
      }

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
        var td5 = document.createElement('td')
        var text1 = document.createTextNode(list[i]['freq']);
        td1.appendChild(text1);
        td2.innerHTML = (list[i]['word'])
        td3.innerHTML = (list[i]['sent'][0])
        td4.innerHTML = (list[i]['sent'][1])
        td5.innerHTML = (list[i]['sent'][2])
        //for (var i = 1, i <= 5, i++){
        //    tr.appendChild('td' + i)}
        tr.appendChild(td1);
        tr.appendChild(td2);
        tr.appendChild(td3)
        tr.appendChild(td4)
        tr.appendChild(td4)
        tr.appendChild(td5)
        tb1.appendChild(tr);
        }
        console.log("finished creating")
    if (prevtable != null){
        prevtable.parentNode.removeChild(prevtable)
        console.log("replacing table")
       }
    cont.appendChild(tb1)
    console.log("appended table")
    }

}

)();
