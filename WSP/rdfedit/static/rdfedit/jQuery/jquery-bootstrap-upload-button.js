$(document).ready(function(){
 
 $('#fileselectbutton').click(function(e){
  $('#id_docfile').trigger('click');
 });
    
 $('#id_docfile').change(function(e){
  var val = $(this).val();
   
  var file = val.split(/[\\/]/);
   
  $('#filename').val(file[file.length-1]);
 });
});
