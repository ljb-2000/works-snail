		function unselectall(){
		if(document.myform.chkAll.checked){
		document.myform.chkAll.checked = document.myform.chkAll.checked&0;
		}
		}
		function CheckAll(form){
		for (var i=0;i<form.elements.length;i++){
		var e = form.elements[i];
		if (e.Name != 'chkAll'&&e.disabled==false)
		e.checked = form.chkAll.checked;
		}
		}


		
function download_template(template_name){
    $.ajax({
    	type: 'GET',
    	data: {template_name:template_name},
    	dataType:'json',
        url:"/download/",
        success:function(data){
            var iframe = document.createElement("iframe");
            iframe.src = data.template_url;
            iframe.style.display = "none";
            document.body.appendChild(iframe);
        },
        error:function(data){
            alert("模版下载出错，请与管理员联系！");
        }
    });
}



function upload(upload_name){
	$.ajax({
		type: 'GET',
		url: '/upload/',
		data: {upload_name:upload_name},
		dataType: 'json',
		success:function(data){
			$('#contentDiv').empty();
			$('#contentDiv').html(data.html);
		},
		error:function(re,status){
				  },
	});
}

       //克隆一份问卷
		function clone_project(that){  
		 
		    	var qnaname = $(that).attr("qnaname");
		        var qnaid = $(that).attr("qnaid");
		        var ret = confirm("你确定要复制'" + qnaname + "'吗？");
		        if (ret)
		        { 
		            $.post
		            (
		                '/clone_project/',
		                {qnaid:qnaid},
		                function(msg)
		                {
		                    if (msg.result == 0)
		                    {
		                        $("#contentDiv").empty();
								$("#contentDiv").html(msg.html);
		                    }else{
		                      alert(msg.result);
		                    }
		                },
		                "json"
		            )
		        }
		    
		}
		