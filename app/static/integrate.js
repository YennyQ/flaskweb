/*editor*/
var editor = new Editor();
editor.render();

/*tags*/
$('#tokenfield').tokenfield({
	autocomplete: {
    source: ['Python','C','C++','JAVA','学习资料'],
    delay: 100
  }
});