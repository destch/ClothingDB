$(document).ready(function(){
    $("#add_to_wantlist").click(function(){
        $.post("{{url_for(main.add_to_wantlist)}}",
        {
          id: "{{item.id}}",
      },
      function(data,status){
          alert("Data: " + data + "\nStatus: " + status);
      });
    });
});