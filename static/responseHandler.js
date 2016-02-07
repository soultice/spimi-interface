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
    $(".freq_table").hide()
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
    var max_chars = calculate_max_td()
    var cont = document.getElementById("container");
    var tb1 = document.createElement("table");
    var prevtable = document.getElementsByClassName("freq_table")[0]
    tb1.setAttribute("class", "freq_table")
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
        td3.innerHTML = format_string(max_chars, list[i]['word'], list[i]['sent'][0])
        td4.innerHTML = (list[i]['sent'][1])
        td5.innerHTML = format_string(max_chars, list[i]['word'], list[i]['sent'][2])
        //for (var i = 1; i <= 5; i++){
        //    var child = document.getElementById("td" + i)
        //    tr.appendChild(child)}
        tr.appendChild(td1);
        tr.appendChild(td2);
        tr.appendChild(td3);
        tr.appendChild(td4);
        tr.appendChild(td4);
        tr.appendChild(td5);
        tb1.appendChild(tr);
        }
    if (prevtable != null){
        prevtable.parentNode.removeChild(prevtable);
        shorten_string(max_chars, 'the','testing the sentence length if i change the sentence here and there and the meaning and so on')
       }
    cont.appendChild(tb1)
    }

  function format_string(maxlen, mkword, string) {
    // highlighting the words that are in the word column in their example
    // sentences, as well as checking if the string is too long and needs to be 
    // shortened so that there will be no 'swallowing' of the important words
    // caused by the text-overflow: hidden css property
    if (string != undefined ){
      if (string.length > maxlen && document.getElementById("cooc").checked){
        var string = shorten_string(maxlen, mkword, string);
      }
      var strarray = string.split(" ");
      for (var i = 0; i < strarray.length; i++){
        if (strarray[i] === mkword){
          strarray[i] = '<span class=\"wmatch\">' + strarray[i] + '</span>';
          }
          //console.log('length', strarray.join(" ").length)
      }
    return strarray.join(" ")
    }
  }

  function shorten_string(maxlen, mkword, string){
    // replacing words in our sentence with '.' while the sentence is longer 
    // than maxlen and the word is not equal to our marked word
    var strbuf = string
    var strarray = string.split(" ");
    for (var i = 0; i < strarray.length; i++){
      if (strarray.join(" ").length > maxlen && strarray[i] != mkword){
        //console.log("length: ",strarray.join(" ").length, maxlen, strarray[i], mkword);
        if (strarray[i-1] !== "."){
        strarray[i] = "."}
        else if (strarray[i-1] === "."){
        strarray.splice(i,i);}
      }
      string = (strarray.join(" "));
    }
    console.log("for word: ", mkword ,"\nshortened: ", strbuf, "\nto:", strarray.join(" "))
    return string
  }

  function join_points(strarray){
    // concatenate multiple points in a string to a single point
  var concstring = new String();
  for (var i = 0; i < strarray.length; i++){
    if (strarray[i] === "." && strarray[i-1] !=="."){
      concstring = concstring.concat(" " + strarray[i])
      }
    else if (strarray[i] != "."){
      concstring = concstring.concat(" " + strarray[i])
      }
    }
    return concstring
  }

  function calculate_max_td(){
    //Smooth way to calculate maximum fitting characters for a table cell
    //getting width of fixed width font letter, as well as width of table cell
    // => maximum chars = width of table cell / width of char
    var cont = document.getElementById("container");
    var str = document.createElement("str");
    str.innerHTML = "A";
    str.setAttribute("id", "str");
    cont.appendChild(str);
    strid = document.getElementById("str");
    console.log("client width:", cont.clientWidth * 0.39);
    console.log("charwidth",str.offsetWidth);
    var maxchars = Math.floor(cont.clientWidth * 0.39 / str.offsetWidth);
    console.log("maxchars:", maxchars);
    return maxchars
  }

}

)();
